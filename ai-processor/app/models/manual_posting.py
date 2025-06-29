from pydantic import BaseModel, Field, field_validator

class ManualGeneratedRequestModel(BaseModel):
    prompt: str = Field(..., min_length=3)
    lang: str = Field(..., pattern = r'^\w{2}$')


    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v):
        
        if v and v not in ['en', 'ru', 'de', 'fr']:
            raise ValueError('Unsupported language code')
        return v

    @field_validator('prompt','lang')
    @classmethod
    def not_empty(cls, v, info):

        if not v:
            raise ValueError(f"'{info.field_name}' is required and cannot be None")
        return v

