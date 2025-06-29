from core import telegram_client, LoggerService, TelegramControlService
from interface.telegram_service_pb2_grpc import add_TelegramControlServiceServicer_to_server

from concurrent import futures
from os         import environ

import asyncio
import grpc

async def serve():

    LoggerService.init() 

    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers = int(environ.get('MAX_WORKERS', 50)))
    )

    add_TelegramControlServiceServicer_to_server(TelegramControlService(), server)  # Регистрируем сервис

    PORT = environ.get('PORT', 50052)

    server.add_insecure_port(f'[::]:{PORT}')

    await server.start()

    await telegram_client.start()
    
    LoggerService.info(f'Cервер запущен на порту {PORT}...')

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        LoggerService.info(f'Cервер остановлен, порт {PORT} свободен')
    except Exception as e:
        LoggerService.info(f'Непредвиденная ошибка: {e}')
    
    await telegram_client.stop()

        
if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        LoggerService.info('\nВыход по Ctrl+C (KeyboardInterrupt)')