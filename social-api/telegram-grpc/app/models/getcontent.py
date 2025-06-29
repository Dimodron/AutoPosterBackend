from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime

class GetContentModel(BaseModel):
    channel:str = Field(..., pattern = r'^@[a-zA-Z0-9_]{5,32}$')
    parsing_count:int =  Field(...,ge=1)
    last_post:Optional[str] = Field(default=None)

    @field_validator("last_post")
    @classmethod
    def validate_datetime_string(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("last_post must be a valid ISO datetime string")
        return v