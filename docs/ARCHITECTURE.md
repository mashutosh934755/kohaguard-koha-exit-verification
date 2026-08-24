# KohaGuard Architecture

## Request path

```text
Book barcode
  -> Browser / Android / USB scanner
  -> KohaGuard frontend
  -> POST /api/verify
  -> Flask decision layer
  -> Koha MariaDB
       items
       biblio
       issues
  -> decision
       AUTHORIZED
       STOP
       REVIEW
       UNKNOWN
  -> SQLite scan log
  -> guard result + analytics
```

## Authoritative circulation state

KohaGuard treats Koha as the source of truth. It does not duplicate checkout state in its analytics database. For a known item, a current row in `issues` indicates an active checkout. A missing current checkout results in a conservative STOP decision unless the configured exception policy returns REVIEW.

## Core Koha tables

- `items` — physical item and barcode
- `biblio` — title/author-level bibliographic data
- `issues` — current checkouts

Historical checkout data should not be substituted for current checkout status.

## Analytics isolation

SQLite stores only KohaGuard scan events. This prevents research/guard logging from modifying Koha circulation records.

## Deployment layers

```text
HTTPS client
  -> Apache :443
  -> Gunicorn :8096
  -> Flask
  -> MariaDB + SQLite
```

Production deployments should keep port 8096 private and expose only the trusted HTTPS reverse proxy.

## Android

The Android version is a Capacitor container. For an internal prototype it can bundle the frontend and call the KohaGuard API. A production Android app should use a trusted HTTPS endpoint rather than allowing cleartext HTTP or bypassing TLS validation.
