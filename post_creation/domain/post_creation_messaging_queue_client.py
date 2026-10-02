import json
import os

from dotenv import load_dotenv
load_dotenv()

from redis.asyncio import Redis
import network.request_models as request_models


class PostCreationMessagingQueueClient:
        def __init__(self, redis_url = "redis://localhost:6379/0", stream_name = "post_creation_stream"):
                self.STREAM_NAME = stream_name
                self._redis_client = Redis.from_url(redis_url, decode_responses=True)

        async def upload(self, request_body: request_models.Post_RequestBody, user_id: str):
                body_dict = request_body.model_dump(mode="json")
                redis_entry = {"user_id": user_id, "request_body": body_dict}
                return await self._redis_client.xadd(self.STREAM_NAME, {"data": json.dumps(redis_entry)})

                

        
# One time synchronous setup of a messaging queue client.
redis_url = os.environ.get("REDIS_URL")
print("redis url : ", redis_url)
post_creation_messaging_queue_client = PostCreationMessagingQueueClient(redis_url, "post_creation_stream")
