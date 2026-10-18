import asyncio
import logging

from domain.database_client import database_client
from domain.post_verifier_messaging_queue_client import post_verifier_messaging_queue_client


logger = logging.getLogger(__name__)



async def main() -> None:

    try:

        # Consumer Group Created in the event loop as the create consumer_group is async method and it being done outside of the main eventloop will cause error for subsequent calls. Unlike supabase httpx client that is meant to handle it. 
        await post_verifier_messaging_queue_client.create_consumer_group()

        while True:

            try:
                # Current get_next_post return order:
                # (request_body_dict, user_id, message_id)
                post = await post_verifier_messaging_queue_client.get_next_post()

                if post is None:
                    continue

                request_body_data, user_id, message_id = post

            except asyncio.CancelledError:
                raise
            
            except Exception:
                # A failed fetch usually has no known message ID.
                print("Redis fetch failed; message_id=unknown")
                logger.exception("Failed to fetch a post from Redis")
                await asyncio.sleep(1)
                continue




            try:

                await database_client.insert(
                    request_body=request_body,
                    user_id=user_id,
                )

                # Acknowledge only after the database insert succeeds.
                await post_verifier_messaging_queue_client.ack_del_post(message_id)


            except asyncio.CancelledError:
                raise

            except Exception:
                print(f"Post processing failed; message_id={message_id}")
                logger.exception(
                    "Verification, database insert, or Redis acknowledgement failed"
                )
                await asyncio.sleep(1)
                continue

    await post_verifier_messaging_queue_client.close_client()




if __name__ == "__main__":


    asyncio.run(main())
    
