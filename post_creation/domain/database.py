from fastapi import HTTPException, status

from domain.supabase_service_client import supabase_service_client

import network.request_models as request_models

from uuid import uuid4


class Database:
	def __init__(self):
		self._supabase_service_client = supabase_service_client

	def _database_entry_formatter(self, request_body: request_models.Post_RequestBody, user_id: str):
		"""
		database entry format

		├── id - pk
		├── user_id - fk domain.users.id
		├── text
		├── long_text
		├── media_ids
		├── reference_link
		├── parent_post_id - fk application.posts.id
		├── created_at
		├── post_status - active, deleted, pending, rejected
		└── post_user_visibility - public, private
		"""

		post_id = str(uuid4())
		post_status = request_models.PostStatus.PENDING.value

		database_entry = {
			"id": post_id,
			"user_id": user_id,
			"text": request_body.text,
			"long_text": request_body.long_text,
			"media_ids": request_body.media_ids,
			"reference_link": str(request_body.reference_link) if request_body.reference_link else None,
			"parent_post_id": request_body.parent_post_id,
			"post_status": post_status,
			"post_user_visibility": request_body.post_user_visibility.value,
		}

		return database_entry


	async def insert(self, request_body: request_models.Post_RequestBody, user_id: str):

		database_entry = self._database_entry_formatter(request_body, user_id)

		response = await self._insert(database_entry)

		return response 




	async def _insert(self, database_entry):

		try:
			response = await (
				self._supabase_service_client
				.table("posts")
				.insert(database_entry)
				.execute()
			)
			return response
		
		except:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Failed to create enrty in the database."
			)


# Shared stateless instance for route handlers.
database = Database()
