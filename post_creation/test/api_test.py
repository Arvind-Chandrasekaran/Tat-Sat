import os
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

EXPIRED_TOKEN = (
    "eyJhbGciOiJFUzI1NiIsImtpZCI6ImVhYmY3ZTVkLThjMTQtNDllMS1hMDMyLWNjNDU3ODc4ZTQwNCIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJodHRwczovL2dzYmR3ZGh6cWh2bmt5bG1hc3NyLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIxZTE3YTRjOC1lNDAzLTRhODgtOTI2Yi1kOGZjY2JlMWQwYWYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzg3NTg0NjM4LCJpYXQiOjE3ODc1ODEwMzgsImVtYWlsIjoiYXJ2aW5kLmM5NzUxQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzg3NTgxMDM4fV0sInNlc3Npb25faWQiOiIwZWU5ZjY1Zi1lNzRlLTRiY2QtODdiZi01Mjc1Yzk3M2Y2ZmUiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ."
    "3wm8I26gYdh57E7dow7rg17faCWXfI0OJUzjCa_NeNHJ6PZ371XCTG6rgSw-aURgd7-_z1nbI_bkux1kLAFHMw"
)


@pytest.fixture(scope="session")
def valid_access_token() -> str:
    """Authenticates once per test session and yields a valid JWT."""
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_PUBLISHABLE_KEY"]
    client: Client = create_client(url, key)

    credentials = {
        "email": os.environ["LOGIN_TEST_USER_EMAIL"],
        "password": os.environ["LOGIN_TEST_USER_PASSWORD"],
    }
    login_response = client.auth.sign_in_with_password(credentials)
    return login_response.session.access_token


@pytest.fixture(scope="session")
def auth_headers(valid_access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {valid_access_token}"}


# --- Negative Auth Tests ---


@pytest.mark.parametrize(
    "headers",
    [
        {"Authorization": "Bearer 1232121"},  # Invalid token
        {"Authorization": f"Bearer {EXPIRED_TOKEN}"},  # Expired token
        {},  # Missing token
    ],
    ids=["invalid_token", "expired_token", "missing_token"],
)
def test_unauthorized_requests(headers: dict[str, str]) -> None:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=headers)
    assert response.status_code == 401


# --- Positive & Functional Tests ---


def test_valid_token_access(auth_headers: dict[str, str]) -> None:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=auth_headers)
    assert response.status_code == 200


def test_media_upload_flow(auth_headers: dict[str, str]) -> None:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()
    assert "signed_upload_urls" in payload
    signed_upload_urls = payload["signed_upload_urls"]
    assert len(signed_upload_urls) >= 2

    test_files = [
        ("test_img.jpg", "image/JPEG"),
        ("test_vid.mp4", "video/MP4"),
    ]

    for signed_upload, (filename, content_type) in zip(signed_upload_urls, test_files):
        file_path = Path(__file__).parent / filename
        assert file_path.is_file(), f"Missing upload fixture: {file_path}"

        with file_path.open("rb") as file:
            upload_response = requests.put(
                signed_upload["signed_url"],
                data=file,
                headers={"Content-Type": content_type},
                timeout=30,
            )

        assert upload_response.status_code in (200, 201), upload_response.text



