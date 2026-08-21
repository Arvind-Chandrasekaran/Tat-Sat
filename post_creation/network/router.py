from fastapi import APIRouter, Request 
from request_parser import RequestParser


router = APIRouter()

@router.get("/post/media")
async def post_media(request : Request):


    # jwt token validation 
    request_parser = RequestParser(request)
    jwt_token = request_parser.get_jwt_token(request)




    # create media object urls for return 
    return {
        "message": "post_media endpoint works"
    }



@router.post("/post")
async def post():

    # jwt token validation 

    # save the post to the database

    return {
        "message": "post endpoint works"
    }




