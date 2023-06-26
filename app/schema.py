from pydantic import BaseModel

class ThumbCreate(BaseModel):
    original_img_name: str
    key: str
    thumb_size : int

class GetThumbs(BaseModel):
    original_img_id : int

class ThumbDetail(BaseModel):
    thumb_id : int