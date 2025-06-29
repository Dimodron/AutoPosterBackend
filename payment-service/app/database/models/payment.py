from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class PaymentModel(BaseModel):
    id: Optional[int] = None
    user_id: UUID
    status: str
    amount: int
    currency: str
    valid_until: datetime
    tariff_id: int
    balance: int
    payment_id: Optional[UUID] = None
    payed_at: datetime
