import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url: str = os.environ["SUPABASE_PROJECT_URL"]
key: str = os.environ["SUPABASE_PUBLISHABLE_KEY"]
client: Client = create_client(url, key)

credentials = {
    "email": os.environ["TEST_USER_EMAIL"],
    "password": os.environ["TEST_USER_PASSWORD"],
}
login_response = client.auth.sign_in_with_password(credentials)

print(login_response.session.access_token)

file_path = Path("credentials.json")

# Load existing data
data = {}
if file_path.exists() and file_path.stat().st_size > 0:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

now = datetime.now(timezone.utc)

# 1. Add the new token with the current UTC ISO timestamp
user_email = credentials["email"]
data[user_email] = {
    "access_token": login_response.session.access_token,
    "created_at": now.isoformat(),
}

# 2. Filter out any entries older than 1 hour (3600 seconds)
valid_data = {}
for email, entry in data.items():
    created_at_str = entry.get("created_at")
    if not created_at_str:
        continue

    created_at = datetime.fromisoformat(created_at_str)
    age_seconds = (now - created_at).total_seconds()

    if age_seconds <= 3600:
        valid_data[email] = entry

# 3. Write back cleaned data
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(valid_data, f, indent=2)

print(f"Saved token for {user_email} and pruned expired tokens in {file_path}")