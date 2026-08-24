# Koha Integration

KohaGuard is designed to leave normal Koha circulation workflows unchanged. Checkout and return remain Koha operations; KohaGuard reads the current state to make an exit decision.

## Current-state lookup

Conceptual query:
```sql
SELECT
  i.itemnumber,
  i.barcode,
  i.itemcallnumber,
  i.notforloan,
  i.itemlost,
  i.withdrawn,
  b.title,
  b.author,
  iss.issue_id,
  iss.issuedate,
  iss.date_due
FROM items i
JOIN biblio b ON b.biblionumber=i.biblionumber
LEFT JOIN issues iss ON iss.itemnumber=i.itemnumber
WHERE i.barcode=?
LIMIT 1;
```

Decision:
```text
item absent                 -> UNKNOWN
current issue exists        -> AUTHORIZED
exceptional item state      -> REVIEW
known item, no current issue-> STOP
```

## Why `issues` matters
`issues` represents current checkouts. Historical circulation tables should not be used as proof that an item is currently authorized to leave.

## Compatibility
The reference implementation was tested with Koha 25.11. Schema/API details may change. Always validate against the target Koha version and test instance.

## Preferred production integration
Where practical, use supported Koha REST APIs and service accounts with least privilege. Direct database reads are useful for controlled institutional deployments but increase coupling to the Koha schema and must be reviewed during upgrades.

## Do not
- write checkout records directly with ad-hoc SQL
- expose Koha DB credentials in frontend JavaScript
- provide the guard with unnecessary patron personal data
- treat a database/network failure as authorization
