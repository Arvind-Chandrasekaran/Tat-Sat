import os
from supabase import acreate_client, AsyncClient
import asyncio

from dotenv import load_dotenv
load_dotenv()


# shared instance across modules 
url: str = os.environ.get("SUPABASE_PROJECT_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

async def create_supabase():
  supabase: AsyncClient = await acreate_client(url, key)
  return supabase


# asyncio.run will create a new event loop, for the async function / coroutine and block the main thread until the coroutine comes to an end. 
# Here it basically makes the client creation synchronous.  
# This will happen only once in entire event loop generation.
# Note that a normal client will connect to the event loop, it means its socket will be  
supabase_service_client = asyncio.run(create_supabase())



