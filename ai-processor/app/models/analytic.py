from pydantic import BaseModel, Field, field_validator
from typing import List

class ReactionModel(BaseModel):
    count:int = Field(...)
    emoji:str = Field(...)

class PostModel(BaseModel):
    id:int = Field(...)
    channel:int = Field(...)
    content:str = Field(...)
    posted_at:str = Field(...)
    text_urls:list[str]
    views:int = Field(...) 
    forwards:int = Field(...)
    replies_count:int = Field(...)
    total_reactions:int = Field(...)
    stars:int = Field(...)
    reaction:List[ReactionModel]

class AnalyticPostsRequestModel(BaseModel):
    posts: List[PostModel]
    lang: str = Field(..., pattern = r'^\w{2}$')

    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v):
        
        if v and v not in ['en', 'ru', 'de', 'fr']:
            raise ValueError("Unsupported language code")
        return v

    @field_validator("posts","lang")
    @classmethod
    def not_empty(cls, v, info):

        if not v:
            raise ValueError(f"'{info.field_name}' is required and cannot be None")
        return v
