# Troubleshooting

## Browser cannot reach port 8096
Check service and firewall:
```bash
sudo systemctl status kohaguard
sudo ss -lntp | grep ':8096'
curl http://127.0.0.1:8096/api/status
sudo ufw status
```
For production, prefer HTTPS via Apache rather than exposing 8096.

## Camera does not open
Browser camera APIs require a secure context in normal web deployments. Use trusted HTTPS. If native `BarcodeDetector` is unavailable, KohaGuard uses ZXing Browser.

## `SYSTEM ERROR: KohaGuard API unavailable`
Check browser developer console, CORS, API URL and backend:
```bash
curl -X POST http://127.0.0.1:8096/api/verify \
  -H 'Content-Type: application/json' \
  -d '{"barcode":"YOUR_BARCODE","scan_source":"TEST"}'
```

## Koha shows biblios but zero items
A bibliographic record is not a physical item. Create/import actual item records with barcodes through normal Koha workflows before testing exit verification.

## Barcode is always UNKNOWN
Verify the physical item exists:
```sql
SELECT itemnumber,barcode,biblionumber FROM items WHERE barcode='YOUR_BARCODE';
```

## Item is issued but KohaGuard says STOP
Confirm there is a current checkout:
```sql
SELECT i.barcode,iss.issue_id,iss.issuedate,iss.date_due
FROM items i
LEFT JOIN issues iss ON iss.itemnumber=i.itemnumber
WHERE i.barcode='YOUR_BARCODE';
```

## Android build: SDK directory not writable
Make the SDK writable by the build user or install it in that user's home directory. Do not run the whole build as root merely to bypass permissions.

## Android build: `invalid source release: 21`
Current Capacitor Android releases may require JDK 21. Verify:
```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
java -version
javac -version
./gradlew --version
```

## Android black screen
Do not rely on an iframe loading a self-signed HTTPS site. For a prototype, bundle the frontend locally and configure a reachable API endpoint. For production, use a trusted TLS endpoint and normal Android network security practices.
