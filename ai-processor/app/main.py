from concurrent import futures

from interface.ai_service_pb2_grpc import add_AiServiceServicer_to_server

from core.logs import LoggerService
from core.ai_service import AiService

import asyncio
import grpc
from os import environ 

async def serve():
    
    LoggerService.init()

    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers = int(environ.get('MAX_WORKERS', 50)))
    )

    add_AiServiceServicer_to_server(AiService(), server)

    PORT = int(environ.get('PORT', 50060))
    
    server.add_insecure_port(f'[::]:{PORT}')
    
    await server.start()

    LoggerService.info(f'Cервер запущен на порту {PORT}...')

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        LoggerService.info(f'Cервер остановлен, порт {PORT} свободен')
    except Exception as e:
        LoggerService.info(f'Непредвиденная ошибка: {e}')

if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        LoggerService.info('\nВыход по Ctrl+C (KeyboardInterrupt)')