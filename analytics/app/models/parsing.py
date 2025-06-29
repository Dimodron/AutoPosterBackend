from pydantic import BaseModel
from typing import Literal

class ParsingModel(BaseModel):
    messenger: Literal['telegram', 'vk', 'instagram']
    lang: Literal['en', 'ru', 'de', 'fr']