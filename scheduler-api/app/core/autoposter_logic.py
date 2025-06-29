from uuid     import UUID
from clients  import Ai
from datetime import datetime
from collections import Counter
from core        import LoggerService
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from clients import Telegram
from supabase import AsyncClient
from datetime import datetime, timedelta, timezone, time

class Autoposting:
    def __init__(self, db:AsyncClient, user_id:UUID, messenger:str,scheduler:AsyncIOScheduler ,max_posts:int = 10 ):
        self._max_posts   = max_posts
        self._client      = db.client
        self._user_id     = user_id
        self._messenger   = messenger
        self._analytic_id = []
        self.scheduler    = scheduler

    async def __get_options(self):
        options = await (
                    self._client
                    .schema(self._messenger)
                    .table('options')
                    .select('*')
                    .eq('user_id', self._user_id)
                    .maybe_single()
                    .execute()
                )

        return  options.data

    async def __get_posts(self):

        posts = {
                    0:[], # Monday 
                    1:[], # Tuesday  
                    2:[], # Wednesday  
                    3:[], # Thursday  
                    4:[], # Friday  
                    5:[], # Saturday  
                    6:[]  # Sunday
                }


        analytic_resp = await (
                    self._client
                    .schema(self._messenger)
                    .table('analytic')
                    .select('id,post_id,posted_at')
                    .not_.contains('user_generated',{self._user_id})
                    .gte('er_score', 5)
                    .eq('post_channel', 1)
                    .order("posted_at", desc=False)
                    .execute()
                )

        # if not resp.data:
        #     LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.__get_posts|There are no free posts in the analytics for {channels[i]}')
        #     continue
            
        for post in analytic_resp.data:
            
            day = datetime.fromisoformat(post.get('posted_at')).weekday()
            
            if len(posts[day])<4:
                posts[day].append({"id":post.get('id'),"post_id":post.get('post_id')})

        for i in range(len(posts)):
            print(f'{posts[i]}\n')


    async def __update_post(self, id:int, new_time:str):
        await (
            self._client
            .schema(self._messenger)
            .table('auto_posts')
            .update({"scheduled_at":new_time})
            .eq("id", id)
            .execute()
        )

    async def __save_posts(self,posts:list[dict]):
        request = await (
            self._client
            .schema(self._messenger)
            .table('auto_posts')
            .insert([{'parent_id':a.get('parent_id'),'user_id':self._user_id,'content':a.get('content'),'scheduled_at':a.get('scheduled_at')} for a in posts])
            .execute()
        )
        return request.data

    async def __mark_generated(self):
        
        resp = await (
                    self._client
                    .schema(self._messenger)
                    .table('analytic')
                    .select("id, user_generated")
                    .in_('id', self._analytic_id)
                    .execute()
                )       

        rows = resp.data

        to_upsert = []
        for row in rows:
            users = row.get("user_generated") or []
            
            if self._user_id not in users:
                users.append(self._user_id)
            
            to_upsert.append({
                "id": row["id"],
                "user_generated": users
            })

        await (
                self._client
                .schema(self._messenger)
                .table('analytic')
                .upsert(to_upsert, on_conflict="id")
                .execute()
        )

    async def __check_posts(self):
        posts = await (
                self._client
                .schema(self._messenger)
                .table('auto_posts')
                .select('id,content,image_url,scheduled_at')
                .eq('user_id', self._user_id)
                .eq('is_publicated', False)
                .execute()
            )
        
        return posts.data

    async def __schedule_post(self, id:int, schedule_date:str, channel_name:str, content:str, image_url:str):
        self.scheduler.add_job(
                    Telegram.post_content,
                    trigger            = DateTrigger(datetime.fromisoformat(schedule_date)),
                    id                 = str(f'job_{self._user_id}_{self._messenger}_{id}'),
                    args               = [channel_name,content,image_url],
                    misfire_grace_time = 10,
                    replace_existing   = True
                )


    async def __time_shift(self, date:str):
        posted_at = datetime.fromisoformat(date)
        today = datetime.now(timezone.utc)

        delta = (posted_at.weekday() - today.weekday() + 7) % 7
        if delta == 0:
            delta = 7

        next_date = (today + timedelta(days=delta)).date()

        H = posted_at.hour
        M = posted_at.minute
        M_rounded = 0 if M < 30 else 30

        rounded_time = time(hour=H, minute=M_rounded, second=0)

        return str(datetime.combine(next_date, rounded_time, tzinfo=timezone.utc).isoformat())

    async def start_loop(self):
        
        options = await self.__get_options()

        #TODO:Сделать проверку на дни

        await self.__get_posts()


        # if not options.get('channels_to_parse'):
        #     LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|no processing channels')
        #     return

        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|Received {len(options.get('channels_to_parse'))} {options.get('channels_to_parse')} channels')

        # publish_autoposts = await self.__check_posts()

        # count_not_publish_autoposts = len(publish_autoposts)

        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|Posts that are in the database and not posted {count_not_publish_autoposts} {[ap.get('id') for ap in publish_autoposts]}')

        # if publish_autoposts:
        #     LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|We are re-planning the posts that are in the database {count_not_publish_autoposts}')
        #     for auto_posts in publish_autoposts:

        #         if datetime.fromisoformat(auto_posts.get('scheduled_at')) < datetime.now(timezone.utc):
        #             auto_posts['scheduled_at'] = await self.__time_shift(auto_posts.get('scheduled_at',''))
        #             LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|New time {auto_posts['scheduled_at']} for an old post id:{auto_posts.get('id')}')
        #             await self.__update_post(auto_posts.get('id'),auto_posts['scheduled_at'])

        #         await self.__schedule_post(auto_posts.get('id'), auto_posts.get('scheduled_at',''), options.get('maintainer_channel'), auto_posts.get('content'), auto_posts.get('image_url'))

        # if count_not_publish_autoposts >= self._max_posts:
        #     LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|autoposting {count_not_publish_autoposts} channels out of {self._max_posts}')
        #     return
        
        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|autoposting {count_not_publish_autoposts} channels out of {self._max_posts}')

        # posts = await self.__get_posts(options.get('channels_to_parse'), (self._max_posts-count_not_publish_autoposts))

        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|According to analytics {self._analytic_id} found posts {len(posts)} {[p.get('id') for p in posts]}')

        # if not posts:
        #     return

        # data = {
        #     "posts":posts,
        #     "prompts":options.get('prompts'),
        #     "prompt_base":options.get('prompt_base'),
        #     "tone_of_voice":options.get('tov'),
        #     "words_count":options.get('words_count'),
        #     "use_hashtag":options.get('use_hashtag'),
        #     "use_emoji":options.get('use_emoji'),
        #     "lang":"ru" 
        # }

        # ai = Ai()

        # request_posts = await ai.get_auto_post(**data)

        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|Generated posts received {len(request_posts)}')

        # if not request_posts:
        #     return

        # posts = []

        # for post in request_posts:

        #     posts.append({
        #                 'parent_id':post.parent_id,
        #                 'user_id':self._user_id,
        #                 'content':post.content,
        #                 'scheduled_at': await self.__time_shift(post.scheduled_at)
        #                 } )

        # request  = await self.__save_posts(posts)
        
        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|Saved posts {[req.get('id') for req in request]}')
        
        # await self.__mark_generated()
        
        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|We noted in analytics {self._analytic_id} that the user generated the post')

        # for req_post in request:
        #     await self.__schedule_post(req_post.get('id'),req_post.get('scheduled_at'), options.get('maintainer_channel'), req_post.get('content'), req_post.get('image_url'))

        # LoggerService.debug(f'user-id: {self._user_id}|core.autoposter_logic.start_loop|scheduled posts {[{"id":req.get('id'),"time":req.get('scheduled_at')}  for req in request]}')