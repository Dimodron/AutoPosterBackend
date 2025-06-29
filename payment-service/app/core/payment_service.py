from abc    import ABC, abstractmethod
from typing import Dict, Any
from uuid   import UUID

class PaymentService(ABC):
    @abstractmethod
    async def initiate_payment(
        self, 
        user_id:   UUID, 
        tariff_id: int, 
        amount:    int, 
        currency:  str
    ) -> Dict[str, Any]:
        ...
    
    # @abstractmethod
    # async def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
    #     ...
    
    # @abstractmethod
    # async def handle_webhook(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    #     ...