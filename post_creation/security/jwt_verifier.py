import jwt
from jwt import PyJWKClient
import os
from dotenv import load_dotenv
load_dotenv()


supabase_project_id = os.getenv('SUPABASE_PROJECT_ID')  
jwks_url = f"https://{supabase_project_id}.supabase.co/auth/v1/.well-known/jwks.json"


jwks_client = PyJWKClient(jwks_url)

def verify_token(token: str):

    try:

        # Retrieve the correct public key based on the token header
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"], # or ES256 depending on your project configuration
            issuer=f"https://{supabase_project_id}.supabase.co/auth/v1",
            options={"verify_aud": False} # Supabase tokens typically omit or use 'authenticated' role for aud
        )
        return payload

    except jwt.PyJWTError as e:

        raise ValueError(f"Token verification failed: {e}")