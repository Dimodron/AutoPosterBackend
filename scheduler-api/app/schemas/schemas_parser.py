from pydantic import BaseModel, Field

class ParserSettingsSchema(BaseModel):
    parsing_timeout: int = Field(
        ge = 15,
        le = 60 
    )
