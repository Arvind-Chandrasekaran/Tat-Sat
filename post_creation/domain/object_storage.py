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


        async def _verify_media_files(self, user_id: str, media_ids: list[str] ) -> list[str]:
                """
                Checks each media file separately and concurrently.

                Returns the media IDs that do not exist.
                """

                results = await asyncio.gather(
                *(
                        self.media_exists(
                        user_id=user_id,
                        media_id=media_id,
                        )
                        for media_id in media_ids
                )
                )

                return [
                media_id
                for media_id, exists in zip(media_ids, results)
                if not exists
                ]


        async def verify_media_files(self, user_id: str, media_ids: list[str]) -> None:
                """
                Verifies all media IDs exist for the user.
                Raises HTTPException 400 if any files are missing.
                """
                missing_files = await self._verify_media_files(user_id, media_ids)
                
                if missing_files:
                        raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail={
                                "error": "MEDIA_NOT_FOUND",
                                "message": "One or more media files could not be found in storage.",
                                "missing_media_ids": missing_files,
                                }
                        )



# shared instance accross route handlers - stateless 
object_storage = ObjectStorage()        



        








                

                









