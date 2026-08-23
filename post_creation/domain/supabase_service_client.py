import os
from supabase import acreate_client, AsyncClient
from dotenv import load_dotenv
import asyncio

load_dotenv()

# shared instance across modules 
url: str = os.environ.get("SUPABASE_PROJECT_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

async def create_supabase():
  supabase: AsyncClient = await acreate_client(url, key)
  return supabase


# asyncio.run will block the entire eventloop until this creations happens. We allow this one action to be synchronous. 
supabase_service_client = asyncio.run(create_supabase())



