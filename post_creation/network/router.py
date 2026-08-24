from fastapi import APIRouter, Request, status, Depends, Header 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 

from security.jwt_manager import JWTManager

from domain.object_storage import object_storage

import network.request_parser as request_parser
import network.request_models as request_models
import network.response_models as response_models



router = APIRouter()



@router.get(
    "/post-media-urls",

    tags=["Create Signed Upload URLs for Media"],

    description="""
    Creates 4 signed upload URLs that allow an authenticated user to upload media directly to object storage.        
    The returned signed URLs should be used by the client to upload the media directly to object storage.
    """,

    response_model= response_models.PostMediaURLs,

    response_description="List of signed upload urls.",       

    status_code=status.HTTP_200_OK
   )

async def post_media_urls(http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj)):

    # AuthN & AuthZ  
    # http_authorization_header_credentials_obj = request_parser.http_authorization_header_credentials_obj.__call__(request)   #no need for this, we have the done it using depends 
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = JWTManager(jwt) # will perform authN and authZ


    # create signed upload url for return 
    user_id = jwt_manager.user_id
    signed_upload_urls = await object_storage.create_signed_url_upload(user_id)

    return {  
        "signed_upload_urls": signed_upload_urls    # responds with 200 - ok message
    }
    




@router.post("/post")
async def post( request_body : request_models.PostBodySchema,  http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj)):

    # AuthN & AuthZ  
    # http_authorization_header_credentials_obj = request_parser.http_authorization_header_credentials_obj.__call__(request)   #no need for this, we have the done it using depends 
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = JWTManager(jwt) # will perform authN and authZ

    # create signed upload url for return 
    user_id = jwt_manager.user_id

    # check the media uploads 



    




    
    
    
    








