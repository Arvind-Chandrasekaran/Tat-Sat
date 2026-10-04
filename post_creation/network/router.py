# Network 
from fastapi import APIRouter, status, Depends, HTTPException 
from fastapi.responses import JSONResponse

import network.request_parser as request_parser
import network.request_models as request_models
import network.response_models as response_models



# Security
from fastapi.security import HTTPAuthorizationCredentials 
from security.jwt_client import JWTClient, InvalidJWTError, JWTVerifierError



# domain 
from domain.object_storage_client import object_storage_client
from domain.post_creation_messaging_queue_client import post_creation_messaging_queue_client





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

    try:
        jwt_client = await JWTClient.create(jwt)  # will perform authN and authZ  

    except InvalidJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


    except JWTVerifierError:
        raise HTTPException(
            status_code=500,
            detail="Authentication service unavailable",
        )




    # create signed upload url for return 
    user_id = jwt_client.user_id
    signed_upload_urls = await object_storage_client.create_signed_url_upload(user_id)

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
        
        # 422 (request body validation error) and 200 (success status code are usually added automatically).
    
                    202: {
                            "description": "Post submitted for processing",
                            "content": {
                                            "application/json": {
                                                "example": {
                                                    "status": "queued",
                                                    "message": "Post submitted for processing",
                                                    "queue_id": "entry_id"
                                                            }
                                                                }
                                    }
                        },

                    
                    500 : {
                            
                            "description" : "Server Error"

                          }
                    



                }

    )

async def post( request_body : request_models.Post_RequestBody,  http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj_creator)):

    # AuthN & AuthZ  
    # http_authorization_header_credentials_obj = request_parser.http_authorization_header_credentials_obj_creator.__call__(request)   # request is instance of Request. but no need for this, we have the done it using Depends 
    jwt = http_authorization_header_credentials_obj.credentials
    
    try:
        jwt_client = await JWTClient.create(jwt)  # will perform authN and authZ  

    except InvalidJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTVerifierError:
        raise HTTPException(
            status_code=500,
            detail="Authentication service unavailable",
        )


    # Uploaded post to messaging queue
    user_id = jwt_client.user_id

    try:
            entry_id = await post_creation_messaging_queue_client.upload(
                request_body=request_body, user_id=user_id
            )

            return JSONResponse(
                                status_code=202,
                                content= {
                                            "status": "queued",
                                            "message": "Post submitted for processing",
                                            "queue_id": entry_id,
                                         },
                                )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to enqueue post due to an internal error.",
        )
 








@router.get(

    "/health",

    tags=["Check health of the service"],

    description="""
    Check if the service is active. Returns 200 ok when it is. 
    """,


            )
async def health():
    return {"status": "ok"}





















    



    




    
    
    
    








