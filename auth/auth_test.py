import os
from dotenv import load_dotenv

from supabase import create_client, Client

load_dotenv()  # reads variables from a .env file and sets them in os.environ


# Create Supabase Client 
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
client : Client = create_client(url, key)



# Login Test 
login_test_user_email = os.environ.get("LOGIN_TEST_USER_EMAIL")
login_test_user_password = os.environ.get("LOGIN_TEST_USER_PASSWORD")

user = {
  'email': login_test_user_email,
  'password': login_test_user_password,
}

data = client.auth.sign_in_with_password(user)

print(data)