import asyncio
import logging

from domain.database_client import database_client
from domain.post_verifier_messaging_queue_client import post_verifier_messaging_queue_client


logger = logging.getLogger(__name__)



async def main() -> None:

    try:

        # Consumer Group Created in the event loop as the create consumer_group is async method and it being done outside of the main eventloop will cause error for subsequent calls. Unlike supabase httpx client that is meant to handle it. 
        print("Consumer group check started.")
        await post_verifier_messaging_queue_client.create_consumer_group()

        
        print("Worker loop started.")
        while True:

            try:
                # Current get_next_post return order:
                # (request_body_dict, user_id, message_id)
                print("Post requested from messaging queue client.")
                post = await post_verifier_messaging_queue_client.get_next_post()

                if post is None:
                    print("Post is None")
                    continue

                request_body, user_id, message_id = post
                print("Post received.", request_body, user_id, message_id)

            except asyncio.CancelledError:
                raise
            
            except Exception:
                # A failed fetch usually has no known message ID.
                print("Redis fetch failed; message_id=unknown")
                logger.exception("Failed to fetch a post from Redis")
                continue




            try:

                await database_client.insert(
                    request_body=request_body,
                    user_id=user_id,
                )

                print("Database Insert. Done")


            except asyncio.CancelledError:
                raise

            except Exception:
                print(f"Post insert failed, could be because post is malformed or service unavailable; message_id={message_id}")
                # make sure to have malformed post check better in verifier step so that here only service unavailable ones come.
                await asyncio.sleep(1)
                continue

            # Acknowledge only after the database insert succeeds.
            await post_verifier_messaging_queue_client.ack_del_post(message_id)

            print("ack and delete for messaging queue done.")


    
    except:
        await post_verifier_messaging_queue_client.close_client()
        print("messaging queue client closed.")
        print("worker ends")


    finally:
        await post_verifier_messaging_queue_client.close_client()
        print("messaging queue client closed.")
        print("worker ends")




if __name__ == "__main__":
    asyncio.run(main())
    
