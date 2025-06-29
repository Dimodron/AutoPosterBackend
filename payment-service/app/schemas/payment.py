from pydantic import BaseModel

class PaymentInitiationSchema(BaseModel):
    tariff_id: int