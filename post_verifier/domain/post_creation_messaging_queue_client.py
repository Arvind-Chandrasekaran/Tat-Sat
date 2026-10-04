import asyncio
import json
import os

from dotenv import load_dotenv
load_dotenv()

from redis.asyncio import Redis


class PostCreationMessagingQueueClient:
        def __init__(self, redis_url, stream_name = "post_creation_stream"):
                self.STREAM_NAME = stream_name
                self._redis_client = Redis.from_url(redis_url, decode_responses=True)

        async def upload(self, request_body, user_id: str):
                body_dict = request_body.model_dump(mode="json")
                redis_entry = {"user_id": user_id, "request_body": body_dict}
                return await self._redis_client.xadd(self.STREAM_NAME, {"data": json.dumps(redis_entry)})

        async def consume(self):
                last_id = "0-0"

                while True:
                        messages = await self._redis_client.xread(
                                {self.STREAM_NAME: last_id},
                                count=1,
                                block=1000,
                        )

                        for _, entries in messages:
                                for entry_id, fields in entries:
                                        message = json.loads(fields["data"])
                                        print(message, flush=True)
                                        await self._redis_client.xdel(self.STREAM_NAME, entry_id)
                                        last_id = entry_id


redis_url = os.environ.get("REDIS_URL")
redis_url = "redis://localhost:6379/0" if not redis_url else redis_url
post_creation_messaging_queue_client = PostCreationMessagingQueueClient(redis_url, "post_creation_stream")


if __name__ == "__main__":
        asyncio.run(post_creation_messaging_queue_client.consume())
