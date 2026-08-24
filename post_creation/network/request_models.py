"""
Files request schema/model or format in which responses are given by each end-point

"""

from pydantic import BaseModel, HttpUrl


class PostBodySchema(BaseModel):
    text: str
    reference_link: HttpUrl
    media_1: str
    media_2: str
    media_3: str
    media_4: str
    parent_post_id: str
    post_topics: list[str]