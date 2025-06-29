from os import environ
from grpc.aio import insecure_channel
import interface.telegram_service_pb2 as telegram_service_pb2
import interface.telegram_service_pb2_grpc as telegram_service_pb2_grpc
from typing import Optional

class Telegram:
    
    def __init__(self) -> None:
        self.endpoint: str = environ.get('TELEGRAM_API_GRPC_URL')

    async def get_content(self, channel_name: str, count_posts: int, last_post_date: Optional[str] ):

        async with insecure_channel(self.endpoint) as channel:
            
            stub = telegram_service_pb2_grpc.TelegramControlServiceStub(channel)
            
            request = telegram_service_pb2.GetContentRequest(
                channel = channel_name,
                parsing_count = count_posts,
                last_post = last_post_date,
            )
            
            response = await stub.GetContent(request)

            if response.status_code != 200:
                raise SystemError(f'telegram-grpc | {response.detail}')
            
            return response.data

class Instagram:
    ...
    
class Vk:
    ...