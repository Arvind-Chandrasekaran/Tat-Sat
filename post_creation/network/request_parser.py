from fastapi.security import HTTPBearer



http_authorization_header_credentials_obj = HTTPBearer(
    bearerFormat="JWT",
    description=(
    """
    The client must provide a valid JWT access token in the `Authorization` header.
    The JWT payload must contain the following 3 claims:
        iss = f"https://{supabase_project_id}.supabase.co/auth/v1"
        aud = f"authenticated"
        sub = f"{user_id}"
    """
    )
)

