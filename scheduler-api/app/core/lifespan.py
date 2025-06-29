from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Database
from core import LoggerService, StartupTasks

parse_scheduler             = AsyncIOScheduler()
analytic_scheduler          = AsyncIOScheduler()
manual_posting_scheduler    = AsyncIOScheduler()
auto_posting_scheduler      = AsyncIOScheduler()
auto_post_task_scheduler    = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.database = await Database.serve()
   
    app.state.parse_scheduler                  = parse_scheduler
    app.state.analytic_scheduler               = analytic_scheduler
    app.state.manual_posting_scheduler         = manual_posting_scheduler
    app.state.auto_posting_scheduler           = auto_posting_scheduler
    app.state.auto_post_task_scheduler         = auto_post_task_scheduler

    parse_scheduler.start()
    analytic_scheduler.start()
    manual_posting_scheduler.start()
    auto_posting_scheduler.start()
    auto_post_task_scheduler.start()

    # try:
    #     await StartupTasks.initialization(app)
    # except Exception as error:
    #     LoggerService.error(error, exc=error)

    yield  

    parse_scheduler.shutdown()
    analytic_scheduler.shutdown()
    manual_posting_scheduler.shutdown()
    auto_posting_scheduler.shutdown()
