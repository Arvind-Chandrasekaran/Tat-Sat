# Network 
from fastapi import APIRouter, status, Depends, HTTPException 
from fastapi.responses import JSONResponse

import network.request_parser as request_parser
import network.response_models as response_models


# Security
from fastapi.security import HTTPAuthorizationCredentials 
from security.jwt_client import JWTClient, InvalidJWTError, JWTVerifierError



# domain 
from domain.object_storage_client import object_storage_client




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
    








@router.get(

    "/health",

    tags=["Check health of the service"],

    description="""
    Check if the service is active. Returns 200 ok when it is. 
    """,


            )
async def health():
    return {"status": "ok"}





















    



    




    
    
    
    








