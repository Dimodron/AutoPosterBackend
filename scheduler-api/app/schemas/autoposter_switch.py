from pydantic import BaseModel, Field

class AutoposterSwitchSchema(BaseModel):
    isActive: bool
