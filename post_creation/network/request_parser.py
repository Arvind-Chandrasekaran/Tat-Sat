from fastapi import Request, HTTPException



def get_jwt_token(request: Request) -> str:
    
    """
    Extract the JWT from the Authorization header.

    Expected format:
        Authorization: Bearer <JWT>
    """

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