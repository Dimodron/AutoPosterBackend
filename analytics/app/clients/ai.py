from os import environ
from grpc.aio import insecure_channel
from interface.ai_service_pb2 import  AnalyticPostsRequest
from interface.ai_service_pb2_grpc import AiServiceStub

class Ai:
    
    def __init__(self) -> None:
        self.endpoint: str = environ.get('AI_PROCESSOR_API_GRPC_URL')

    async def analytic_posts(self, request_posts:list, lang:str):

        async with insecure_channel(self.endpoint) as channel:
            
            stub = AiServiceStub(channel)
            
            request = AnalyticPostsRequest(
                posts = request_posts,
                lang = lang,
            )
            
            response = await stub.AnalyticPosts(request)

            if response.status_code != 200:
                raise SystemError(f'ai-processor | {response.detail}')

            return list(response.data)

