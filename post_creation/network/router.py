# Network
import base64
import json

from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from post_creation.network import request_parser, request_models, response_models



# Security
from fastapi.security import HTTPAuthorizationCredentials
from post_creation.security.jwt_client import JWTClient, InvalidJWTError, JWTVerifierError



# domain
from post_creation.domain.object_storage_client import object_storage_client
from post_creation.domain.post_creation_messaging_queue_client import post_creation_messaging_queue_client
from post_creation.domain.supabase_service_client import supabase_service_client





router = APIRouter()


def _decode_feed_cursor(cursor: str | None) -> str | None:
    if not cursor:
        return None
    try:
        payload = json.loads(
            base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
        )
        return payload["created_at"]
    except (ValueError, KeyError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid feed cursor") from exc


def _encode_feed_cursor(created_at: str) -> str:
    payload = json.dumps({"created_at": created_at}).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii")


@router.get(
    "/feed",
    tags=["Feed"],
    description="Returns visible active posts for the frontend feed.",
)
async def feed(
    filter: str = Query(default="ALL", pattern="^(ALL|HIGH_QUALITY)$"),
    cursor: str | None = None,
    limit: int = Query(default=20, ge=1, le=50),
):
    cursor_created_at = _decode_feed_cursor(cursor)
    query = (
        supabase_service_client
        .schema("domain")
        .table("posts")
        .select("*")
        .eq("post_status", "active")
        .eq("post_user_visibility", "public")
        .order("created_at", desc=True)
        .limit(limit + 1)
    )
    if cursor_created_at:
        query = query.lt("created_at", cursor_created_at)

    response = await query.execute()
    posts = response.data or []
    if filter == "HIGH_QUALITY":
        posts = [
            post for post in posts
            if int((post.get("analysis") or {}).get("score", 0)) > 50
        ]
    has_more = len(posts) > limit
    posts = posts[:limit]
    next_cursor = (
        _encode_feed_cursor(posts[-1]["created_at"])
        if has_more and posts
        else None
    )
    return {"feed": posts, "next_cursor": next_cursor}



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
    status_code = 202,

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



                    401 : {
                            "description": "Invalid authentication credentials.",

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
