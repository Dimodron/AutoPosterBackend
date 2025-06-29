from fastapi                       import FastAPI
from apscheduler.triggers.interval import IntervalTrigger

class StartupTasks:

    @staticmethod
    async def initialization(app: FastAPI):
        ...

        # app.state.parse_scheduler.add_job(
        #         Parser().parse_channels_for_user,
        #         trigger            = IntervalTrigger(minutes = 15),
        #         id                 = str(f'parsing_job_{user_id}_user'),
        #         args               = [app, user_id, messenger_type],
        #         misfire_grace_time = 10,
        #         replace_existing   = True
        #     )
        
        # app.state.parse_scheduler.add_job(
        #         Parser().parse_channels_for_user,
        #         trigger            = IntervalTrigger(minutes = 15),
        #         id                 = str(f'parsing_job_{user_id}_user'),
        #         args               = [app, user_id, messenger_type],
        #         misfire_grace_time = 10,
        #         replace_existing   = True
        #     )

@staticmethod
async def changing(app: FastAPI, user:str, interval: int,):
    job_id: str = f'parsing_job_{user}_user'
    job = app.state.parse_scheduler.get_job(job_id)

    new_job = app.state.parse_scheduler.add_job(
            Parser().parse_channels_for_user,
            trigger            = IntervalTrigger(minutes = interval),
            id                 = job_id,
            args               = job.args,
            misfire_grace_time = 10,
            replace_existing   = True
        )
    
    app.state.log.info(f'Update schedule options: \n id: {new_job.id}, interval_min: {new_job.trigger.interval.total_seconds()/60}, old_interval_min: {job.trigger.interval.total_seconds()/60}')

@staticmethod
async def show(app: FastAPI):
    ...