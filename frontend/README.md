<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# TatSat frontend

This is the canonical TatSat frontend. The project root is the parent
directory, [`../`](../), which also contains the FastAPI service, tests, and
canonical database schema.

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

## Implemented surfaces

- Feed, explore, create, profile navigation, and responsive post views.
- Draft-side Gemini analysis and DQS presentation.
- Post detail discourse/graph tabs and semantic relationship UI.
- Backend health bootstrap and diagnostic log overlay.

## Current integration status

The frontend still uses a placeholder authorization header and does not yet
perform the signed-upload flow. The backend now returns `202 Accepted` after
placing a post on Redis, while the frontend still expects synchronous post
completion. These are tracked in the root TODO list and must be resolved
before the create-post flow is production-ready.

## TODO

- [ ] Use the Supabase browser session and send its access token as Bearer auth.
- [ ] Request signed media URLs, upload files, and submit media IDs.
- [ ] Handle the `202 queued` response and show queue/pending status.
- [ ] Replace placeholder feed, comments, and graph calls with API clients.
- [ ] Move runtime configuration from hardcoded endpoints to environment
      variables.
