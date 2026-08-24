# KohaGuard — Koha-Integrated Library Exit Verification

KohaGuard is an open-source, low-cost circulation-aware exit verification framework for libraries using **Koha ILS** and barcoded physical collections.

It bridges **library circulation** and **physical collection security**: a guard or staff member scans a book barcode using a phone camera, USB scanner, or manual entry, and KohaGuard checks the live Koha circulation state to return an immediate decision.

- 🟢 **AUTHORIZED EXIT** — item is currently checked out
- 🔴 **STOP / VERIFY** — item exists but is not currently checked out
- 🟠 **STAFF REVIEW** — exceptional item state
- ⚪ **UNKNOWN BARCODE** — barcode is not found in Koha

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

See `research/EXPERIMENT-PROTOCOL.md`.

## Important limitation

KohaGuard is **not a universal replacement for RFID**. RFID offers non-line-of-sight detection, multi-item reading and automated security gates. KohaGuard is intended as a low-cost complementary or transitional security layer for barcode-based Koha libraries.

## License

MIT. See `LICENSE`.

## Citation

See `CITATION.cff`.
