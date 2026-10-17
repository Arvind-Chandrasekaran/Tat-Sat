from post_verifier_messaging_queue_client import post_verifier_messaging_queue_client
# from domain.database_client import database_client
import asyncio




class WorkerClient:

        def __init__(self, post_verifier_messaging_queue_client = None, database_client = None):
                self._post_verifier_messaging_queue_client = post_verifier_messaging_queue_client
                self._database_client = database_client

                
        def _verify(self):
                pass 

        # async function defition does not need eventloop (hence asycnio import). Running needs eventloop.
        async def run(self):

                post_verifier_messaging_queue_client = self._post_verifier_messaging_queue_client
                
                post = await post_verifier_messaging_queue_client.get_next_post()
                
                print(post)

        def test(self):
                print("hello world")



worker_client = WorkerClient(post_verifier_messaging_queue_client)
asyncio.run(worker_client.run())

