<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# TatSat frontend

This is the canonical TatSat frontend. The project root is the parent
directory, [`../`](../), which also contains the FastAPI service, tests, and
the canonical database schema.

## Run locally

```bash
npm install
npm run dev
```

The frontend expects the FastAPI service from `../post_creation/` at
`http://127.0.0.1:8000`.

## Database setup

Use [`../schema_unified.sql`](../schema_unified.sql) as the only active
database schema. The archived `db/schema.sql` prototype is not supported.
