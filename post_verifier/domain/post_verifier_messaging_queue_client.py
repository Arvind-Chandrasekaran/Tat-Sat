from redis.asyncio import Redis
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

import uuid 
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()



class PostVerifierMessagingQueueClient:


    def __init__(self, redis_url: str, stream_name: str = "post_creation_stream", consumer_group: str = "post_verifier_consumer_group"):


        self.stream_name = stream_name
        self.consumer_group = consumer_group
        self.consumer_name = str(uuid.uuid4().hex[:6])
        
        self._redis_client = Redis.from_url(redis_url, decode_responses=True)

        # Do not Create a consumer here do it inside the event loop where other io calls will be made to ensure that the connection created for this call does not close after the event loop
        # asyncio.run(self._create_consumer_group())
        

        
    async def _create_consumer_group(self) -> None:

        """
        Idempotently ensures the consumer group exists.

        - id="0": processes all unconsumed messages from the start of the
        stream.
        - id="$": processes only messages arriving after group creation.
        
        """
   
        start_id = "0"

        try:
            await self._redis_client.xgroup_create(
                name=self.stream_name,
                groupname=self.consumer_group,
                id=start_id,
                mkstream=True,  # Auto-creates stream if empty
            )
        



        except ResponseError as exc:

            if "BUSYGROUP" in str(exc):
                pass

            else:
                raise exc








    async def get_next_post(self, block_ms: int = 2000) :
        """
        Pulls the next unconsumed message ('>') for this consumer group.
        """
        
        entries = await self._redis_client.xreadgroup(
            groupname=self.consumer_group,
            consumername=self.consumer_name,
            streams={self.stream_name: ">"},
            count=1,
            block=block_ms,
        )

        return entries




    async def ack_del_post(self, message_id: str) -> None:
        """
        1. Acknowledges message in the consumer group (clears from PEL).
        2. Deletes message from the stream entirely (reclaims Redis memory).
        """
        pipe = self._redis_client.pipeline()
        pipe.xack(self.stream_name, self.consumer_group, message_id)
        pipe.xdel(self.stream_name, message_id)
        await pipe.execute()



    async def close_client(self) -> None:
        """
        Frees tcp socket in system for other processes to use the socket resource.
        Make sure do it before event loop closes.
        """
        await self._redis_client.aclose()








redis_url = os.environ.get("REDIS_URL")  
post_verifier_messaging_queue_client = PostVerifierMessagingQueueClient(redis_url)




