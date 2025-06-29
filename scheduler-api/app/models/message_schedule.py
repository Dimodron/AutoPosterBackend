from pydantic import BaseModel, field_validator, Field
from typing   import Optional
from datetime import datetime

class MessageScheduleModel(BaseModel):
    post_id: int
    channel:str = Field(..., pattern = r'^@[a-zA-Z0-9_]{5,32}$')
    scheduled_at: str

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v: str) -> str:
        if v is None:
            return v

        try:
            dt = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("scheduled_at must be a valid ISO datetime string")

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        if dt < now:
            raise ValueError("scheduled_at must be in the future (>= now)")

        return v