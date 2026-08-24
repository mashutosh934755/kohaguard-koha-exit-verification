# KohaGuard — Koha-Integrated Library Exit Verification

KohaGuard is a **free and open-source, low-infrastructure circulation-aware exit verification framework** for libraries using **Koha ILS** and barcoded physical collections.

It bridges **library circulation** and **physical collection security**: a guard or staff member scans a book barcode using a phone camera, USB scanner, or manual entry, and KohaGuard checks the live Koha circulation state to return an immediate decision.

- 🟢 **AUTHORIZED EXIT** — item is currently checked out
- 🔴 **STOP / VERIFY** — item exists but is not currently checked out
- 🟠 **STAFF REVIEW** — exceptional item state
- ⚪ **UNKNOWN BARCODE** — barcode is not found in Koha

## Free and open-source adoption

KohaGuard is intended to be openly reproducible and reusable by institutions that already use **Koha** and barcode-based physical collections.

The software itself is provided under the **MIT License**, so institutions can use, study, modify, adapt, and redistribute the code without paying a proprietary software license fee, subject to the terms of the license.

KohaGuard is described as **low-infrastructure** because it is designed to reuse infrastructure that many Koha libraries already have, such as:

- an existing Koha server;
- existing item barcodes;
- an existing local network;
- an existing desktop, laptop, tablet, or smartphone; and
- optionally, a USB barcode scanner.

The framework does **not require mandatory RFID deployment** in order to perform circulation-aware exit verification. This can avoid the need to immediately retag an entire collection or purchase RFID gates, readers, and related middleware solely for this workflow.

However, **free software does not mean zero operational cost**. An institution may still incur local costs for servers, networking, devices, maintenance, staff time, security hardening, backups, certificates, support, and deployment.

A concise description for publications and institutional documentation is:

> **KohaGuard is a free and open-source, low-infrastructure framework designed for institutions already using Koha and barcode-based physical collections. It reuses existing circulation data and barcode infrastructure without requiring proprietary licensing or mandatory RFID deployment.**

## Architecture

```text
Physical Book
   ↓
Barcode / Camera / Manual Entry
   ↓
KohaGuard Frontend (HTML/CSS/JavaScript + ZXing)
   ↓
Python Flask API
   ↓
Koha MariaDB/MySQL (items + issues + biblio)
   ↓
Decision Engine
   ↓
AUTHORIZED / STOP / REVIEW / UNKNOWN
   ↓
SQLite Analytics
   ↓
Dashboard + CSV Export
```

## Technology stack

| Layer | Technology |
|---|---|
| ILS | Koha 25.11 (tested) |
| Backend | Python + Flask |
| Production WSGI | Gunicorn |
| Koha database | MariaDB/MySQL |
| DB connector | PyMySQL |
| Frontend | HTML + CSS + JavaScript |
| Camera barcode scanning | ZXing Browser |
| Analytics | SQLite |
| Reverse proxy | Apache |
| Web app | HTTPS / PWA |
| Android | Capacitor + Gradle |
| Android SDK | API 36 (tested) |
| Java | JDK 21 for current Capacitor Android build |

## Repository contents

- `backend/` — Flask API, analytics, decision logic
- `frontend/` — guard-facing interface and camera scanner
- `deployment/` — systemd, Apache, firewall and installation examples
- `koha/` — Koha integration notes, SQL and demo-data utilities
- `android/` — Android/Capacitor build instructions
- `docs/` — architecture, API, privacy, troubleshooting and reproducibility
- `research/` — research design and evaluation protocol

## Quick start

> Use a **test Koha instance first**. Never publish database passwords, patron data, SSL private keys, or production `.env` files.

```bash
git clone https://github.com/mashutosh934755/kohaguard-koha-exit-verification.git
cd kohaguard-koha-exit-verification
cp .env.example .env
# edit .env with your TEST Koha DB settings
sudo bash deployment/install.sh
```

Open:

```text
https://YOUR-HOST/kohaguard/
https://YOUR-HOST/kohaguard/dashboard
```

## Core API

```text
GET  /api/status
POST /api/verify
GET  /api/analytics/summary
GET  /api/analytics/export.csv
GET  /dashboard
```

Example verification request:

```bash
curl -X POST http://127.0.0.1:8096/api/verify \
  -H 'Content-Type: application/json' \
  -d '{"barcode":"KGDEMO001","scan_source":"CAMERA SCAN"}'
```

## Security and privacy

KohaGuard is designed to minimize unnecessary patron exposure. The guard-facing workflow only needs the item-level authorization decision and bibliographic details. Do **not** log patron names/card numbers unless your institution has a documented legal and operational need.

The repository intentionally excludes:

- production database credentials
- patron/card-number datasets
- SSL private keys
- live analytics databases
- institution-specific internal IP addresses as defaults

## Research use

Suggested research framing:

**Bridging Library Circulation and Physical Security: Design and Evaluation of a Real-Time Koha-Integrated Exit Verification Framework**

Recommended evaluation measures include classification accuracy, false-negative rate, false-positive rate, end-to-end verification time, backend response latency, camera-vs-manual performance, usability, and field deployment outcomes.

For academic writing, the recommended contribution statement is:

> **The framework is openly reproducible and can be adopted free of software licensing cost by Koha-based institutions, subject only to their local server, networking, device, maintenance, and deployment requirements.**

See `research/EXPERIMENT-PROTOCOL.md`.

## Relationship to RFID

KohaGuard is **not a universal replacement for RFID**. RFID offers non-line-of-sight detection, multi-item reading, automated security gates, inventory functionality, and other capabilities that a barcode-based workflow does not provide.

KohaGuard instead provides a **free, open-source and low-infrastructure complementary or transitional security layer** for barcode-based Koha libraries. Its purpose is to let institutions reuse their existing barcode and circulation infrastructure for point-of-exit verification without making RFID a mandatory prerequisite.

## License

MIT. See `LICENSE`.

## Citation

See `CITATION.cff`.
