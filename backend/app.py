#!/usr/bin/env python3
"""KohaGuard backend.

Sanitized reference implementation matching the architecture used by the
KohaGuard prototype. Configure with environment variables; never hard-code
production credentials.
"""

from __future__ import annotations

import csv
import io
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request, send_from_directory

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATE_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=None)

ANALYTICS_DB = os.getenv(
    "KOHAGUARD_ANALYTICS_DB", str(BASE_DIR / "data" / "kohaguard_analytics.db")
)
LIBRARY_NAME = os.getenv("LIBRARY_NAME", "Your University Library")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")


def koha_connection():
    return pymysql.connect(
        host=os.getenv("KOHA_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("KOHA_DB_PORT", "3306")),
        user=os.environ["KOHA_DB_USER"],
        password=os.environ["KOHA_DB_PASSWORD"],
        database=os.environ["KOHA_DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset="utf8mb4",
    )


def analytics_conn():
    Path(ANALYTICS_DB).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(ANALYTICS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_analytics():
    conn = analytics_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            barcode TEXT,
            title TEXT,
            author TEXT,
            callnumber TEXT,
            status TEXT NOT NULL,
            scan_source TEXT,
            response_time_ms INTEGER,
            checkout_date TEXT,
            due_date TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scan_timestamp ON scan_events(timestamp)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scan_status ON scan_events(status)"
    )
    conn.commit()
    conn.close()


def write_analytics(result: dict, scan_source: str, response_time_ms: int):
    init_analytics()
    conn = analytics_conn()
    conn.execute(
        """
        INSERT INTO scan_events (
            timestamp, barcode, title, author, callnumber, status,
            scan_source, response_time_ms, checkout_date, due_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            result.get("barcode"),
            result.get("title"),
            result.get("author"),
            result.get("callnumber"),
            result.get("status"),
            scan_source,
            response_time_ms,
            result.get("checkout_date"),
            result.get("due_date"),
        ),
    )
    conn.commit()
    conn.close()


@app.after_request
def common_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Access-Control-Allow-Origin"] = CORS_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def index():
    return render_template("index.html", library_name=LIBRARY_NAME)


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(
        STATIC_DIR, "manifest.webmanifest", mimetype="application/manifest+json"
    )


@app.route("/sw.js")
def service_worker():
    response = send_from_directory(STATIC_DIR, "sw.js", mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.route("/api/status")
def status():
    try:
        conn = koha_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM biblio")
            biblios = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) AS c FROM items")
            items = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) AS c FROM issues")
            checkouts = cur.fetchone()["c"]
        conn.close()
        return jsonify(ok=True, biblios=biblios, items=items, checkouts=checkouts)
    except Exception as exc:
        app.logger.exception("Koha status check failed")
        return jsonify(ok=False, error=str(exc)), 500


def verify_item(barcode: str) -> dict:
    """Return a conservative item-level exit decision.

    This uses Koha's current `issues` table as the authoritative current
    checkout state. Adjust exceptional-state policy to local circulation rules.
    """
    conn = koha_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    i.itemnumber,
                    i.barcode,
                    i.itemcallnumber AS callnumber,
                    i.notforloan,
                    i.itemlost,
                    i.withdrawn,
                    b.title,
                    b.author,
                    iss.issue_id,
                    iss.issuedate,
                    iss.date_due
                FROM items i
                JOIN biblio b ON b.biblionumber = i.biblionumber
                LEFT JOIN issues iss ON iss.itemnumber = i.itemnumber
                WHERE i.barcode = %s
                LIMIT 1
                """,
                (barcode,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return {
            "status": "UNKNOWN",
            "barcode": barcode,
            "message": "Barcode not found in Koha",
        }

    base = {
        "barcode": row["barcode"],
        "title": row.get("title"),
        "author": row.get("author"),
        "callnumber": row.get("callnumber"),
    }

    if row.get("issue_id"):
        return {
            **base,
            "status": "AUTHORIZED",
            "message": "Book is currently issued",
            "checkout_date": str(row.get("issuedate") or ""),
            "due_date": str(row.get("date_due") or ""),
        }

    # Example conservative exception policy. Institutions should document and
    # adapt these conditions rather than silently authorizing unusual states.
    if row.get("itemlost") or row.get("withdrawn") or row.get("notforloan"):
        return {
            **base,
            "status": "REVIEW",
            "message": "Item requires staff review before exit",
        }

    return {
        **base,
        "status": "STOP",
        "message": "Book is NOT issued",
    }


@app.route("/api/verify", methods=["POST", "OPTIONS"])
def verify():
    if request.method == "OPTIONS":
        return ("", 204)

    payload = request.get_json(silent=True) or {}
    barcode = str(payload.get("barcode", "")).strip()
    scan_source = str(payload.get("scan_source", "UNKNOWN")).strip() or "UNKNOWN"

    if not barcode:
        return jsonify(status="ERROR", message="Barcode is required"), 400

    started = time.perf_counter()
    try:
        result = verify_item(barcode)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        write_analytics(result, scan_source, elapsed_ms)
        return jsonify(result)
    except Exception as exc:
        app.logger.exception("Verification failed")
        return jsonify(status="ERROR", message="Verification service unavailable"), 500


@app.route("/api/analytics/summary")
def analytics_summary():
    init_analytics()
    conn = analytics_conn()
    try:
        def count(where="", params=()):
            q = "SELECT COUNT(*) AS c FROM scan_events"
            if where:
                q += " WHERE " + where
            return conn.execute(q, params).fetchone()["c"]

        total = count()
        authorized = count("status='AUTHORIZED'")
        blocked = count("status='STOP'")
        unknown = count("status='UNKNOWN'")
        review = count("status='REVIEW'")
        today = count("date(timestamp)=date('now','localtime')")
        avg = conn.execute(
            "SELECT ROUND(AVG(response_time_ms),1) AS v FROM scan_events WHERE response_time_ms IS NOT NULL"
        ).fetchone()["v"]
        recent = conn.execute(
            """
            SELECT id,timestamp,barcode,title,status,scan_source,response_time_ms
            FROM scan_events ORDER BY id DESC LIMIT 100
            """
        ).fetchall()
        return jsonify(
            ok=True,
            total=total,
            authorized=authorized,
            blocked=blocked,
            unknown=unknown,
            review=review,
            today=today,
            avg_response_ms=avg or 0,
            recent=[dict(r) for r in recent],
        )
    finally:
        conn.close()


@app.route("/api/analytics/export.csv")
def export_csv():
    init_analytics()
    conn = analytics_conn()
    rows = conn.execute(
        """
        SELECT timestamp,barcode,title,author,callnumber,status,scan_source,
               response_time_ms,checkout_date,due_date
        FROM scan_events ORDER BY id DESC
        """
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "timestamp",
            "barcode",
            "title",
            "author",
            "callnumber",
            "status",
            "scan_source",
            "response_time_ms",
            "checkout_date",
            "due_date",
        ]
    )
    for r in rows:
        writer.writerow(list(r))

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": 'attachment; filename="kohaguard-scan-history.csv"'},
    )


@app.route("/dashboard")
def dashboard():
    return send_from_directory(STATIC_DIR, "dashboard.html")


init_analytics()

if __name__ == "__main__":
    app.run(
        host=os.getenv("KOHAGUARD_BIND", "0.0.0.0"),
        port=int(os.getenv("KOHAGUARD_PORT", "8096")),
        debug=False,
    )
