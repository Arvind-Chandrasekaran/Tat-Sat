from fastapi import HTTPException, status

from domain.supabase_service_client import supabase_service_client

import network.request_models as request_models

from uuid import uuid4


class Database:
	def __init__(self):
		self._supabase_service_client = supabase_service_client

	def _post_database_entry_formatter(self, request_body: request_models.Post_RequestBody, user_id: str):
		"""
		database entry format

		├── id - pk
		├── user_id - fk domain.users.id
		├── text
		├── long_text
		├── media_ids (we ignore this)
		├── media_types (we ignore this)
		├── reference_link
		├── parent_id - fk application.posts.id
		├── created_at
		├── post_status - active, deleted, pending, rejected
		└── post_user_visibility - public, private
		"""

		post_id = str(uuid4())
		post_status = request_models.PostStatus.PENDING.value

		database_entry = {
			"user_id": user_id,
			"text": request_body.text,
			"long_text": request_body.long_text,
			"reference_link": str(request_body.reference_link) if request_body.reference_link else None,
			"parent_post_id": request_body.parent_post_id,
			"post_status": post_status,
			"post_user_visibility": request_body.post_user_visibility.value,
		}

		return database_entry



	async def _insert_post(self, database_entry):

		try:
			response = await (
				self._supabase_service_client
				.schema("domain")
				.table("posts")
				.insert(database_entry)
				.execute()
			)
			return response
		
		except Exception as e:
			# Log the exact error details from PostgREST / Supabase
			print(f"PostgREST Error Details: {e}")

			error_payload = e 
			message = str(error_payload.message).lower()			
			
			if "posts_text_length_check" in message :
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="Text limit exceeded."
				)

			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Failed to create enrty in the database."
			)




	async def _insert_post_media(self, post_id: str, media_ids: list[str], media_types: list[str], user_id: str):
		if not media_ids:
			return []

		post_media_rows = [
			{
				"post_id": post_id,
				"media_type": media_type.value,
				"storage_path": f"{user_id}/{media_id}",
				"display_order": index+1,
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


	async def insert(self, request_body: request_models.Post_RequestBody, user_id: str):

		post_database_entry = self._post_database_entry_formatter(request_body, user_id)
		response = await self._insert_post(post_database_entry)

		post_id = None
		if response and getattr(response, "data", None):
			post_id = response.data[0].get("id")

		if post_id is not None and request_body.media_ids:
			await self._insert_post_media(
				post_id,
				request_body.media_ids,
				request_body.media_types,
				user_id,
			)

		return response 




# Shared stateless instance for route handlers.
database = Database()
