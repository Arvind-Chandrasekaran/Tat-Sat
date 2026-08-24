from fastapi import APIRouter, Request, status, Depends, Header 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 

from security.jwt_manager import JWTManager

from domain.object_storage import object_storage

from network.request_parser import RequestHeader
import network.response_models as response_models
import network.request_models as request_models


router = APIRouter()

security = HTTPBearer(
    bearerFormat="JWT",
    description=(
        "Enter a signed JWT. The token must include the claim: "
        "`{\"authenticated\": true}` along with standard claims (`sub`, `exp`)."
    )
)

@router.get(
    "/post-media-urls",

    tags=["Create Signed Upload URLs for Media"],

    summary="Create signed upload URLs that enable client to upload the media part of their post directly to object storage",

    description="""
    Creates signed upload URLs that allow an authenticated user to upload media directly to object storage.

    The client must provide a valid JWT access token in the `Authorization` header.
    The JWT payload must contain the following 3 claims:
        iss = f"https://{supabase_project_id}.supabase.co/auth/v1"
        aud = f"authenticated"
        sub = f"{user_id}"
        
    The returned signed URLs should be used by the client to upload the media directly to object storage.
    """,

    response_model= response_models.PostMediaURLs,

    response_description="List of signed upload urls.",       
    status_code=status.HTTP_200_OK
   )



async def post_media_urls(credentials: HTTPAuthorizationCredentials = Depends(security), x_api_key : str =     Header(
        description="Tenant-specific API key for rate-limiting and billing",
        examples=["ak_live_99a8b7c6d5e4"]
    )):

    # AuthN & AuthZ  
    jwt = credentials.credentials
    jwt_manager = JWTManager(jwt) # will perform authN and authZ


    # create signed upload url for return 
    user_id = jwt_manager.user_id
    signed_upload_urls = await object_storage.create_signed_url_upload(user_id)

    return {      # responds with 200 - ok message
        "signed_upload_urls": signed_upload_urls 
    }
    




@router.post("/post")
async def post(request : Request, body : request_models.PostBodySchema, credentials: HTTPAuthorizationCredentials = Depends(security)):

    # AuthN & AuthZ  
    jwt = credentials.credentials
    jwt_manager = JWTManager(jwt) # will perform authN and authZ


    # validate the media paths 
    

    user_id = jwt_manager.user_id
    signed_upload_urls = await object_storage.create_signed_url_upload(user_id)








