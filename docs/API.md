# API Reference

## GET `/api/status`
Returns current Koha connection health and counts.

Example:
```json
{"ok":true,"biblios":13819,"items":10,"checkouts":5}
```

## POST `/api/verify`
Request:
```json
{"barcode":"KGDEMO001","scan_source":"CAMERA SCAN"}
```

Possible statuses:
- `AUTHORIZED` — current checkout exists
- `STOP` — item exists but no current checkout exists
- `REVIEW` — exceptional item state requires staff review
- `UNKNOWN` — barcode not found
- `ERROR` — verification service failed

Example authorized response:
```json
{
  "status":"AUTHORIZED",
  "message":"Book is currently issued",
  "barcode":"KGDEMO001",
  "title":"Example title",
  "author":"Example author",
  "callnumber":"EX-001",
  "checkout_date":"2026-08-24 11:31:17",
  "due_date":"2026-09-07 23:59:00"
}
```

## GET `/api/analytics/summary`
Returns aggregate counts, average response time and recent scan events.

## GET `/api/analytics/export.csv`
Downloads the scan-event log as CSV.

## Security
Do not expose these APIs directly to the public Internet without authentication, trusted TLS, network controls, rate limiting and an institutional security review.
