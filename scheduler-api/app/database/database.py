from supabase import AsyncClient, create_async_client
from os import environ

class Database:
    def __init__(self, client: AsyncClient) -> None:
        self.__client = client

    @classmethod
    async def serve(cls) -> "Database":
        client   = await create_async_client(environ["SUPABASE_ENDPOINT"], environ["SUPABASE_KEY"])
        return cls(client)

    @property
    def client(self) -> AsyncClient:
        return self.__client
