# Reproducing KohaGuard from Scratch

This guide summarizes the end-to-end build path used in the prototype, with institution-specific values replaced by placeholders.

## 1. Precheck Koha
```bash
koha-version || true
koha-list
sudo koha-mysql YOURINSTANCE <<'SQL'
SELECT COUNT(*) AS biblios FROM biblio;
SELECT COUNT(*) AS items FROM items;
SELECT COUNT(*) AS current_checkouts FROM issues;
SELECT COUNT(*) AS barcoded_items FROM items WHERE barcode IS NOT NULL AND barcode<>'';
SQL
```

## 2. Clone and configure
```bash
git clone https://github.com/mashutosh934755/kohaguard-koha-exit-verification.git
cd kohaguard-koha-exit-verification
cp .env.example .env
nano .env
```
Use the Koha DB credentials from your own protected Koha configuration. Never copy credentials into GitHub.

## 3. Install
```bash
sudo bash deployment/install.sh
sudo nano /opt/kohaguard/.env
sudo systemctl restart kohaguard
sudo systemctl status kohaguard
curl http://127.0.0.1:8096/api/status
```

## 4. Verify API
```bash
curl -X POST http://127.0.0.1:8096/api/verify \
  -H 'Content-Type: application/json' \
  -d '{"barcode":"A_REAL_TEST_BARCODE","scan_source":"TEST-CURL"}'
```

## 5. HTTPS reverse proxy
```bash
sudo a2enmod ssl proxy proxy_http headers
sudo cp deployment/apache-kohaguard.conf /etc/apache2/sites-available/kohaguard.conf
# edit ServerName and trusted certificate paths
sudo a2ensite kohaguard.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

## 6. Firewall
Production recommendation: allow HTTPS and SSH from approved networks; do not expose 8096 publicly.
```bash
sudo ufw allow 443/tcp
sudo ufw status
```

## 7. Camera scanner
The installer downloads the pinned ZXing Browser UMD build into `frontend/static/vendor/`. Camera access should be served through a secure context (trusted HTTPS).

## 8. Demo items (test Koha only)
Create a dedicated demo patron through Koha, then:
```bash
sudo koha-shell -c "perl /path/to/repo/koha/create-demo-data.pl --cardnumber YOUR_DEMO_CARD" YOURINSTANCE
```
The utility creates ten demo items and attempts to issue the first five. Review local circulation rules before running it.

## 9. Validate ground truth
```bash
sudo koha-mysql YOURINSTANCE <<'SQL'
SELECT i.barcode,b.title,
CASE WHEN iss.issue_id IS NULL THEN 'NOT_ISSUED' ELSE 'ISSUED' END AS status,
iss.issuedate,iss.date_due
FROM items i
JOIN biblio b ON b.biblionumber=i.biblionumber
LEFT JOIN issues iss ON iss.itemnumber=i.itemnumber
WHERE i.barcode LIKE 'KGDEMO%'
ORDER BY i.barcode;
SQL
```

## 10. Analytics
Open `/kohaguard/dashboard`. CSV is available at `/kohaguard/api/analytics/export.csv`.

## 11. Android
Follow `android/BUILD-ANDROID.md`. Use JDK 21 for the current tested Capacitor build. The production app should call a trusted HTTPS endpoint.

## 12. Research data collection
Follow `research/EXPERIMENT-PROTOCOL.md`. Demo transactions prove workflow, not theft reduction or population-level accuracy.
