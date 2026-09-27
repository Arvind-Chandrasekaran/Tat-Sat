from pydantic import BaseModel, HttpUrl, Field, model_validator
from enum import Enum

class PostUserVisibilityType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class PostStatus(Enum):
    ACTIVE = "active"
    PENDING = "pending"
    REJECTED = "rejected"
    DELETED = "deleted"

class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

class PostType(Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"

class Post_RequestBody(BaseModel):
    # Required
    content: str = Field(..., max_length=560, description="Post content, limited to 560 chars per cognitive throughput derivation")
    type: PostType = PostType.TEXT

    # Optional
    long_text: str | None = None
    media_url: str | None = None
    media_ids: list[str] = Field(default_factory=list, max_length=4)
    media_types: list[MediaType] = Field(default_factory=list, max_length=4)
    reference_link: HttpUrl | None = None
    parent_post_id: str | None = None
    post_user_visibility: PostUserVisibilityType = PostUserVisibilityType.PUBLIC

    @model_validator(mode="after")
    def validate_media_lists(self):
        if len(self.media_ids) != len(self.media_types):
            raise ValueError("media_types length must match media_ids length")
        return self
