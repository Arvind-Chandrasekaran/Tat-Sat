"""
Files request schema/model or format in which responses are given by each end-point
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional

class MediaItem(BaseModel):
    file_id: Optional[str] = None
    is_uploaded: bool = False

class PostBodySchema(BaseModel):
    text: str

    media_1: Optional[MediaItem] = None
    media_2: Optional[MediaItem] = None
    media_3: Optional[MediaItem] = None
    media_4: Optional[MediaItem] = None

    reference_url: Optional[HttpUrl] = None

    parent_post_id: Optional[str] = None
    post_topics: list[str] = []