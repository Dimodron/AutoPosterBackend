from os import environ
from grpc.aio import insecure_channel
import interface.telegram_service_pb2 as telegram_service_pb2
import interface.telegram_service_pb2_grpc as telegram_service_pb2_grpc

class Telegram:
    def __init__(self) -> None:
        self.endpoint: str = environ.get('TELEGRAM_API_GRPC_URL')
    
    async def post_content(self, channel_name: str, content: str, image_url: str = '') -> None:

        async with insecure_channel(self.endpoint) as channel:
            stub = telegram_service_pb2_grpc.TelegramControlServiceStub(channel)
            request = telegram_service_pb2.PostContentRequest(
                channel      = channel_name,
                content      = content,
                image_url    = image_url,
            )
            
            response = await stub.PostContent(request)

            if response.status_code != 200:
                raise SystemError(f'telegram-grpc | {response.detail}')
            
