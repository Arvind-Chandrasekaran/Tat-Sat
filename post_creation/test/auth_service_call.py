import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

BASE_URL = "http://localhost:8000"

url: str = os.environ["SUPABASE_PROJECT_URL"]
key: str = os.environ["SUPABASE_PUBLISHABLE_KEY"]
client: Client = create_client(url, key)

credentials = {
"email": os.environ["TEST_USER_EMAIL"],
"password": os.environ["TEST_USER_PASSWORD"],
}
login_response = client.auth.sign_in_with_password(credentials)

print(login_response.session.access_token)
