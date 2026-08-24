# Security and Privacy Guidance

KohaGuard reads live circulation state, so deployment should be treated as an institutional security system rather than a casual public website.

## Minimum controls
- Use a dedicated least-privilege Koha database/API account where possible.
- Prefer read-only permissions for item/circulation verification.
- Expose the application through trusted HTTPS.
- Keep Gunicorn/internal API ports private.
- Restrict CORS to approved app/web origins in production.
- Protect analytics/dashboard endpoints with authentication if they contain operational data.
- Apply firewall and network segmentation appropriate to the institution.
- Back up configuration before upgrades.

## Secrets that must never be committed
- database passwords
- patron exports
- API secrets
- private keys
- signing keys / keystores
- production `.env`
- live SQLite analytics databases

## Data minimization
The guard normally needs an item-level decision, not patron identity. Avoid displaying or logging borrower name, email, phone, card number or other personal data unless a documented policy, legal basis and security requirement justify it.

## Logging
Recommended fields: timestamp, item barcode, bibliographic title, decision, scan source and response time. Define retention periods rather than storing event logs indefinitely.

## Failure policy
A network/database error should never silently become AUTHORIZED. Fail closed into a clear staff-review/system-error state and define a manual fallback procedure.

## Production Android
Do not bypass TLS certificate errors. Use trusted TLS, authenticated APIs, secure release signing and normal Android network-security configuration.
