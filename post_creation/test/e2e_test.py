import os
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"





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
        {},  # Missing token
    ],
    ids=["invalid_token", "missing_token"],
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



