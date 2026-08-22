from supabase import create_client, Client
import requests

import os
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
access_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImVhYmY3ZTVkLThjMTQtNDllMS1hMDMyLWNjNDU3ODc4ZTQwNCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2dzYmR3ZGh6cWh2bmt5bG1hc3NyLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIxZTE3YTRjOC1lNDAzLTRhODgtOTI2Yi1kOGZjY2JlMWQwYWYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzg3MzgxMjcyLCJpYXQiOjE3ODczNzc2NzIsImVtYWlsIjoiYXJ2aW5kLmM5NzUxQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzg3Mzc3NjcyfV0sInNlc3Npb25faWQiOiJkZWZkY2E5MC01N2JjLTQxNWUtOGUyYi1lYWNlNGE4MmE2OTkiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.DRlyoytrpuYXn7rgq0zhszxCbP5YZvrsKRbWfEfIIiOXiPe_iWtbTDFlstF9RSPBd0H7j57_wG3dHg1ZEdi55A"





# /post/media

def test_valid_token() -> None:

  response = requests.get(
    "http://127.0.0.1:8000/post/media",

    headers={
        "Authorization": f"Bearer {access_token}"
    }
  )


  assert response.status_code == 200



def test_invalid_token() -> None:
  access_token_false = "1232121"  

  response = requests.get(
    "http://127.0.0.1:8000/post/media",
    headers={
        "Authorization": f"Bearer {access_token_false}"
    }
  )



def test_missing_token() -> None:
  response = requests.get(
    "http://127.0.0.1:8000/post/media")

  assert response.status_code == 401


test_valid_token()
test_invalid_token()
test_missing_token()


print("post/media - passed")

