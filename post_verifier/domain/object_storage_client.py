from domain.supabase_service_client import supabase_service_client



class ObjectStorageClient:
        def __init__(self):
                self._supabase_service_client = supabase_service_client



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
                        raise ValueError(f"Missing media objects: {missing_ids}")






                





# shared instance accross route handlers - stateless 
object_storage_client = ObjectStorageClient()        



        








                

                









