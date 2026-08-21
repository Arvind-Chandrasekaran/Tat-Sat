import os


from dotenv import load_dotenv
load_dotenv()  # for local loading of env variables. Can be safely ignored for prod


class JWTManager:

    def __init__(self, jwt_token) -> None:


        supabase_project_id = os.environ["SUPABASE_PROJECT_ID"] 
        self._supabase_project_id = supabase_project_id
        self._jwks_url = f"https://{supabase_project_id}.supabase.co/auth/v1/.well-known/jwks.json"   # endpoint for public key
    
        self._jwt_token = jwt_token


    








