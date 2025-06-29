from interface.telegram_service_pb2 import ContentData,ReactionsBreakdown

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest,GetCustomEmojiDocumentsRequest
from telethon.tl.types import MessageEntityTextUrl,ReactionPaid,ReactionCustomEmoji, DocumentAttributeCustomEmoji
from telethon.sessions import StringSession

from datetime import datetime
from os                import environ

class TelegramSession:
    def __init__(self) -> None:
        self.client: TelegramClient = None
        self.telegram_session       = StringSession(environ.get('TELEGRAM_SESSION')) 
        self.telegram_api           = int(environ.get('TELEGRAM_API_ID'))
        self.telegram_hash          = str(environ.get('TELEGRAM_API_HASH'))

        self.model       = 'iPhone 13 Pro Max'
        self.system      = '14.8.1'
        self.app         = '8.4'
        self.lang        = 'en'
        self.system_lang = 'en-US'
        
        self.__client()
        
    def __client(self)-> None: 
        self.client = TelegramClient(
                self.telegram_session, 
                self.telegram_api,
                self.telegram_hash,

                device_model=self.model,
                system_version=self.system,
                app_version=self.app,
                lang_code=self.lang,
                system_lang_code=self.system_lang
            )
            
    async def start(self) -> None:
        await self.client.start()
        
    async def stop(self) -> None:
        await self.client.disconnect()

    async def send(self, channel: str, content: str, image_url: str | None = None) -> None:
        
        if bool(image_url):
            
            await self.client.send_file(
                channel,
                image_url,
                caption      = content,
                link_preview = False,
                parse_mode   = 'markdown',
            )
        
        else:
            await self.client.send_message(
                channel,
                content,
                link_preview = False,
                parse_mode   = 'markdown',
            )

    async def parsing_channel(self, channel: str, parsing_count: int, date: str | None = None) -> list[dict]:

        message_list:list[ContentData] = []

        history = await self.client(
                    GetHistoryRequest(
                        peer=channel,
                        offset_id=0,
                        offset_date= None,
                        add_offset=0,
                        limit= parsing_count,
                        max_id=0,
                        min_id=0,
                        hash=0
                    )
                )

        emoji_cache = {}

        for msg in history.messages:

            if (date and (msg.date <= datetime.fromisoformat(date))):
                continue
                

            message = ContentData()

            content = msg.message or ''
            
            if not content.strip():
                continue  

            stars = 0
            summ = 0

            for r in getattr(msg.reactions, 'results', []) or []:

                if isinstance(r.reaction, ReactionPaid):
                    stars=r.count
                    continue
                
                if isinstance(r.reaction, ReactionCustomEmoji):
                    doc_id = r.reaction.document_id
                    
                    if doc_id not in emoji_cache:
                        docs =  await self.client(GetCustomEmojiDocumentsRequest(
                            document_id=[doc_id]
                        ))
                        if docs:
                            doc = docs[0]

                            alt = None
                            for attr in doc.attributes:
                                if isinstance(attr, DocumentAttributeCustomEmoji):
                                    alt = attr.alt
                                    break
                            emoji_cache[doc_id] = alt or f"<unknown:{doc_id}>"
                        else:
                            emoji_cache[doc_id] = f"<missing:{doc_id}>"

                    key = emoji_cache[doc_id]

                    summ = summ + r.count
                    message.reactions_breakdown.append(ReactionsBreakdown(emoji=key,count=r.count))
                    continue
                
                try:
                    summ = summ + r.count
                    message.reactions_breakdown.append(ReactionsBreakdown(emoji=r.reaction.emoticon,count=r.count))
                except Exception:
                    continue
            
            if msg.entities:
                for e in msg.entities:
                    if isinstance(e, MessageEntityTextUrl):
                        message.url.append(e.url)

            message.id = 0
            message.content = content
            message.views = msg.views or 0
            message.forwards = msg.forwards or 0
            message.replies_count = msg.replies.replies if msg.replies else 0
            message.total_reactions = summ
            message.stars = stars
            message.posted_at = str(msg.date)

            message_list.append(message)

        return message_list

telegram_client = TelegramSession()