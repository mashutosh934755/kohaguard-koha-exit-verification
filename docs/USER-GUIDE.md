# KohaGuard User Guide

## Guard workflow
1. Open the KohaGuard gate interface.
2. Confirm the top status shows Koha connected.
3. Choose **Scan Mode** for camera scanning or **Type Mode** for manual/USB input.
4. Present the barcode clearly.
5. Follow the decision:
   - Green **AUTHORIZED EXIT** — item has a current checkout.
   - Red **STOP / VERIFY** — item is known but has no current checkout.
   - Orange **STAFF REVIEW** — exceptional item state.
   - Grey **UNKNOWN BARCODE** — identifier was not found.
6. Use the automatic reset or **NEXT SCAN**.

## Important operational rule
A system/network error is not authorization. Follow your institution's manual verification procedure.

## Analytics
The dashboard shows total scans, authorized, blocked, unknown, today's scans and average backend response time. CSV export is intended for audit/research, subject to institutional data-retention policy.

## Camera tips
- Keep the barcode flat and well lit.
- Avoid glare.
- Fill a useful portion of the scan frame.
- Clean damaged labels or use Type Mode as fallback.
