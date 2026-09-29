
## Asynchronous post creation

The API publishes each validated post request to a Redis Stream and returns HTTP 202 with a `post_id`. Run Redis and launch a separate worker process with `python post_worker.py` from this directory. Set `REDIS_URL` for both API and worker (defaults to `redis://localhost:6379/0`) and provide the existing Supabase environment variables to the worker. The worker inserts the post and its media rows; failed jobs remain pending and are retried after 60 seconds. Configure Redis persistence (AOF or managed durable Redis) so queued work survives broker restarts.
