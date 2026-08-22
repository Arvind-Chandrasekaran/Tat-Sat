from fastapi import APIRouter, Request 
from network.request_parser import RequestParser
from security.jwt_manager import JWTManager
from domain.object_storage import object_storage


router = APIRouter()

@router.get("/post/media")
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




