import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# shared instance across modules 
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase_client: Client = create_client(url, key)



