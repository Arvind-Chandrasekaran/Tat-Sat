from pydantic import BaseModel



class SignedUploadURL(BaseModel):
    media_id: str
    path: str
    signed_url: str
    token: str


class PostMedia(BaseModel):
    signed_upload_urls: list[SignedUploadURL]
