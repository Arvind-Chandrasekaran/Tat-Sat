from domain.supabase_service_client import supabase_service_client


class Database:
	def __init__(self):
		self._supabase_service_client = supabase_service_client


	async def create_post(self, post_data):
		response = await (
			self._supabase_service_client
			.table("posts")
			.insert(post_data)
			.execute()
		)

		return response.data[0] if response.data else None


# Shared stateless instance for route handlers.
database = Database()
