from yookassa import Configuration, Payment
from typing   import Dict, Any
from uuid     import uuid4, UUID
from os       import environ

from core.payment_service import PaymentService

class Yookassa(PaymentService):
    '''Сервис для работы с платежами через ЮKassa.'''
    def __init__(self) -> None:
        self.__shop_id:    int = environ.get('YOOKASSA_SHOP_ID')
        self.__secret_key: str = environ.get('YOOKASSA_SECRET_KEY')
        self.__return_url: str = environ.get('RETURN_URL')

        Configuration.account_id = self.__shop_id
        Configuration.secret_key = self.__secret_key

    async def initiate_payment(self, user_id: UUID, tariff_id: int, amount: int, currency: str = 'RUB') -> Dict[str, Any]:
        idempotence_key: str = str(uuid4())

        payment_data: Dict[str, Any] = {
            'amount' : {
                'value'    : str(round(amount / 100, 2)), # Преобразование копеек в рубли
                'currency' : currency
            },
            'confirmation': {
                'type'       : 'redirect', # Возвращает URL для перенаправления на страницу оплаты
                'return_url' : self.__return_url
            },
            'capture'     : True, # Автоматическое списание средств
            'description' : f'Оплата сервиса AutoPoster {tariff_id}-{user_id}',
            'metadata' : {
                'user_id'   : str(user_id),
                'tariff_id' : str(tariff_id)
            }
        }

        try:
            payment = Payment.create(payment_data, idempotence_key)
            
            return {
                'payment_id'       : payment.id,
                'confirmation_url' : payment.confirmation.confirmation_url
            }

        except Exception as error:
            raise Exception(f'Ошибка при создании платежа: \n{str(error)}')