from pydantic import BaseModel, Field

class PostGenerateModel(BaseModel):
    prompt: str = Field(..., min_length=3)