from fastapi import APIRouter, Request, status, Depends, Header 
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 
from security.jwt_manager import JWTManager
from domain.object_storage import object_storage
from domain.database import database
import domain.ai_service as ai_service
import network.request_parser as request_parser
import network.request_models as request_models
import network.response_models as response_models
import asyncio

router = APIRouter()

@router.get(
    "/post-media-urls",
    tags=["Create Signed Upload URLs for Media"],
    responses={
        200: {"model": response_models.PostMediaURLs, "description": "List of signed upload urls."},       
        401: {"description": "Invalid Authentication Credentials"}
    }
)
async def post_media_urls(http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj_creator)):
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = await JWTManager.create(jwt)   
    user_id = jwt_manager.user_id
    signed_upload_urls = await object_storage.create_signed_url_upload(user_id)
    return {"signed_upload_urls": signed_upload_urls}

@router.post(
    "/post",
    tags=["Create a Post"],
    responses={
        200: {"description" : "Post created."}, 
        400: {"description": "Bad request."}
    }
)
async def post(request_body: request_models.Post_RequestBody, http_authorization_header_credentials_obj: HTTPAuthorizationCredentials = Depends(request_parser.http_authorization_header_credentials_obj_creator)):
    jwt = http_authorization_header_credentials_obj.credentials
    jwt_manager = await JWTManager.create(jwt)
    user_id = jwt_manager.user_id

    # 1. AI Analysis & Embedding
    analysis, embedding = await asyncio.gather(
        ai_service.analyze_post_content(request_body.content, request_body.type.value == "VIDEO"),
        ai_service.generate_embedding(request_body.content)
    )

    # 2. Topic Extraction
    # Fetch recent topics to prime the AI
    recent_posts = await database.get_recent_posts()
    recent_topics = list(set([p.get('topic') for p in recent_posts if p.get('topic')]))[:10]
    topic = await ai_service.analyze_post_topic(request_body.content, recent_topics)
    topic_embedding = await ai_service.generate_embedding(topic) if topic else None

    # 3. Relationship Mapping
    similar_posts = []
    if embedding and analysis.get('score', 0) > 40:
        similar_posts = await database.get_similar_posts(embedding, topic_embedding, match_threshold=0.5, match_count=5)
    
    if similar_posts:
        rel_map = await ai_service.analyze_post_relationships(request_body.content, similar_posts)
        analysis['semanticConnections'] = [
            {"postId": post_id, "type": rel_type} 
            for post_id, rel_type in rel_map.items()
        ]

    # 4. Insert to Database
    await database.insert(
        request_body=request_body,
        user_id=user_id,
        analysis=analysis,
        topic=topic,
        embedding=embedding,
        topic_embedding=topic_embedding
    )

    return {"message": "Post Created."}


@router.get(
    "/feed",
    tags=["Get Feed"]
)
async def get_feed(filter: str = "ALL"):
    try:
        query = database._supabase_service_client.schema("domain").table("posts").select("id, text, user_id, analysis, topic, created_at, post_status").eq("post_status", "active").order("created_at", desc=True)
        response = await query.execute()
        posts = response.data if response and hasattr(response, 'data') else []
        
        # map 'text' to 'content' for the frontend compatibility
        for p in posts:
            p['content'] = p.get('text', '')

        if filter == "HIGH_QUALITY":
            posts = [p for p in posts if p.get('analysis', {}).get('score', 0) >= 70]
            
        return {"feed": posts}
    except Exception as e:
        print(f"Error fetching feed: {e}")
        return {"feed": []}

@router.get("/health", tags=["Check health of the service"])
def health():
    return {"status": "ok"}
