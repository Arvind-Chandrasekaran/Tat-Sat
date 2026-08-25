"""
Files request schema/model or format in which responses are given by each end-point
"""

from pydantic import BaseModel, HttpUrl, Field



class Post_RequestBody(BaseModel):

    """
    Pydantic class represents the request body of the /post end-point's reqeuest. 
    This class's instance will be used as parameter in fastAPI and pydantic instance will be created.
    This pydantic class instance is better than a dictionary. As it will not give key error for the optinal value if they are omitted. 
    If the optional key value is omitted, it will give the default value specified after '='. 
    """

    # Required
    text: str

    # Optional: client can omit these entirely
    media_ids: list[str] = Field(default_factory=list, max_length=4)
    reference_url: HttpUrl | None = None
    parent_post_id: str | None = None
    post_topics: list[str] = Field(default_factory=list)

