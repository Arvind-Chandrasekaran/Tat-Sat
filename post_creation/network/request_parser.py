from fastapi.security import HTTPBearer


class RequestParser:
    """
    Contains helper functions to parse the request sent by client. 
    """

    def authorization_header(self):
        """
        The authorization header received will be same for all the routes in this end-point.
        """

        security = HTTPBearer(
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

        return security


request_parser_obj = RequestParser()