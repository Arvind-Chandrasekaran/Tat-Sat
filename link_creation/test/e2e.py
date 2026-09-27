import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


@pytest.fixture(scope="session")
def valid_access_token() -> str:
    """Authenticates once per test session and yields a valid JWT."""
    url: str = os.environ["SUPABASE_PROJECT_URL"]
    key: str = os.environ["SUPABASE_PUBLISHABLE_KEY"]
    client: Client = create_client(url, key)

    credentials = {
        "email": os.environ["TEST_USER_EMAIL"],
        "password": os.environ["TEST_USER_PASSWORD"],
    }
    login_response = client.auth.sign_in_with_password(credentials)

    return login_response.session.access_token


@pytest.fixture(scope="session")
def auth_headers(valid_access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {valid_access_token}"}