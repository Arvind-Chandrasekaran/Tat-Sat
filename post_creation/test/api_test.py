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





# /post/media

def test_invalid_token() -> None:
  access_token_false = "1232121"  

  response = requests.get(

    "http://127.0.0.1:8000/post-media-urls",

    headers={
        "Authorization": f"Bearer {access_token_false}"
    }
  )



def test_missing_token() -> None:
  response = requests.get(
    "http://127.0.0.1:8000/post-media-urls")

  assert response.status_code == 401




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

  post_response = requests.post(
    "http://127.0.0.1:8000/post",
    headers={
      "Authorization": f"Bearer {access_token}",
      "Content-Type": "application/json",
    },
    json={
      "text": "Upload integration test post",
      "media_1": {"file_id": uploaded_media_ids[0], "is_uploaded": True},
      "media_2": {"file_id": uploaded_media_ids[1], "is_uploaded": True},
    },
    timeout=30,
  )

  assert post_response.status_code == 200, post_response.text


    






test_invalid_token()
test_missing_token()
test_upload()

print("post/media - passed")




