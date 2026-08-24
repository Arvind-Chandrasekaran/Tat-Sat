from supabase import create_client, Client
import requests

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # reads variables from a .env file and sets them in os.environ


# Create JWT 
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_PUBLISHABLE_KEY"]
client : Client = create_client(url, key)

login_test_user_email = os.environ["LOGIN_TEST_USER_EMAIL"]
login_test_user_password = os.environ["LOGIN_TEST_USER_PASSWORD"]

user = {
  'email': login_test_user_email,
  'password': login_test_user_password,
}

login_response = client.auth.sign_in_with_password(user)
access_token = login_response.session.access_token
access_token_expired = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImVhYmY3ZTVkLThjMTQtNDllMS1hMDMyLWNjNDU3ODc4ZTQwNCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2dzYmR3ZGh6cWh2bmt5bG1hc3NyLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIxZTE3YTRjOC1lNDAzLTRhODgtOTI2Yi1kOGZjY2JlMWQwYWYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzg3NTg0NjM4LCJpYXQiOjE3ODc1ODEwMzgsImVtYWlsIjoiYXJ2aW5kLmM5NzUxQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzg3NTgxMDM4fV0sInNlc3Npb25faWQiOiIwZWU5ZjY1Zi1lNzRlLTRiY2QtODdiZi01Mjc1Yzk3M2Y2ZmUiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.3wm8I26gYdh57E7dow7rg17faCWXfI0OJUzjCa_NeNHJ6PZ371XCTG6rgSw-aURgd7-_z1nbI_bkux1kLAFHMw"




# /post/media

def test_invalid_token() -> None:
  access_token_false = "1232121"  

  response = requests.get(

    "http://127.0.0.1:8000/post-media-urls",

    headers={
        "Authorization": f"Bearer {access_token_false}"
    }
  )


  assert response.status_code == 401


def test_missing_token() -> None:
  response = requests.get(
    "http://127.0.0.1:8000/post-media-urls")

  assert response.status_code == 401



def test_expired_token() -> None:

  response = requests.get(
    "http://127.0.0.1:8000/post-media-urls",

    headers={
        "Authorization": f"Bearer {access_token_expired}"
    }
  )

  assert response.status_code == 401




def test_valid_token() -> None:

  response = requests.get(
    "http://127.0.0.1:8000/post-media-urls",

    headers={
        "Authorization": f"Bearer {access_token}"
    }
  )

  assert response.status_code == 200







def test_upload() -> None:

  response = requests.get(
    "http://127.0.0.1:8000/post-media-urls",

    headers={
        "Authorization": f"Bearer {access_token}"
    }
  )

  assert response.status_code == 200

  signed_upload_urls = response.json()["signed_upload_urls"]
  assert len(signed_upload_urls) >= 2

  test_files = [
    ("test_img.jpg", "image/JPEG"),
    ("test_vid.mp4", "video/MP4"),
  ]

  uploaded_media_ids = []

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
    uploaded_media_ids.append(signed_upload["media_id"])





test_invalid_token()
test_missing_token()
test_valid_token()
test_expired_token()
test_upload()

print("post/media - passed")




