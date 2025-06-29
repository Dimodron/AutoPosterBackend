from fastapi                 import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core                    import LoggerService
from core.lifespan           import lifespan
from routes                  import manualposting,autoposting

LoggerService.init()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "User"],
    expose_headers=["*"],
)

app.include_router(manualposting.router)
app.include_router(autoposting.router)



# from fastapi                        import FastAPI, Header, HTTPException
# from fastapi.middleware.cors        import CORSMiddleware
# from fastapi.responses              import JSONResponse

# from contextlib                     import asynccontextmanager
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.date      import DateTrigger
# from apscheduler.triggers.interval  import IntervalTrigger


# from models                        import ParserSettingsSchema, MessageScheduleSchema, MessageAddSchema, AutoposterSwitchSchema
# from database                       import Database
# from core                           import initialize_scheduled_jobs, update_user_job, publish_message_job, autoposting_post, delivery_to_queue
# from core.logs                      import LoggerService
# from integrations                   import ai_client

# from datetime                       import datetime,timezone, timedelta
# from os                             import environ
# from typing                         import AsyncGenerator, Any
# import sentry_sdk

# parse_scheduler   = AsyncIOScheduler()
# publish_scheduler = AsyncIOScheduler()
# autoposter_scheduler = AsyncIOScheduler()

# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    
#     sentry_sdk.init(
#         dsn              = environ.get('SENTRY_URL'),
#         send_default_pii = True,
#     )
    
#     app.state.database          = await Database.serve()
    
#     app.state.log               = LoggerService()
#     app.state.parse_scheduler   = parse_scheduler
#     app.state.publish_scheduler = publish_scheduler
#     app.state.autoposter_scheduler = autoposter_scheduler

#     app.state.publish_scheduler.start()
#     app.state.parse_scheduler.start()
#     app.state.autoposter_scheduler.start()
#     app.state.autoposter_scheduler.start()


#     try:
#         await initialize_scheduled_jobs(app)
#     except Exception as error:
#         sentry_sdk.capture_exception(error)
#         app.state.log.error('Error initialize jobs', exc=error)

#     try:
#         yield
#     finally:
#         app.state.parse_scheduler.shutdown()
#         app.state.publish_scheduler.shutdown()
#         app.state.autoposter_scheduler.shutdown()
        
# app = FastAPI(
#     lifespan = lifespan
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins     = ['*'],
#     allow_credentials = True,
#     allow_methods     = ['*'],
#     allow_headers     = ['Content-Type', 'User', 'Messenger'],
#     expose_headers    = ['*'],
# )

# @app.post(
#     '/telegram/parse/timeout', 
#     tags = ['Telegram'], 
#     summary = 'Change parsing timeout'
# )
# async def telegram_parse_timeout(
#     parser_settings: ParserSettingsSchema, 
#     user_id: str | None = Header(..., alias = 'User')
# ) -> JSONResponse:
#     interval: int = parser_settings.parsing_timeout

#     try:
#         await update_user_job(
#             app      = app,
#             user     = user_id,
#             interval = interval
#         )

#     except Exception as error:
#         sentry_sdk.capture_exception(error)
#         app.state.log.error('An error occured while updating parser job',exc=error)
#         raise HTTPException(
#             status_code = 500,
#             detail      = f'An error occured while updating parser job Error: {error}'
#         )

#     return JSONResponse(
#         {
#            'message': f'Parsing timeout updated to {interval} minutes for user {user_id}'
#         },
#         status_code = 200
#     )

# @app.post(
#     '/telegram/manual/schedule', 
#     tags = ['Telegram'], 
#     summary = 'Schedule message for sending'
# )
# async def telegram_post_schedule(
#     message: MessageScheduleSchema, 
#     messenger: str | None = Header(..., alias = 'Messenger'), 
#     user_id:   str | None = Header(..., alias = 'User')
# ) -> JSONResponse:
    
#     messenger: str = messenger.lower()
    
#     post: dict[str, Any] = await (
#         app.state.database.client
#             .schema(messenger)
#             .table('manual_posts')
#             .select('is_publicated')
#             .eq('id', message.post_id)
#             .eq('user_id', user_id)
#             .maybe_single()
#             .execute()
#     )

#     if not post:
#         raise HTTPException(
#             status_code = 404,
#             detail      = 'POST_NOT_FOUND'
#         )

#     if post.data.get('is_publicated'):
#         raise HTTPException(
#             status_code = 400,
#             detail      = 'POST_ALREADY_PUBLICATED'
#         )
    
#     new_job = app.state.publish_scheduler.add_job(
#         publish_message_job,
#         trigger            = DateTrigger(message.scheduled_at),
#         id                 = f'{messenger}_{message.post_id}_{user_id}',
#         args               = [message.post_id, messenger, user_id, app],
#         misfire_grace_time = 10,
#         replace_existing   = True
#     )

