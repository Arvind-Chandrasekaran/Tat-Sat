"""
Response schema/model or format in which responses are given by each end-point

"""


from pydantic import BaseModel



# post/media

class SignedUploadURL(BaseModel):
    media_id: str
    path: str
    signed_url: str
    token: str


class PostMediaURLs(BaseModel):
    signed_upload_urls: list[SignedUploadURL]
    
