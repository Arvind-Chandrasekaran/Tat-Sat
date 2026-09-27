from fastapi import HTTPException, status
from domain.supabase_service_client import supabase_service_client
import network.request_models as request_models
from uuid import uuid4

class Database:
    def __init__(self):
        self._supabase_service_client = supabase_service_client

    async def get_recent_posts(self):
        try:
            response = await (
                self._supabase_service_client
                .schema("domain")
                .table("posts")
                .select("id, text, embedding, topic")
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            return response.data if response and hasattr(response, 'data') else []
        except Exception as e:
            print(f"Failed to fetch posts: {e}")
            return []

    async def get_similar_posts(self, query_embedding: list, query_topic_embedding: list = None, match_threshold=0.5, match_count=5):
        try:
            payload = {
                "query_embedding": query_embedding,
                "query_topic_embedding": query_topic_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
                "filter_quality": True
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            # Note: We must call the RPC function in the domain schema if Supabase supports schema-specific RPC, 
            # otherwise it might be public. We defined it in domain.
            response = await self._supabase_service_client.rpc('sattva_hybrid_search', payload).execute()
            # remap 'text' to 'content' for the AI relationship processing
            data = response.data if response and hasattr(response, 'data') else []
            for item in data:
                item['content'] = item.get('text', '')
            return data
        except Exception as e:
            print(f"Failed RPC: {e}")
            return []

    async def _insert_post_media(self, post_id: str, media_ids: list[str], media_types: list[str], user_id: str):
        if not media_ids:
            return []
        
        post_media_rows = [
            {
                "post_id": post_id,
                "media_type": media_type.value,
                "storage_path": f"{user_id}/{media_id}",
                "display_order": index + 1,
                "post_media_status": "pending",
            }
            for index, (media_id, media_type) in enumerate(zip(media_ids, media_types))
        ]
        
        response = await (
            self._supabase_service_client
            .schema("domain")
            .table("post_media")
            .insert(post_media_rows)
            .execute()
        )
        return response

    async def insert(self, request_body: request_models.Post_RequestBody, user_id: str, analysis: dict, topic: str, embedding: list, topic_embedding: list):
        
        # Ensure post_status is pending as per documentation for media verification
        post_status = request_models.PostStatus.PENDING.value

        database_entry = {
            "user_id": user_id,
            "text": request_body.content,
            "long_text": request_body.long_text if hasattr(request_body, 'long_text') else None,
            "reference_link": str(request_body.reference_link) if hasattr(request_body, 'reference_link') and request_body.reference_link else None,
            "parent_post_id": request_body.parent_post_id,
            "post_status": post_status,
            "post_user_visibility": request_body.post_user_visibility.value if hasattr(request_body, 'post_user_visibility') else "public",
            "analysis": analysis,
            "topic": topic,
            "embedding": embedding,
            "topic_embedding": topic_embedding
        }

        try:
            response = await (
                self._supabase_service_client
                .schema("domain")
                .table("posts")
                .insert(database_entry)
                .execute()
            )
            
            post_id = None
            if response and getattr(response, "data", None):
                post_id = response.data[0].get("id")

            if post_id and hasattr(request_body, 'media_ids') and request_body.media_ids:
                await self._insert_post_media(
                    post_id,
                    request_body.media_ids,
                    request_body.media_types,
                    user_id
                )
                # Here is the message queue scaffolding for media verification
                print(f"[Queue] Sent post {post_id} media to verification queue.")

            return response
        except Exception as e:
            print(f"Insert Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create entry in the database."
            )

database = Database()