#     app.state.log.debug(f'Schedule message for sending: \n id: {new_job.id}, sendingdate: {new_job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")}')

#     return JSONResponse(
#         {
#             'message': f'Message sending scheduled at {message.scheduled_at} for user {user_id}'
#         },
#         status_code = 200
#     )

# @app.post(
#     '/telegram/manual/add', 
#     tags = ['Telegram'], 
#     summary = 'Add message for sending'
# )
# async def telegram_post_add(
#     message: MessageAddSchema, 
#     messenger: str| None = Header(..., alias = 'Messenger'), 
#     user_id: str | None = Header(..., alias = 'User')
# ) -> JSONResponse:
#     messenger: str = messenger.lower()

#     response: dict[str, Any] = await (
#         app.state.database.client
#             .schema(messenger)
#             .table('manual_posts')
#             .insert({
#                 'content'      : message.content,
#                 'image_url'    : message.image_url,
#                 'scheduled_at' : message.scheduled_at.isoformat(),
#                 'user_id'      : user_id
#             })
#             .execute()
#     )
    
#     post: dict[str, Any] = response.data[0]

#     if message.scheduled_at:
#         new_job = app.state.publish_scheduler.add_job(
#             publish_message_job,
#             trigger            = DateTrigger(message.scheduled_at),
#             id                 = f'{messenger}_{post.get('id')}_{user_id}',
#             args               = [post.get('id'), messenger, user_id, app],
#             misfire_grace_time = 10,
#             replace_existing   = True
#         )

#         app.state.log.debug(f'Schedule message for sending: \n id: {new_job.id}, sendingdate: {new_job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")}')
    
#     app.state.log.debug(f'Messagge add for user {user_id}')

#     return JSONResponse(
#         {
#             'post_id': post.get('id')
#         },
#         status_code = 200
#     )

# @app.post(
#     '/telegram/manual/generate', 
#     tags = ['Telegram'], 
#     summary = 'Generate post in manual posting'
# )
# async def manual_gen_post(
#     messenger: str| None = Header(..., alias = 'Messenger'), 
#     user_id: str | None = Header(..., alias = 'User')

# )->JSONResponse:

#     messenger: str = messenger.lower()

#     try:
#         request = await ai_client.generate_post(user_id,messenger,'manual_posts',1)
#     except Exception as error:
#         sentry_sdk.capture_exception(error)
#         app.state.log.error(error)
#         raise HTTPException(
#             status_code = 400,
#             detail      = type(error).__name__
#         )

#     app.state.log.debug(f' generate_post for user {user_id} status: {request}')

#     return JSONResponse(
#         {},
#         status_code = 200
#     )

# @app.post(
#     '/telegram/autoposter', 
#     tags = ['Telegram'], 
#     summary = 'Autoposter switch'
# )
# async def autoposting(
#     mode: AutoposterSwitchSchema, 
#     messenger: str| None = Header(..., alias = 'Messenger'), 
#     user_id: str | None = Header(..., alias = 'User')
# ) -> JSONResponse:

#     messenger: str = messenger.lower()

#     job = f'autoposting_job_{user_id}_user_{messenger}'

#     if not mode.isActive:
#         if app.state.autoposter_scheduler.get_job(job):
#             app.state.autoposter_scheduler.remove_job(job)
#             app.state.log.debug(f'Schedule message for auto sending deleted for user {user_id}')
#         app.state.log.debug(f'Schedule message for auto sending not found for user {user_id}')
#     else:
#         try:
#             await delivery_to_queue(app,messenger,user_id)
#         except Exception as error:
#             sentry_sdk.capture_exception(error)
#             app.state.log.error(error)
#             raise HTTPException(
#                 status_code = 400,
#                 detail      = type(error).__name__
#             )
        
#     return JSONResponse(
#         {
#             'state': mode.isActive
#         },
#         status_code = 200
#     )

# @app.get(
#     '/telegram/post/get_autoposter_state', 
#     tags = ['Telegram'], 
#     summary = 'get_autoposter_state'
# )
# async def autoposting( 
#     messenger: str| None = Header(..., alias = 'Messenger'), 
#     user_id: str | None = Header(..., alias = 'User')
# ) -> JSONResponse:

#     messenger: str = messenger.lower()

#     job = app.state.autoposter_scheduler.get_job(f'autoposting_job_{user_id}_user_{messenger}')
    
#     app.state.log.debug(f'Check state user: {user_id} state: {job}')

#     return JSONResponse(
#         {
#             'state': bool(job)
#         },
#         status_code = 200
#     )