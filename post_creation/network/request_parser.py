from fastapi import Request, HTTPException

class RequestParser:

    def __init__(self, request: Request) -> None:
        self._request = request
        self._jwt_token = self._get_jwt()


    def _get_jwt(self) -> str:
        
        """
        Extract the JWT from the Authorization header.

        Expected format:
            Authorization: Bearer <JWT>
        """

        request = self._request

        authorization = request.headers.get("Authorization")

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization header",
            )

        scheme, separator, token = authorization.partition(" ")

        if scheme.lower() != "bearer" or not separator or not token:
            raise HTTPException(
                status_code=401,
                detail="Invalid Authorization header",
            )

        return token


    @property
    def get_jwt(self):
        return self._jwt_token



