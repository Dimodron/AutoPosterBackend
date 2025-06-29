from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional

class AddAndSchedulePostSchema(BaseModel):
    content: str
    image_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    
    @field_validator('scheduled_at')
    def must_be_utc(cls, v: datetime) -> datetime:
        if v.tzinfo != timezone.utc:
            raise ValueError('scheduled_at must be in UTC timezone')
        return v