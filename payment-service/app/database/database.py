from supabase import AsyncClient, create_async_client
from datetime import datetime
from typing   import List, Optional
from uuid     import UUID
from os       import environ

from database.models import PaymentModel, TariffModel

class Database:
    def __init__(self, client: AsyncClient) -> None:
        self.__client: AsyncClient = client

        self.__schema: str = 'public'

    @classmethod
    async def serve(cls):
        client = await create_async_client(
            environ.get('SUPABASE_ENDPOINT'),
            environ.get('SUPABASE_KEY')
        )

        return cls(client)
    
    @property
    def client(self) -> AsyncClient:
        return self.__client

    async def get_tariffs(self) -> List[TariffModel]:
        response = (
            await self.__client
                .schema(self.__schema)
                .table('tariffs')
                .select('*')
                .execute()
        )

        return [
            TariffModel(**tariff) 
            for tariff in response.data
        ]

    async def get_tariff_by_id(self, id: int) -> Optional[TariffModel]:
        response = (
            await self.__client
                .schema(self.__schema)
                .table('tariffs')
                .select('*')
                .eq('id', id)
                .maybe_single()
                .execute()
        )

        if response.data:
            return TariffModel(**response.data)
        
        return None

    async def get_payments(self) -> List[PaymentModel]:
        response = (
            await self.__client
                .schema(self.__schema)
                .table('payments')
                .select('*')
                .execute()
        )

        return [
            PaymentModel(**payment) 
            for payment in response.data
        ]

    async def get_payment_by_id(self, id: int) -> Optional[PaymentModel]:
        response = (
            await self.__client
                .schema(self.__schema)
                .table('payments')
                .select('*')
                .eq('id', id)
                .maybe_single()
                .execute()
        )

        if response.data:
            return PaymentModel(**response.data)
        
        return None

    async def get_payments_by_user_id(self, user_id: UUID) -> List[PaymentModel]:
        response = (
            await self.__client
                .schema(self.__schema)
                .table('payments')
                .select('*')
                .eq('user_id', user_id)
                .execute()
        )

        return [
            PaymentModel(**payment) 
            for payment in response.data
        ]

    async def is_subscription_valid(self, user_id: UUID) -> bool:
        payments: List[PaymentModel] = await self.get_payments_by_user_id(user_id)

        current_date = datetime.now()

        for payment in payments:
            if payment.valid_until and (payment.valid_until >= current_date):
                return True
            
        return False
    
    
    async def update_payment_from_webhook(self, payment_data: dict) -> None:
        response = await self.__client.table('payments').select('*').eq('payment_id', payment_data.get('payment_id')).maybe_single().execute()
        
        if response and response.data:
            await self.__client.table('payments').update(
                payment_data
            ).eq('payment_id', payment_data.get('payment_id')).execute()
            
            # logging.info(f'Updated payment record for payment_id {payment_id}')
            
        else:
            await self.__client.table('payments').insert(
                payment_data
            ).execute()
            
            # logging.info(f'Created new payment record for payment_id {payment_id}')

        # except Exception as e:
            # logging.error(f'Failed to update payment: {str(e)}')
            # raise Exception(f'Failed to update payment: {str(e)}')


