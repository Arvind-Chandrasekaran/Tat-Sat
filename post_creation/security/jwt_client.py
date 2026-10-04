from domain.supabase_service_client import supabase_service_client




# Exceptions raised by the jwt_client in different cases

class InvalidJWTError(Exception):
    """JWT is missing, malformed, expired, or otherwise invalid."""
    pass


class JWTVerifierError(Exception):
    """The JWT verification service/client failed."""
    pass



INVALID_JWT_CODES = {
    "bad_jwt",
    "token_expired",
    "invalid_jwt",
    "session_not_found",
}




# This client is stateful hence is not instantiated like domain client

class JWTClient:

    def __init__(self, jwt: str, claims: dict):
        self._jwt = jwt
        self._claims = claims
        self._user_id = claims.get("sub")


    # __init__ can not be async and hence we create another constructor

    @classmethod
    async def create(cls, jwt: str) -> "JWTClient":

        if not jwt or not jwt.strip():
            raise InvalidJWTError("JWT is missing")


        try:
            response = await supabase_service_client.auth.get_claims(jwt)
        
        except Exception as exc:

            print(exc.code)

            if exc.code in INVALID_JWT_CODES:
                raise InvalidJWTError(f"Invalid JWT: {exc}") from exc
            
            else:
                raise JWTVerifierError(f"AuthN and AuthZ Clinet Error: {exc}") from exc



        # Verification completed, but JWT is invalid
        claims = response.get("claims") if response else None

        if not claims or "sub" not in claims:
            raise InvalidJWTError(
                "Invalid JWT"
            )

        return cls(
            jwt=jwt,
            claims=claims,
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






