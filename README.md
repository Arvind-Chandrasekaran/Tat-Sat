# TatSat

TatSat is a quality-focused discourse network prototype.

This directory is the canonical project root. It contains:

- `frontend/` - the React/Vite client
- `post_creation/` - the FastAPI post and media submission service
- `post_verifier/` - the post verification service scaffold
- `post_creation_messaging_queue/` - Redis stream configuration notes
- `schema_unified.sql` - the canonical Supabase/Postgres domain schema
- `docs/` - product and system design documentation

## Database source of truth

Use [`schema_unified.sql`](schema_unified.sql) for database setup and
migrations. The previous standalone frontend and its prototype schema are
archived under `../archive/` and are not active implementation sources.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

Install the dependencies listed in `post_creation/requirements.txt`, configure
the required Supabase, Redis, and environment variables, and run the FastAPI
submission service from `post_creation/`. Post submissions are queued in the
`post_creation_stream` Redis stream for asynchronous verification.

The post verifier is currently scaffolded and is not yet a runnable worker;
posts require a verifier consumer before pending posts become active.
