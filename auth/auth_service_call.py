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

file_path = Path("credentials.json")

# 1. Load existing data
data = {}
if file_path.exists() and file_path.stat().st_size > 0:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            raw = json.load(f)
            # Normalize legacy format (dict -> list) if needed
            if isinstance(raw, dict):
                for email, val in raw.items():
                    data[email] = val if isinstance(val, list) else [val]
        except json.JSONDecodeError:
            data = {}

now = datetime.now(timezone.utc)
user_email = credentials["email"]

# 2. Append new token entry to this specific user's token list
new_entry = {
    "access_token": login_response.session.access_token,
    "created_at": now.isoformat(),
}
data.setdefault(user_email, []).append(new_entry)

# 3. Filter out individual tokens older than 1 hour (3600 seconds)
cleaned_data = {}
for email, token_list in data.items():
    active_tokens = []
    for entry in token_list:
        created_at_str = entry.get("created_at")
        if not created_at_str:
            continue

        try:
            created_at = datetime.fromisoformat(created_at_str)
            if (now - created_at).total_seconds() <= 3600:
                active_tokens.append(entry)
        except ValueError:
            continue

    # Keep user key only if they have remaining valid tokens
    if active_tokens:
        cleaned_data[email] = active_tokens

# 4. Save back to credentials.json
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2)

print(f"Updated {file_path}. Active tokens for {user_email}: {len(cleaned_data.get(user_email, []))}")