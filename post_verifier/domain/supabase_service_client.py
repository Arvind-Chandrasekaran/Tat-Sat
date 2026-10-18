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


# asyncio.run will create a new event loop for the task / async function and will end the event loop when the only task comes to an end. 
# Here it basically makes the client creation synchronous.  
# This will happen only once in entire event loop generation.
# Note that a normal client will connect to the event loop, it means its socket will be created inside the event loop and deleted once the event loop is over. But supabase client is an httpx client so it make the socket not be event loop scoped.
# The redis client's tcp socket will become event loop scoped if a io call is made from it inside an event loop. If that event loop is closed the connection will also close 
supabase_service_client = asyncio.run(create_supabase())



