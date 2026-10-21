import asyncio

from domain.database_client import database_client
from domain.post_verifier_messaging_queue_client import post_verifier_messaging_queue_client





async def main() -> None:

    try:

        print("Worked Started : ", post_verifier_messaging_queue_client.consumer_name)

        # Consumer Group Created in the event loop as the create consumer_group is async method and it being done outside of the main eventloop will cause error for subsequent calls. Unlike supabase httpx client that is meant to handle it. 
        await post_verifier_messaging_queue_client.create_consumer_group()
        print("Consumer group check Done.")
    

        while True:

            try:
                # Current get_next_post return order:
                # (request_body_dict, user_id, message_id)
                print("\n\n1. Post requested from messaging queue client.")
                
                post = await post_verifier_consumer_group.get_next_pending_post() # immediat fetch, will return of nothing is available for now. 

                if post is None:
                    post = await post_verifier_messaging_queue_client.get_next_post()


                request_body, user_id, message_id = post
                print("2. Post received.", request_body, user_id, message_id)

            except asyncio.CancelledError:
                raise
            
            except Exception:
                # A failed fetch usually has no known message ID.
                print("Error: Redis fetch failed; message_id=unknown")
                continue

     


            try:

                await database_client.insert(
                    request_body=request_body,
                    user_id=user_id,
                    messaging_queue_name=str(post_verifier_messaging_queue_client.stream_name),
                    messaging_queue_post_id=str(message_id)

                )

                print("3. Database Insert. Done")


            except asyncio.CancelledError:
                raise

            except Exception as e:
                """
                2 reasons to why the database insertion could have failed 
                    1. Database Service unavailable 
                        In this you must continue as the post should be ack or deleted. 
                    2. Post is malformed (reasons mentioned in the readme.md first type)
                        In these cases the posts can be ack and deleted so no continue. 
                        Error types 22xx and 23xx
                """

                try:
                    code = getattr(e, "code")
                    code = code[:2]

                    if not (code == '22' or code == '23'):
                        print(f"3. Error: Post insert failed because service unavailable. message_id={message_id}")
                        continue 

                    print(f"3. Error: Post insert failed because post malformed (not post media). message_id={message_id}")

                except:
                    print(f"3. Error: Post insert failed because service unavailable. message_id={message_id}")
                    continue 



            try : 
                # Acknowledge only after the database insert succeeds.
                await post_verifier_messaging_queue_client.ack_del_post(message_id)
                print("4. ack and delete for messaging queue done.")
                # if it fails then the same post be appended again, so to solve this make database insertion idempotent (by adding unique messaging queue column and that must be tested in verifier) or have a local storage for un ack message queue ids.
                
            except Exception as e:
                print("Error: redis ack and delete failed.")
                continue 
                # these posts not be re inserted


    
    except Exception as e:
        print(e)
        await post_verifier_messaging_queue_client.close_client()
        print("messaging queue client closed.")
        print("worker ends")


    finally:
        await post_verifier_messaging_queue_client.close_client()
        print("messaging queue client closed.")
        print("worker ends")




if __name__ == "__main__":
    asyncio.run(main())
    
