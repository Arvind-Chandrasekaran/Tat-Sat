from fastapi import APIRouter, Request, status, Depends, Header 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 

from security.jwt_manager import JWTManager

from domain.object_storage import object_storage
from domain.supabase_service_client import supabase_service_client

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

        400: { 
            "description": "Invalid Media ID(s).",
        }

    },

             )
async def post( request_body : request_models.Post_RequestBody,  http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj_creator)):

    # AuthN & AuthZ  
    # http_authorization_header_credentials_obj = request_parser.http_authorization_header_credentials_obj_creator.__call__(request)   # request is instance of Request. but no need for this, we have the done it using depends 
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = await JWTManager.create(jwt) # will perform authN and authZ   


    # check for phantom media ids
    # (this can be outsourced to the media verifier, that kind of modularity makes sense, but having it hear reduces false requests before database enrty is made.)

    user_id = jwt_manager.user_id
    await object_storage.media_id_presence_check(request_body.media_ids, user_id)
    


    # create post database entry with status pending
    





    # send request to media verifier's messaging queue 
    # once it is implemented
        





    return {"message" : "Post Created."}




















"""
Key Notes 

Rogue Client Security 
1 - Malicious file being uplaoded to storage using signed upload url - Proxy Storage and Check magic bytes of the files being uploaded to the storage before approving the post entry in database. 
2 - Phantom  Posts - Post not uploaded by a client could send the media_id as being uploaded - Check the media_ids sent by client. 
3 - Orphan Posts - Post could be uploaded to link but not sent back by client with request to /post. This will lead to creation of media that has no post - Storage Garbage Collector. 

"""        





    



    




    
    
    
    








