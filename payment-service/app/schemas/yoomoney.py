from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

class Amount(BaseModel):
    value: str
    currency: str

class Recipient(BaseModel):
    account_id: str
    gateway_id: str

class PaymentMethod(BaseModel):
    type: str
    id: str
    saved: bool
    status: Optional[str]
    title: str
    account_number: Optional[str]

class YooMoneyWebhookObject(BaseModel):
    id: UUID
    status: str
    amount: Amount
    income_amount: Optional[Amount]
    description: str
    recipient: Optional[Recipient]
    payment_method: PaymentMethod
    captured_at: Optional[datetime]
    created_at: datetime
    test: bool
    refunded_amount: Optional[Amount]
    paid: bool
    refundable: bool
    metadata: Dict[str, str]

class YooMoneyWebhookSchema(BaseModel):
    type: str
    event: str
    object: YooMoneyWebhookObject