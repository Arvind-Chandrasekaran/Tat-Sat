import asyncio
import json
import logging
import os

from post_creation.network.request_models import Post_RequestBody
from post_verifier.domain.database_client import database_client
from post_verifier.domain.post_creation_messaging_queue_client import (
    post_creation_messaging_queue_client,
)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("tatsat.post_verifier")


async def process_entry(entry_id: str, fields: dict[str, str]) -> None:
    payload = json.loads(fields["data"])
    user_id = payload["user_id"]
    request_body = Post_RequestBody.model_validate(payload["request_body"])
    post_id = await database_client.insert_and_activate(request_body, user_id)
    logger.info("Activated post %s from queue entry %s", post_id, entry_id)


async def run() -> None:
    queue = post_creation_messaging_queue_client
    await queue.ensure_group()
    logger.info("Verifier listening on %s", queue.STREAM_NAME)

    while True:
        messages = await queue.read()
        for _, entries in messages:
            for entry_id, fields in entries:
                try:
                    await process_entry(entry_id, fields)
                except Exception:
                    logger.exception("Failed to process queue entry %s", entry_id)
                    continue
                await queue.acknowledge(entry_id)


if __name__ == "__main__":
    asyncio.run(run())