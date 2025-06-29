from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from apscheduler.triggers.date import DateTrigger
from models import MessageScheduleModel,PostGenerateModel
from core import LoggerService
from clients import Ai,Telegram


router = APIRouter(prefix="/manualposting", tags=["Telegram"])

@router.post(
    '/schedule', 
    tags = ['manualposting'], 
    summary = 'Schedule message for sending'
)
async def telegram_post_schedule(
    request: Request,
    message: MessageScheduleModel, 
    messenger: str | None = Header(..., alias = 'Messenger'), 
    user_id:   str | None = Header(..., alias = 'User')
) -> JSONResponse:

    try:
        post = await (
            request.app.state.database.client
            .schema(messenger)
            .table('manual_posts')
            .select('id,content,is_publicated,image_url')
            .eq('id', message.post_id)
            .eq('user_id', user_id)
            .maybe_single()
            .execute()
        )
    except Exception as error:
        LoggerService.error(error, exc=error)
        raise HTTPException(status_code = 500, detail=f'{type(error).__name__}: {error} | routes.telegram_post_schedule in get_post') 

    LoggerService.debug(' @router.post(/manualposting/schedule) | Получен пост')

    if post.data.get('is_publicated'):
        LoggerService.warning(f'{user_id}: the post has already been published')
        raise HTTPException(status_code = 400, detail = 'the post has already been published')

    tg = Telegram()

    try:
        new_job = request.app.state.manual_posting_scheduler.add_job(
            tg.post_content,
            trigger            = DateTrigger(message.scheduled_at),
            id                 = f'{messenger}_{post.data.get('id')}_{user_id}',
            args               = [message.channel,post.data.get('content'),post.data.get('image_url')],
            misfire_grace_time = 30,
            replace_existing   = True
        )
    except Exception as error:
        LoggerService.error(error, exc=error)
        raise HTTPException(status_code = 500, detail= f'{type(error).__name__}: {error} | routes.telegram_post_schedule in manual_posting_scheduler.add_job')

    LoggerService.info(f'Schedule message for sending: \n id: {new_job.id}, sendingdate: {new_job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    return JSONResponse(
        {
            'job_id':new_job.id
        },
        status_code = 200
    )

@router.post(
    '/generate',
    tags = ['manualposting'], 
    summary = 'Generate post in manual posting'
)
async def manual_gen_post(
    request: Request,
    message: PostGenerateModel,
    messenger: str| None = Header(..., alias = 'Messenger'), 
    user_id: str | None = Header(..., alias = 'User')
)->JSONResponse:
    
    ai = Ai()
        
    try:
        ai = await ai.get_post(message.prompt,"ru")
    except Exception as error:
        LoggerService.error(error, exc=error)
        raise HTTPException(status_code = 500, detail= f'{type(error).__name__}: {error} | routes.manualposting in get_post')

    LoggerService.debug(' @router.post(/manualposting/generate) | Получен пост:')

    if not ai:
        LoggerService.warning('Not generic post')
        raise HTTPException(status_code = 404, detail= 'Not generic post')

    try:
        await (request.app.state.database.client.schema(messenger)
                .table('manual_posts')
                .insert({
                    'content'      : ai,
                    'user_id'      : user_id
                }).execute())
    except Exception as error:
        LoggerService.error(error, exc=error)
        raise HTTPException(status_code = 500, detail= f'{type(error).__name__}: {error} | routes.manualposting in save_in_bd')
    
    LoggerService.debug(' @router.post(/manualposting/generate) | Пост сохранен:')

    return JSONResponse(
        {
            'post_id':60,
            'content':ai
        },
        status_code = 200
    )