from typing import List
from clients import Telegram
from datetime import datetime, timedelta,timezone

class Parser():
    
    @staticmethod
    async def parsing_posts(channels:list[str])->list:
        
        telegram = Telegram()

        records: dict[str,List] = {
            'channels':[],
            'parsed_posts':[],
        }


        for channel in channels:
            
            content = await telegram.get_content(channel_name=channel.get('name'),count_posts=100,last_post_date=channel.get('last_post') if channel.get('last_post') else str(datetime.now(timezone.utc) - timedelta(weeks=1)))

            if not content:
                continue
            
            records['channels'].append({'id':channel.get('id'),'posted_at':content[0].posted_at})

            for post in content:
                
                record:dict = {}
                record['content'] = post.content
                record['channel'] = channel.get('id')
                record['reactions_breakdown'] = [{"emoji": r.emoji, "count": r.count} for r in post.reactions_breakdown]
                record['text_urls'] = [p for p in post.url]
                record['views']= post.views
                record['forwards']= post.forwards
                record['replies_count']= post.replies_count
                record['total_reactions']= post.total_reactions
                record['stars']= post.stars
                record['posted_at']= post.posted_at

                records['parsed_posts'].append(record)

        return records
            