from fastapi import APIRouter, Request 
from network.request_parser import RequestParser
from post_creation.security import jwt_manager
from security.jwt_manager import JWTManager

router = APIRouter()

@router.get("/post/media")
async def post_media(request : Request):


    # jwt token validation 
    request_parser = RequestParser(request)
    jwt_token = request_parser.get_jwt()
    jwt_manager = JWTManager(jwt_token)

    return { "message" : "JWT Verified"}
    








@router.post("/post")
async def post():

    # jwt token validation 

    # save the post to the database

    return {
        "message": "post endpoint works"
    }




