from fastapi import HTTPException, status

from post_verifier.domain.supabase_service_client import supabase_service_client

import post_creation.network.request_models as request_models

from uuid import uuid4


class DatabaseClient:
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
		├── external_link
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
		await self._validate_media(request_body.media_ids, user_id)

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

	async def _validate_media(self, media_ids: list[str], user_id: str) -> None:
		if not media_ids:
			return
		expected_paths = [f"{user_id}/{media_id}" for media_id in set(media_ids)]
		response = await (
			self._supabase_service_client
			.schema("storage")
			.table("objects")
			.select("name")
			.eq("bucket_id", "post_media")
			.in_("name", expected_paths)
			.execute()
		)
		found_paths = {row["name"] for row in (response.data or [])}
		missing = sorted(set(expected_paths) - found_paths)
		if missing:
			raise ValueError(f"Media objects do not exist: {', '.join(missing)}")

	async def set_post_status(self, post_id: str, post_status: str) -> None:
		await (
			self._supabase_service_client
			.schema("domain")
			.table("posts")
			.update({"post_status": post_status})
			.eq("id", post_id)
			.execute()
		)

	async def insert_and_activate(
		self,
		request_body: request_models.Post_RequestBody,
		user_id: str,
	) -> str:
		response = await self.insert(request_body, user_id)
		if not response or not getattr(response, "data", None):
			raise RuntimeError("Post insert returned no row")

		post_id = response.data[0]["id"]
		await self.set_post_status(post_id, request_models.PostStatus.ACTIVE.value)
		if request_body.media_ids:
			await (
				self._supabase_service_client
				.schema("domain")
				.table("post_media")
				.update({"post_media_status": "active"})
				.eq("post_id", post_id)
				.execute()
			)
		return post_id




# Shared stateless instance for route handlers.
database_client = DatabaseClient()
