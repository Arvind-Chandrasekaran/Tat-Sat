import json
import os

from dotenv import load_dotenv
load_dotenv()

from redis.asyncio import Redis


class PostCreationMessagingQueueClient:
        def __init__(
                self,
                redis_url: str | None,
                stream_name: str = "post_creation_stream",
                group_name: str = "post_verifier",
                consumer_name: str | None = None,
        ):
                self.STREAM_NAME = stream_name
                self.GROUP_NAME = group_name
                self.CONSUMER_NAME = consumer_name or f"worker-{os.getpid()}"
                self._redis_client = Redis.from_url(
                        redis_url or "redis://localhost:6379/0",
                        decode_responses=True,
                )

        async def ensure_group(self) -> None:
                try:
                        await self._redis_client.xgroup_create(
                                name=self.STREAM_NAME,
                                groupname=self.GROUP_NAME,
                                id="0-0",
                                mkstream=True,
                        )
                except Exception as exc:
                        if "BUSYGROUP" not in str(exc):
                                raise

        async def read(self, count: int = 1, block_ms: int = 1000):
                await self.ensure_group()
                return await self._redis_client.xreadgroup(
                        groupname=self.GROUP_NAME,
                        consumername=self.CONSUMER_NAME,
                        streams={self.STREAM_NAME: ">"},
                        count=count,
                        block=block_ms,
                )

        async def acknowledge(self, entry_id: str) -> None:
                await self._redis_client.xack(
                        self.STREAM_NAME,
                        self.GROUP_NAME,
                        entry_id,
                )


redis_url = os.environ.get("REDIS_URL")
post_creation_messaging_queue_client = PostCreationMessagingQueueClient(
        redis_url,
        "post_creation_stream",
)
