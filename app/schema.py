from pydantic import BaseModel

class ThumbCreate(BaseModel):
    original_img_name: str
    key: str
    thumb_size : int
