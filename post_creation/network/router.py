from fastapi import APIRouter, Request, status, Depends, Header 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 

from security.jwt_manager import JWTManager

from domain.object_storage import object_storage

from network.request_parser import request_parser_obj
import network.request_models as request_models
import network.response_models as response_models



router = APIRouter()



@router.get(
    "/post-media-urls",

    tags=["Create Signed Upload URLs for Media"],

    summary="Create signed upload URLs that enable client to upload the media part of their post directly to object storage",

    description="""
    Creates signed upload URLs that allow an authenticated user to upload media directly to object storage.        
    The returned signed URLs should be used by the client to upload the media directly to object storage.
    """,

    response_model= response_models.PostMediaURLs,

    response_description="List of signed upload urls.",       

    status_code=status.HTTP_200_OK
   )

async def post_media_urls(http_authorization_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser_obj.authorization_header)):

    # AuthN & AuthZ  
    jwt = http_authorization_credentials_obj.credentials
    jwt_manager = JWTManager(jwt) # will perform authN and authZ


    # create signed upload url for return 
    user_id = jwt_manager.user_id
    signed_upload_urls = await object_storage.create_signed_url_upload(user_id)

    return {      
        "signed_upload_urls": signed_upload_urls    # responds with 200 - ok message
    }
    




@router.post("/post")
async def post():
    pass 








