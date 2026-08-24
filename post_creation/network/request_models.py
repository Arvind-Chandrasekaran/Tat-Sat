"""
Files request schema/model or format in which responses are given by each end-point
"""

from pydantic import BaseModel, HttpUrl


class PostBodySchema(BaseModel):
    text: str

    media_1: str
    media_2: str
    media_3: str
    media_4: str

    reference_link: HttpUrl   # it check if the value is a valid http(s) url. later can be converted to str

    parent_post_id: str
    post_topics: list[str]