from domain.post_verifier_messaging_queue_client import post_verifier_messaging_queue_client
import asyncio
import logging
import os
import signal
import socket
import sys
import uuid






NUM_CONCURRENT_WORKERS = int(os.getenv("CONCURRENT_WORKERS", "3"))

# Graceful shutdown event
shutdown_event = asyncio.Event()



async def process_and_persist(user_id: str, request_body: dict) -> None:
    """
    Placeholder for database insertion and business logic.
    """
    logger.info(f"Writing post to DB for user: {user_id}")
    # ------------------------------------------------------------------
    # TODO: Place your database insertion / validation logic here
    # Example:
    # await db.execute("INSERT INTO posts ...", user_id, request_body)
    # ------------------------------------------------------------------
    await asyncio.sleep(0.05)  # Simulate small DB I/O latency


async def worker_loop(
    worker_id: int, client: PostVerifierMessagingQueueClient
) -> None:
    """
    Dedicated worker task. Generates a distinct consumer_name per worker.
    """
    consumer_name = f"{socket.gethostname()}-worker-{worker_id}-{uuid.uuid4().hex[:6]}"
    logger.info(f"Worker {worker_id} started as consumer '{consumer_name}'")

    while not shutdown_event.is_set():
        try:
            # Poll for the next available post
            post = await client.get_next_post(
                consumer_name=consumer_name, block_ms=2000
            )

            if post is None:
                # Timed out waiting; check shutdown_event and loop
                continue

            message_id, user_id, request_body = post

            try:
                # 1. Process DB work
                await process_and_persist(user_id, request_body)

                # 2. XACK from consumer group & XDEL from Redis stream
                await client.complete_and_remove(message_id)
                logger.info(f"Successfully processed and purged message {message_id}")

            except Exception as proc_err:
                # Not ACKed or deleted: remains in PEL for DLQ / retry recovery
                logger.error(
                    f"Processing failed for message {message_id}: {proc_err}",
                    exc_info=True,
                )

        except asyncio.CancelledError:
            break
        except Exception as err:
            logger.error(f"Worker {worker_id} encountered an error: {err}", exc_info=True)
            await asyncio.sleep(1)

    logger.info(f"Worker {worker_id} exiting cleanly.")


async def main() -> None:
    client = await PostVerifierMessagingQueueClient.create(redis_url=REDIS_URL)

    # Attach termination signal handlers (SIGINT, SIGTERM)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_event.set)
        except NotImplementedError:
            # Handles platforms without signal handler support (e.g. Windows)
            pass

    logger.info(f"Launching {NUM_CONCURRENT_WORKERS} workers...")
    workers = [
        asyncio.create_task(worker_loop(i + 1, client))
        for i in range(NUM_CONCURRENT_WORKERS)
    ]

    try:
        await shutdown_event.wait()
    except KeyboardInterrupt:
        shutdown_event.set()

    logger.info("Shutdown initiated. Waiting for active workers to complete...")
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    await client.close()
    logger.info("Redis client closed. System shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())