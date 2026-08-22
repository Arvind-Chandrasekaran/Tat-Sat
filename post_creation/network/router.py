from fastapi import APIRouter, Request, status 
from network.request_parser import RequestParser
from security.jwt_manager import JWTManager
from domain.object_storage import object_storage
import network.response_models as response_models



router = APIRouter()




@router.get(
    "/post/media",

    tags=["Post Media"],

    summary="Create signed upload URLs",

    description="""
    Creates signed upload URLs that allow an authenticated user to
    upload media directly to object storage.

    The client must provide a valid JWT access token in the
    `Authorization` header.

    The returned signed URLs should be used by the client to upload
    the media directly to object storage.
    """,

    response_model= response_models.PostMedia,

    response_description="List of signed upload urls.",       
    status_code=status.HTTP_200_OK
   )

async def post_media(request : Request):


    # AuthN & AuthZ  
    request_parser = RequestParser(request)
    jwt_token = request_parser.get_jwt
    jwt_manager = JWTManager(jwt_token) # will perform authN and authZ


    # create signed upload url for return 
    user_id = jwt_manager.user_id
    signed_upload_urls = object_storage.create_signed_url_upload(user_id)


    # responds with 200 - ok message
    return {
        "signed_upload_urls": signed_upload_urls
    }
    


@router.post("/post")
async def post(request : Request):

    # jwt token validation 

    # save the post to the database

    return {
        "message": "post endpoint works"
    }




