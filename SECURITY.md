# Security Policy

Please do not open public issues containing passwords, patron data, private IP/network diagrams, API secrets, database dumps, signing keys, SSL private keys, or other sensitive institutional information.

For deployments:
- use least-privilege database/API access;
- prefer trusted HTTPS;
- restrict direct access to internal Gunicorn/API ports;
- protect analytics/admin endpoints;
- review logs and retention;
- keep dependencies updated;
- test Koha upgrades before production use.

KohaGuard is reference/research software and must be reviewed under local institutional security policies before production deployment.
