from pydantic import BaseModel
from typing import Literal

class AnalyticModel(BaseModel):
    messenger: Literal['telegram', 'vk', 'instagram']
    lang: Literal['en', 'ru', 'de', 'fr']