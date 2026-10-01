from fastapi import APIRouter, Request, status, Depends, Header, HTTPException 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 

from security.jwt_manager import JWTManager

from domain.object_storage import object_storage
from domain.supabase_service_client import supabase_service_client
from domain.post_creation_messaging_queue_client import post_creation_messaging_queue_client

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

    responses = {

        # automatically adds the 200 return but fastapi wont know the schema of the response needed manually specified
        200 : {

            "model": response_models.PostMediaURLs,
            "description": "List of signed upload urls.",       
        },

        401: {
            "description": "Invalid Authentication Credentials",
        }
    },
    
   )

async def post_media_urls(http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj_creator)):

    # AuthN & AuthZ  
    # http_authorization_header_credentials_obj = request_parser.http_authorization_header_credentials_obj_creator.__call__(request)   # request is instance of Request. but no need for this, we have the done it using depends 
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = await JWTManager.create(jwt) # will perform authN and authZ   

    # create signed upload url for return 
    user_id = jwt_manager.user_id
    signed_upload_urls = await object_storage.create_signed_url_upload(user_id)

    return {  
        "signed_upload_urls": signed_upload_urls    # responds with 200 - ok message
    }
    




@router.post(

    "/post",

    tags=["Create a Post"],

    description="""
    Creates an entry to the posts tabale based on the information provided by a user. 
    It will verify the information before creating the database entry.
    """,

    responses = {

        # automatically adds the 200 and 422 

        202: {
                "status": "queued",
                "message": "Post submitted for processing",
                "queue_id": "entry_id",
            }, 

        400: {
            "description": "Bad request.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Text limit exceeded."
                    }
                }
            }
        }


    },)
async def post( request_body : request_models.Post_RequestBody,  http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj_creator)):

    # AuthN & AuthZ  
    # http_authorization_header_credentials_obj = request_parser.http_authorization_header_credentials_obj_creator.__call__(request)   # request is instance of Request. but no need for this, we have the done it using Depends 
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = await JWTManager.create(jwt) # will perform authN and authZ   



    # Uploaded post to messaging queue
    user_id = jwt_manager.user_id

    try:
            entry_id = await post_creation_messaging_queue_client.upload(
                request_body=request_body, user_id=user_id
            )
            # HTTP 202 Accepted: standard code indicating request queued for processing
            return {
                "status": "queued",
                "message": "Post submitted for processing",
                "queue_id": entry_id,
            }

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enqueue post due to an internal error.",
        )
 








@router.get(

    "/health",

    tags=["Check health of the service"],

    description="""
    Check if the service is active. Returns 200 ok when it is. 
    """,


            )
def health():
    return {"status": "ok"}
















"""
Key Notes 

Rogue Client Security 
1 - Malicious file being uplaoded to storage using signed upload url - Proxy Storage and Check magic bytes of the files being uploaded to the storage before approving the post entry in database. 
2 - Phantom  Posts - Post not uploaded by a client could send the media_id as being uploaded - Check the media_ids sent by client. 
3 - Orphan Posts - Post could be uploaded to link but not sent back by client with request to /post. This will lead to creation of media that has no post - Storage Garbage Collector. 

"""        





    



    




    
    
    
    








