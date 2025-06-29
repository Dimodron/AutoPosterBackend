from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from apscheduler.triggers.date import DateTrigger
from models import (
    ParserSettingsSchema, MessageScheduleSchema,
    MessageAddSchema, AutoposterSwitchSchema
)
from core.jobs import update_user_job, publish_message_job, delivery_to_queue

router = APIRouter(prefix="/autoposter", tags=["autoposter"])

@app.post(
    '/telegram/parse/timeout', 
    tags = ['Telegram'], 
    summary = 'Change parsing timeout'
)
async def telegram_parse_timeout(
    parser_settings: ParserSettingsSchema, 
    user_id: str | None = Header(..., alias = 'User')
) -> JSONResponse:
    interval: int = parser_settings.parsing_timeout

    try:
        await update_user_job(
            app      = app,
            user     = user_id,
            interval = interval
        )

    except Exception as error:
        sentry_sdk.capture_exception(error)
        app.state.log.error('An error occured while updating parser job',exc=error)
        raise HTTPException(
            status_code = 500,
            detail      = f'An error occured while updating parser job Error: {error}'
        )

    return JSONResponse(
        {
           'message': f'Parsing timeout updated to {interval} minutes for user {user_id}'
        },
        status_code = 200
    )

@router.post("/manual/schedule", summary="Schedule message for sending")
async def telegram_post_schedule(
    message: MessageScheduleSchema,
    messenger: str = Header(..., alias="Messenger"),
    user_id:   str = Header(..., alias="User")
) -> JSONResponse:
    messenger = messenger.lower()
    db = router.app.state.database.client
    # проверяем существование поста
    post = (await db.schema(messenger)
                  .table("manual_posts")
                  .select("is_publicated")
                  .eq("id", message.post_id)
                  .eq("user_id", user_id)
                  .maybe_single()
                  .execute())
    if not post:
        raise HTTPException(404, "POST_NOT_FOUND")
    if post.data.get("is_publicated"):
        raise HTTPException(400, "POST_ALREADY_PUBLICATED")

    router.app.state.publish_scheduler.add_job(
        publish_message_job,
        trigger=DateTrigger(message.scheduled_at),
        id=f"{messenger}_{message.post_id}_{user_id}",
        args=[message.post_id, messenger, user_id, router.app],
        misfire_grace_time=10,
        replace_existing=True
    )
    return JSONResponse(
        {"message": f"Scheduled at {message.scheduled_at} for {user_id}"},
        status_code=200
    )