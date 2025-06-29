from typing    import Any

class SupabaseDataUpload:
    def __init__(self, db):
        self._client = db.client

    async def upload_analytic(self,messenger:str, posts:list)-> None:
        
        post_list:list[dict[str,Any]] = []
        ids:int=[]
        
        for post in posts:
            ids.append(post.post_id)
            post_list.append(
                {
                    "post_id": post.post_id,
                    "er_score": post.er_score,
                    "sentiment_score": post.sentiment_score,
                    "final_score": post.final_score,
                    "posted_at": post.posted_at,
                    "post_channel": post.post_channel,
                }
            )
        
        resp =  await(
            self._client
            .schema(messenger)
            .table('analytic')
            .insert(post_list)
            .execute()
        )

        if not resp:
            return

        await (
            self._client
            .schema(messenger)
            .table('parsed_posts')
            .update({"analyzed": True})
            .in_("id", ids).execute()
        )

    async def upload_parsed_posts(self,messenger:str, records:dict)-> None:
        
        resp = await (
                self._client
                .schema(messenger)
                .table('parsed_posts')
                .insert(records.get('parsed_posts'))
                .execute()
            )
        
        
        for channel in records.get('channels'):

            await (
                    self._client
                    .schema(messenger)
                    .table('channels')
                    .update({"last_post": channel.get('posted_at')})
                    .eq('id',channel.get('id'))
                    .execute()
                )
