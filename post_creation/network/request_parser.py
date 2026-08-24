from fastapi import Request, HTTPException

class RequestHeader:

    def __init__(self, request: Request) -> None:
        self._request = request
        self._jwt = self._get_jwt()


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
    def jwt(self):
        return self._jwt




class RequestBody:

    async def __init__(self, request : Request):

        self._request = request 

        try:
            body = await request.json()

        except body.decoder.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid or empty JSON body")

        self._body_validate_parameters()


    def _body_validate_parameters(self):

        body = self._body

        


