import asyncio
import json
from google import genai
from os import environ
from core.logs import LoggerService
import asyncio

class Generator:
    def __init__(self,process_id:str =''):
        self.client = genai.Client(api_key=environ['GEMINI_API_KEY'])
        self.model  = environ['GEMINI_MODEL']
        self.max_attempts = 5
        self.process_id= ''

    def __ai_request(self, prompt: str) -> str:
        try:
            resp = self.client.models.generate_content(
                model    = self.model,
                contents = prompt
            ).text
        except Exception as error:
            LoggerService.error(type(error).__name__,exc=error)
            return "```json[]```"

        return resp.text if hasattr(resp, 'text') else str(resp)

    def __json_preparation(self, generated_posts: str) -> list[dict[str, str]]:
        
        for attempt in range(1, self.max_attempts + 1):
            
            try:
                return json.loads(generated_posts.removeprefix('```json').rstrip('` \n'))
            except Exception as error:
                LoggerService.warning(f"{self.process_id}|Attempt {attempt} failed: {error}")
                generated_posts = (
                    "⚠️ Твоя задача: исправь JSON ниже.\n"
                    "- Не добавляй никаких пояснений, комментариев или кода.\n"
                    "- Сохрани тот же формат, просто сделай JSON валидным.\n"
                    "- Верни только JSON, без markdown и других вставок.\n\n"
                    f"Error:  {error}"
                    f"Сообщение:\n{generated_posts}"
                )

                LoggerService.debug()

                generated_posts = self.__ai_request(generated_posts)
        
        return []

    async def __generate(self, prompt: str, prompt_number:int) -> list[dict[str, str]]:
        
        ai_response = await asyncio.to_thread(self.__ai_request,prompt)

        LoggerService.debug(f'{self.process_id}| Received a response from gemini as per the prompt: {prompt_number} \n {ai_response}\n')

        json_resp = await asyncio.to_thread(self.__json_preparation,ai_response)

        LoggerService.debug(f'{self.process_id}| reading the prompt num: {prompt_number} and validate request \n{json_resp}')

        return json_resp

    async def start(self, prompts: list[str],delay:int = 0) -> list[list[dict[str, str]]]:
            
        """
        Starts asynchronous generation for a list of prompts.

        :param prompts: list[str]
            A list of string prompts to process.
        :param delay: int, optional
            Delay in seconds before launching each subsequent task.
            If set to 0 (default), all tasks start concurrently.
            This delay helps avoid exceeding per-second request rate limits.

        """
        async def _with_delay(prompt: str, wait: int, prompt_number: int):
            if wait:
                await asyncio.sleep(wait)

            return await self.__generate(prompt,prompt_number)
        
        tasks = [
            _with_delay(prompt, idx * delay,idx + 1)
            for idx, prompt in enumerate(prompts)
        ]

        return await asyncio.gather(*tasks)
