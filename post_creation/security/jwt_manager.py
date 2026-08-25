from fastapi import HTTPException, status
from domain.supabase_service_client import supabase_service_client


class JWTManager:
    def __init__(self, jwt: str, claims: dict):
        self._jwt = jwt
        self._claims = claims
        self._user_id = claims.get("sub")


    # __init__ can not be async and hence we create another constructor
    @classmethod
    async def create(cls, jwt: str) -> "JWTManager":

        try:
            response = await supabase_service_client.auth.get_claims(jwt)

            claims = response.get('claims')

            if not response or "sub" not in claims:
                raise ValueError("Missing 'sub' claim")  # will jump to except

            return cls(jwt=jwt, claims=claims)

        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @property
    def jwt(self) -> str:
        return self._jwt

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def claims(self) -> dict:
        return self._claims






