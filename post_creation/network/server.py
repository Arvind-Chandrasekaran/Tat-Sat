import uvicorn
from fastapi import FastAPI, APIRouter, Request 

router = APIRouter()

@router.get("/post/media")
async def post_media(request : Request):

    authorization_header = request.headers.get("Authorization")
    


    # jwt token validation 
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




if __name__ == "__main__":
    app = FastAPI()
    app.include_router(router)
    uvicorn.run(app, host="127.0.0.1", port=8000)

