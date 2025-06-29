from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class SchedulePostSchema(BaseModel):
    post_id: int = Field(..., ge=1)
    scheduled_at: datetime

    @field_validator('scheduled_at')
    def must_be_utc(cls, v: datetime) -> datetime:
        if v.tzinfo != timezone.utc:
            raise ValueError('scheduled_at must be in UTC timezone')
        return v