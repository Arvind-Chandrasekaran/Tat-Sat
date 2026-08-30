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


@pytest.fixture
def signed_upload_payload(auth_headers: dict[str, str]) -> list[dict]:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=auth_headers, timeout=30)
    assert response.status_code == 200, response.text

    payload = response.json()
    signed_upload_urls = payload["signed_upload_urls"]
    assert isinstance(signed_upload_urls, list)
    assert len(signed_upload_urls) >= 2
    return signed_upload_urls


def upload_test_files(signed_uploads: list[dict]) -> list[str]:
    test_files = [
        (Path(__file__).parent / "test_img.jpg", "image/JPEG"),
        (Path(__file__).parent / "test_vid.mp4", "video/MP4"),
    ]

    uploaded_media_ids: list[str] = []

    for signed_upload, (file_path, content_type) in zip(signed_uploads, test_files):
        assert file_path.is_file(), f"Missing upload fixture: {file_path}"

        with file_path.open("rb") as file:
            upload_response = requests.put(
                signed_upload["signed_url"],
                data=file,
                headers={"Content-Type": content_type},
                timeout=30,
            )

        assert upload_response.status_code in (200, 201), upload_response.text
        uploaded_media_ids.append(signed_upload["media_id"])

    return uploaded_media_ids


# --- Negative Auth Tests ---


@pytest.mark.parametrize(
    "headers",
    [
        {"Authorization": "Bearer 1232121"},
        {},
    ],
    ids=["invalid_token", "missing_token"],
)
def test_unauthorized_requests(headers: dict[str, str]) -> None:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=headers, timeout=30)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "endpoint, method",
    [
        ("/post", "post"),
    ],
    ids=["create_post_requires_auth"],
)
def test_post_requires_auth(endpoint: str, method: str) -> None:
    payload = {
        "text": "This should fail without auth.",
        "media_ids": [],
        "media_types": [],
    }
    response = getattr(requests, method)(f"{BASE_URL}{endpoint}", json=payload, timeout=30)
    assert response.status_code == 401


# --- Positive & Functional Tests ---


def test_valid_token_access(auth_headers: dict[str, str]) -> None:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=auth_headers, timeout=30)
    assert response.status_code == 200


def test_media_upload_flow(auth_headers: dict[str, str]) -> None:
    response = requests.get(f"{BASE_URL}/post-media-urls", headers=auth_headers, timeout=30)
    assert response.status_code == 200

    payload = response.json()
    assert "signed_upload_urls" in payload
    signed_upload_urls = payload["signed_upload_urls"]
    assert len(signed_upload_urls) >= 2

    uploaded_media_ids = upload_test_files(signed_upload_urls[:2])
    assert len(uploaded_media_ids) == 2


def test_create_post_without_media(auth_headers: dict[str, str]) -> None:
    payload = {
        "text": "This is a valid text-only post created during E2E testing.",
        "media_ids": [],
        "media_types": [],
        "post_user_visibility": "public",
    }

    response = requests.post(f"{BASE_URL}/post", json=payload, headers=auth_headers, timeout=30)
    assert response.status_code == 200, response.text
    assert response.json().get("message") == "Post Created."




def test_create_post_with_uploaded_media(auth_headers: dict[str, str], signed_upload_payload: list[dict]) -> None:
    uploaded_media_ids = upload_test_files(signed_upload_payload[:2])

    payload = {
        "text": "This post includes uploaded media for validation.",
        "long_text": "This is a longer description that should be accepted when the media is valid.",
        "media_ids": uploaded_media_ids,
        "media_types": ["image", "video"],
        "reference_link": "https://example.com/post",
        "post_user_visibility": "public",
    }

    response = requests.post(f"{BASE_URL}/post", json=payload, headers=auth_headers, timeout=30)
    assert response.status_code == 200, response.text
    assert response.json().get("message") == "Post Created."




def test_post_rejects_invalid_media_ids(auth_headers: dict[str, str]) -> None:
    payload = {
        "text": "This should fail because the uploaded media does not exist.",
        "media_ids": ["invalid-media-id-12345", "invalid-media-id-67890"],
        "media_types": ["image", "video"],
    }

    response = requests.post(f"{BASE_URL}/post", json=payload, headers=auth_headers, timeout=30)
    assert response.status_code == 400, response.text


def test_post_rejects_mismatched_media_lists(auth_headers: dict[str, str]) -> None:
    payload = {
        "text": "This should fail because media_id and media_type lengths differ.",
        "media_ids": ["a", "b"],
        "media_types": ["image"],
    }

    response = requests.post(f"{BASE_URL}/post", json=payload, headers=auth_headers, timeout=30)
    assert response.status_code == 422, response.text


def test_post_rejects_text_length_exceeded(auth_headers: dict[str, str]) -> None:
    very_long_text = "A" * 20000
    payload = {
        "text": very_long_text,
        "media_ids": [],
        "media_types": [],
    }

    response = requests.post(f"{BASE_URL}/post", json=payload, headers=auth_headers, timeout=30)
    assert response.status_code == 400, response.text
    assert response.json().get("detail") == "Text limit exceeded."
