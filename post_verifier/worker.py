import asyncio
import sys

from domain.database_client import database_client
from domain.post_verifier_messaging_queue_client import post_verifier_messaging_queue_client
from domain.object_storage_client import object_storage_client


async def main() -> None:
    try:
        print("Serverless Worker Started :", post_verifier_messaging_queue_client.consumer_name)

        # Ensure consumer group exists
        await post_verifier_messaging_queue_client.create_consumer_group()
        print(f"Consumer group check done: {post_verifier_messaging_queue_client.consumer_group}")

        # 1. Attempt to fetch a pending post (autoclaim)
        post = await post_verifier_messaging_queue_client.get_next_pending_post()

        # 2. If no pending post, fetch a single new post with a short timeout (e.g., 2000ms)
        # Avoid block_ms=0 here, otherwise a serverless container will hang indefinitely and hit execution limits.
        if post is None:
            post = await post_verifier_messaging_queue_client.get_next_post(block_ms=2000)

        # If queue is empty, exit cleanly
        if post is None:
            print("Queue is empty. Exiting serverless execution.")
            return

        request_body, user_id, message_id = post
        print(f"Post received. message_id={message_id}, user_id={user_id}")

        # 3. Media presence check
        media_ids = request_body.get('media_ids', None)
        media_ids_check = True

        if media_ids:
            try:
                await object_storage_client.media_id_presence_check(media_ids, user_id)
            except Exception as e:
                print(f"Error: Media id presence check failed: {e}")
                media_ids_check = False

        # 4. Database insertion
        if media_ids_check:
            try:
                await database_client.insert(
                    request_body=request_body,
                    user_id=user_id,
                    messaging_queue_name=str(post_verifier_messaging_queue_client.stream_name),
                    messaging_queue_post_id=str(message_id)
                )
                print(f"Database Inserted. message_id={message_id}")

            except asyncio.CancelledError:
                raise

            except Exception as e:
                code = getattr(e, "code", "")
                code = str(code)[:2]

                if not (code == '22' or code == '23'):
                    print(f"Error: Post insert failed (service unavailable). message_id={message_id}")
                    # Do not ack/del if service is down so it can be retried later via PEL
                    return 

                print(f"Error: Post insert failed (post malformed). message_id={message_id}")

        # 5. Acknowledge and delete from Redis stream
        try:
            await post_verifier_messaging_queue_client.ack_del_post(message_id)
            print(f"Ack and delete completed for message_id={message_id}")
        except Exception as e:
            print(f"Error: Redis ack and delete failed for message_id={message_id}: {e}")
            return

    except Exception as e:
        print(f"Critical Worker Error: {e}")
        raise

    finally:
        await post_verifier_messaging_queue_client.close_client()
        print("Messaging queue client closed. Worker execution ends.")


if __name__ == "__main__":
    asyncio.run(main())