from interface.analytic_service_pb2_grpc import AnalyticServiceServicer
import interface.analytic_service_pb2 as analytic_service_pb2
from core import Parser, SupabaseDataUpload, SupabaseDataLoad
from core.logs import LoggerService
from clients import Ai

from database import Database
import models
from pydantic import ValidationError

class AnalyticService(AnalyticServiceServicer):
    
    async def ParsingPosts(self, request, context): 
        
        def return_data(code:int,detail:str = ''):
                return analytic_service_pb2.ParsingPostsResponse(
                    code = code,
                    detail = detail,
                )

        data = {
                    "messenger":request.messenger.lower(),
                    "lang":request.lang.lower(),
                }

        try:
            models.ParsingModel(**data)
        except ValidationError as error:

            LoggerService.error('ParsingModel | Validation Error',exc=error)
            
            return return_data(
                code=400,
                detail=str(error)
            )

        LoggerService.debug(f'ParsingPosts | Получены данные:\n{data}')

        db = await Database.serve()

        try:
            channels = await SupabaseDataLoad(db).get_channels(data.get('messenger'))
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.supabase_data_load in get_data_for_analysis')

        LoggerService.debug(f'ParsingPosts | Получены каналы: {len(channels)}')

        if not channels:
            LoggerService.warning('ParsingPosts | Not channels in db')
            return return_data(404,'Not channels in data base')
        
        try:
            records = await Parser.parsing_posts(channels)
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.parser in parsing_posts')

        LoggerService.debug(f'ParsingPosts | Получены записи: {len(records.get('parsed_posts'))}')

        if (not records.get('channels')) or (not records.get('parsed_posts')):
            LoggerService.warning('Not posts in channels or repeated posts')
            return return_data(404,'Not posts in channels or repeated posts')

        try:
            await SupabaseDataUpload(db).upload_parsed_posts(data.get('messenger'),records)
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.supabase_data_upload in upload_parsed_posts')

        LoggerService.debug('ParsingPosts |  успешная загрузка')

        return return_data(200, 'Ok')
    
    async def AnalyticPosts(self, request, context):
        
        def return_data(code:int,detail:str = ''):
                    return analytic_service_pb2.ParsingPostsResponse(
                        code = code,
                        detail = detail,
                    )
        
        data = {
                    "messenger":request.messenger,
                    "lang":request.lang,
                }

        LoggerService.debug(f'AnalyticPosts | Получены данные:\n{data}')

        try:
            models.AnalyticModel(**data)
        except ValidationError as error:

            LoggerService.error('AnalyticModel | Validation Error',exc=error)
            
            return return_data(
                code=400,
                detail=str(error)
            )

        db = await Database.serve()
        
        try:
            data_analytic = await SupabaseDataLoad(db).get_data_for_analysis(data.get('messenger'))
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.supabase_data_load in get_data_for_analysis')
        
        LoggerService.debug(f'AnalyticPosts | Получены каналы для аналитики: {len(data_analytic)}')

        if not data_analytic:
            LoggerService.warning('Not chanel for analytic')
            return return_data(404,'Not chanel for analytic')

        ai = Ai()

        try:
            response = await ai.analytic_posts(data_analytic,data.get('lang'))
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.ai in analytic_posts')

        LoggerService.debug(f'AnalyticPosts | Полученная аналитика по {len(response)} каналам: ')

        try:
            await SupabaseDataUpload(db).upload_analytic(data.get('messenger'),response)
        except Exception as error:
            LoggerService.error(error, exc=error)
            return return_data(500, f'{type(error).__name__}: {error} | core.supabase_data_upload in upload_analytic')

        LoggerService.debug('AnalyticPosts | успешная загрузка')

        return return_data(200, 'Ok')