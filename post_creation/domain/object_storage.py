from fastapi import HTTPException, status 

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
                storage_location = f"{user_id}/{media_id}"

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






        async def media_id_presence_check(self, media_ids, user_id):

                if not media_ids:
                        return

                # Deduplicate IDs and build exact storage paths
                unique_ids = list(set(media_ids))
                expected_paths = [f"{user_id}/{media_id}" for media_id in unique_ids]

                # Query all paths in a single roundtrip
                response = await (
                        self._supabase_service_client.schema("storage").table("objects")
                        .select("name")
                        .in_("name", expected_paths)
                        .execute()
                )

                # Supabase response data contains the list of matched rows
                found_paths = {row["name"] for row in (response.data or [])}

                # Verify all expected objects were found
                missing_paths = set(expected_paths) - found_paths
                if missing_paths:
                        missing_ids = [path.split("/", 1)[1] for path in missing_paths]
                        raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid media ID(s): {', '.join(missing_ids)}",
                        )






                





# shared instance accross route handlers - stateless 
object_storage = ObjectStorage()        



        








                

                









