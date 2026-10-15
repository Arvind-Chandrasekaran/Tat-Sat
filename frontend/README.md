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

The frontend expects the FastAPI service from [`../post_creation/`](../post_creation/)
at `http://127.0.0.1:8000`.

Configure runtime endpoints and Supabase browser credentials with Vite
variables when needed:

```bash
VITE_API_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## Database setup

Use [`../schema_unified.sql`](../schema_unified.sql) as the only active
database schema. The archived `db/schema.sql` prototype is not supported.

## Implemented surfaces

- Feed, explore, create, profile navigation, and responsive post views.
- Draft-side Gemini analysis and DQS presentation.
- Post detail discourse/graph tabs and semantic relationship UI.
- Backend health bootstrap and diagnostic log overlay.
- Supabase session Bearer authentication.
- Signed media upload and asynchronous queue submission.

## Current integration status

The frontend uses the active Supabase browser session to send Bearer tokens,
uploads selected media through the signed-upload flow, and handles the
backend's `202 Accepted` queue response. The verifier worker must still be
running for queued posts to become persisted and visible.

## TODO

- [ ] Add a user sign-in/session screen for users without an existing
      Supabase session.
- [ ] Replace placeholder comments and graph calls with API clients.
- [ ] Add post-status polling or realtime updates after queue submission.
- [ ] Move any remaining runtime configuration to environment variables.
