from pydantic import BaseModel

class TariffModel(BaseModel):
    id:       int       # int8    -> int
    title:    str       # varchar -> str
    price:    int       # int8    -> int (цены в копейках, храним в int)
    currency: str       # varchar -> str
    service:  str