from pydantic import BaseModel, Field, field_validator
from typing import List


class PostModel(BaseModel):
    id: int
    content: str
    posted_at: str

class AutoGeneratedRequestModel(BaseModel):
    posts: List[PostModel]
    prompts: List[str]
    prompt_base: str = Field(...)
    tone_of_voice: str = Field(...)
    
    words_count: int = Field(..., ge=1)
    use_emoji: bool
    use_hashtag: bool
    lang: str = Field(..., pattern = r'^\w{2}$')


    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v):
        
        if v and v not in ['en', 'ru', 'de', 'fr']:
            raise ValueError("Unsupported language code")
        return v

    @field_validator("posts","prompts","prompt_base", "tone_of_voice", "lang", "words_count")
    @classmethod
    def not_empty(cls, v, info):

        if not v:
            raise ValueError(f"'{info.field_name}' is required and cannot be None")
        return v

