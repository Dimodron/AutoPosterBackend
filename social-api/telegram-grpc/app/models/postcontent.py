from pydantic import BaseModel, Field
from typing import Optional

class PostContentModel(BaseModel):
    channel:str = Field(..., pattern = r'^@[a-zA-Z0-9_]{5,32}$')
    content:str =  Field(...,min_length=3)
    image_url: Optional[str] = Field(
        default=None,
        pattern=r"\b(?:https?://|www\.)[0-9A-Za-z\-._~:/?#\[\]@!$&'()*+,;=%]+\b",
    )
