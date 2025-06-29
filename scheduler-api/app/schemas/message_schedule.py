from pydantic import BaseModel, Field
from typing   import Optional
from datetime import datetime

class MessageScheduleSchema(BaseModel):
    post_id: int
    scheduled_at: datetime
    
class MessageAddSchema(BaseModel):
    content: str
    scheduled_at: Optional[datetime] = Field(None)
    image_url: Optional[str] = Field(None)