import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

credentials = {
    "email": os.environ["TEST_USER_EMAIL"],
    "password": os.environ["TEST_USER_PASSWORD"],
}

credentials_file = Path(__file__).with_name("credentials.json")

if credentials_file.exists():
    with credentials_file.open("r", encoding="utf-8") as file:
        saved_credentials = json.load(file)
else:
    saved_credentials = []

saved_credentials.append(credentials)

with credentials_file.open("w", encoding="utf-8") as file:
    json.dump(saved_credentials, file, indent=2)