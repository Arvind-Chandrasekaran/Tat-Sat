from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool

import jwt
from jwt import PyJWKClient


import os
from dotenv import load_dotenv
load_dotenv()  # for local loading of env variables. Can be safely ignored for prod




# shared instance across all JWTManager instances 
jwks_url : str = os.environ["SUPABASE_JWKS_URL"]   # endpoint for public key. Since it is public, it has no protection
jwks_client = PyJWKClient(jwks_url)




class JWTManager_Local:

    def __init__(self, jwt_token : str) -> None:
        
        self._jwks_client = jwks_client

        self._jwt_token = jwt_token

        supabase_project_id = os.environ["SUPABASE_PROJECT_ID"] 
        self._supabase_project_id = supabase_project_id
        
        # can be seen the metadata of public singing key
        self._algorithms : list[str]= ["ES256"]
        
        # claims needed for authN    
        self._jwt_issuer : str = f"https://{supabase_project_id}.supabase.co/auth/v1"
        self._jwt_audience : str = "authenticated"

        self._verify()
        # + saves the self._payload

        self._get_user_id()
        # save the self._user_id
    



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

        # mindful of the iat error. There is start time fo JWT, and the server time can somtimes be behind the the start of iat due to serve having improper clock
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT",
            )


    def _get_user_id(self):

        user_id = self._payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT does not contain a user ID",
            )

        self._user_id = user_id



    @property
    def user_id(self):
        return self._user_id











