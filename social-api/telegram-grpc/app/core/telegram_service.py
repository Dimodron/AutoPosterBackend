from interface.telegram_service_pb2 import GetContentResponse, ContentData, PostContentResponse
from interface.telegram_service_pb2_grpc import TelegramControlService

from core.telegram import telegram_client
from core.logs import LoggerService

import models

from pydantic import ValidationError 

class TelegramControlService(TelegramControlService):
    async def GetContent(self, request, context):
        
        def return_data(code:int,detail:str, content:list[ContentData] = []):
                return GetContentResponse(
                status_code = code,
                detail = detail,
                data = content,
            )

        data = {
                    "channel":request.channel,
                    "parsing_count":request.parsing_count,
                    "last_post":request.last_post if request.last_post !='' else None,
                }

        try:
            models.GetContentModel(**data)
        except ValidationError as error:
            LoggerService.error('GetContent | Validation Error',exc=error)
            return return_data(
                code=400,
                detail=str(error)
            )

        LoggerService.debug(f'GetContent | Получены данные:\n{data}')

        try:
            messages: list[ContentData] = await telegram_client.parsing_channel(request.channel,request.parsing_count,request.last_post)
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.telegram in parse')

        LoggerService.debug(f'GetContent | Получены посты по каналу {data.get('channel')} :{len(messages)}')
        
        if not messages:
            LoggerService.warning('Not tg messages')
            return_data(404,'Not messages for tg channel')

        return return_data(200,'ok',messages)

    async def PostContent(self, request, context):  
        def return_data(code:int,detail:str):
                return PostContentResponse(
                status_code = code,
                detail = detail,
            )

        data = {
                    "channel":request.channel,
                    "content":request.content,
                    "image_url":request.image_url if request.image_url !='' else None,
                }
        try:
            models.PostContentModel(**data)
        except ValidationError as error:
            LoggerService.error('PostContentModel | Validation Error',exc=error)
            return return_data(
                code=400,
                detail=str(error)
            )
        
        LoggerService.debug(f'PostContent | Получены данные:\n{data}')

        try:
            await telegram_client.send(**data)
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.telegram in send')

        LoggerService.debug(f'PostContent | Данные ушли в канаl: {data.get('channel')}')

        return return_data(200,'ok')
    
    
    
