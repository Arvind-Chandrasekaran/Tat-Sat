import uuid
from domain.supabase_service_client import supabase_service_client
import asyncio

class ObjectStorage:
        def __init__(self):
                self._supabase_service_client = supabase_service_client


        async def _create_signed_url_upload(self, user_id):
                """
                Creates one signed upload URL.

                The object path is unique, so each upload gets its own
                storage location.
                """

                ssc = self._supabase_service_client

                media_id = str(uuid.uuid4())
                storage_location = f"{media_id}/{user_id}"

                response = await (
                        ssc.storage
                        .from_("post_media")
                        .create_signed_upload_url(storage_location)
                )

                return {
                        "media_id": media_id,
                        "path": storage_location,  # storage location accoridng to the terms of supabase for client to understand
                        "signed_url": response["signedUrl"],
                        "token": response["token"],
                }


        async def create_signed_url_upload(self, user_id):
                MAX_FILES = 4

                tasks = [
                        self._create_signed_url_upload(user_id)
                        for _ in range(MAX_FILES)
                ]

                signed_urls = await asyncio.gather(*tasks)

                return signed_urls



# shared instance accross route handlers - stateless 
object_storage = ObjectStorage()        



        








                

                









