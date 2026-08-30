"""
Request schema/model or format in which request is to be given to each end-point
"""

from pydantic import BaseModel, HttpUrl, Field
from enum import Enum



class PostUserVisibilityType(Enum):

    public = 1
    private = 2 




class Post_RequestBody(BaseModel):

    """
    Pydantic class represents the request body of the /post end-point's reqeuest. 
    This class's instance will be used as parameter in fastAPI and pydantic instance will be created.
    This pydantic class instance is better than a dictionary. As it will not give key error for the optinal value if they are omitted. 
    If the optional key value is omitted, the object will give the default value specified after '='. 
    """

    # Required
    text: str
    post_user_visibility : PostUserVisibilityType = PostUserVisibilityType.public

    # Optional: client can omit these entirely
    long_text : str | None = None
    media_ids: list[str] = Field(default_factory=list, max_length=4)
    reference_link: HttpUrl | None = None
    parent_post_id: str | None = None


