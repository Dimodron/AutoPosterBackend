
class SupabaseDataLoad:
    def __init__(self, db):
        
        self._client = db.client

    async def get_channels(self,messenger:str):
        channels = await (
                    self._client
                    .schema(messenger)
                    .table('channels')
                    .select('*')
                    .execute()
                )
        
        return channels.data

    async def get_data_for_analysis(self,messenger:str):
        
        posts = await (
                self._client
                .schema(messenger)
                .table("parsed_posts")
                .select("*")
                .eq("analyzed", False)
                .execute()
            )
        
        request_data = []

        for post in posts.data:
            request_data.append({
                "id":post.get('id'),
                "channel":post.get('channel'),
                "content":post.get('content'),
                "posted_at":post.get('posted_at'),
                "text_urls":post.get('text_urls'),
                "views":post.get('views'),
                "forwards":post.get('forwards'),
                "replies_count":post.get('replies_count'),
                "total_reactions":post.get('total_reactions'),
                "stars":post.get('stars'),
                "reaction":post.get('reaction'),
            })

        return request_data