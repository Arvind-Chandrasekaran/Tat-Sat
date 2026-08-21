from fastapi import HTTPException, status

import jwt
from jwt import PyJWKClient


import os
from dotenv import load_dotenv
load_dotenv()  # for local loading of env variables. Can be safely ignored for prod



class JWTManager:

    def __init__(self, jwt_token : str) -> None:

        self._jwt_token : str = jwt_token

        supabase_project_id : str = os.environ["SUPABASE_PROJECT_ID"] 
        self._supabase_project_id : str = supabase_project_id
        
        self._jwks_url : str = f"https://{supabase_project_id}.supabase.co/auth/v1/.well-known/jwks.json"   # endpoint for public key
        self._jwks_client : str = PyJWKClient(self._jwks_url)

        # decryption algorithm - fixed can be seen in the metadat of jwks response
        self._algorithms : list[str]= ["ES256"]

        
        # claims needed for authN    
        self._jwt_issuer : str = f"https://{supabase_project_id}.supabase.co/auth/v1"
        self._jwt_audience : str = "authenticated"

        self._verify()
    



    def _verify(self) -> None:

        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(self._jwt_token)

            self._payload = jwt.decode(
                self._jwt_token,
                signing_key.key,
                algorithms=self._algorithms,
                issuer=self._jwt_issuer,
                audience=self._jwt_audience,
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT has expired",
            )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT",
            )


    @property
    def get_user_id(self):
        pass

    








