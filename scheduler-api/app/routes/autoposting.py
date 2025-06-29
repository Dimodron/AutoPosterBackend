from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from core import LoggerService, Autoposting
from clients import Telegram
from datetime import datetime

router = APIRouter(prefix="/autoposter", tags=["autoposter"])

@router.post(
    '/start', 
    tags = ['autoposter'], 
    summary = 'Start Autoposting'
)
async def autoposting(
    request: Request,
    messenger: str| None = Header(..., alias = 'Messenger'), 
    user_id: str | None = Header(..., alias = 'User')
) -> JSONResponse:

    autpost= Autoposting(request.app.state.database,user_id,messenger,request.app.state.auto_posting_scheduler)

    try:
        await autpost.start_loop()
    except Exception as error:
        LoggerService.error(f'user-id: {user_id}|routes.autoposter in start_loop|{type(error).__name__}',exc=error)
        raise HTTPException(status_code = 500, detail=f'user-id: {user_id}|routes.autoposter in start_loop|{type(error).__name__}: {error}')

    return JSONResponse({},status_code = 200)

# @router.post(
#     '/stop', 
#     tags = ['Telegram'], 
#     summary = 'Stop autoposting'
# )
# async def autoposting(
#     mode: AutoposterSwitchSchema, 
#     messenger: str| None = Header(..., alias = 'Messenger'), 
#     user_id: str | None = Header(..., alias = 'User')
# ) -> JSONResponse:

# @router.post(
#     '/edit_time', 
#     tags = ['Telegram'], 
#     summary = 'get_autoposter_state'
# )
# async def autoposting( 
#     messenger: str| None = Header(..., alias = 'Messenger'), 
#     user_id: str | None = Header(..., alias = 'User')
# ) -> JSONResponse:
#     ...

@router.get(
    '/schedule_status', 
    tags = ['Telegram'], 
    summary = 'get utoposting schedule job'
)
async def autoposting(
    request: Request,
    messenger: str| None = Header(..., alias = 'Messenger'), 
    user_id: str | None = Header(..., alias = 'User')
) -> JSONResponse:
    
    user_jobs = [
        {"id":job.id, "run_time":job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")} for job in request.app.state.auto_posting_scheduler.get_jobs()
        if user_id in job.id
    ]

    return JSONResponse(
        {
            "jobs":user_jobs
        },
        status_code = 200
    )