from typing import Any
import json
from typing import Literal


class PromptBuilder:
    def __init__(self, language: str, type: Literal['analytic','generation','manual'], max_posts: int = 5) -> None:
        
        if not language:
            raise ValueError('no language')

        if not type:
            raise ValueError('no resources type')

        if type == 'analytic':
            self.prompt_file_path: str = f'./resources/analytic/{language}/prompt'
            self.config_file_path: str = ''
        if type == 'generation':
            self.prompt_file_path: str = f'./resources/generation/{language}/prompt'
            self.config_file_path: str = f'./resources/generation/{language}/config.json'

        if type == 'manual':
            self.prompt_file_path: str = f'./resources/manual/{language}/prompt'
            self.config_file_path: str = ''

        language: str = language.lower()

        language = language.lower()

        self.max_posts:int = max_posts
        self.base_prompt: str
        self.config:      dict[str, Any] 

        self.__load_resources()
            
    def __load_resources(self) -> None:

        if self.prompt_file_path:
            with open(self.prompt_file_path, 'r', encoding = 'utf-8') as prompt_file:
                self.base_prompt = ''.join(prompt_file.readlines())
        
        if self.config_file_path:
            with open(self.config_file_path, 'r', encoding = 'utf-8') as config_file:
                self.config = json.load(config_file)

    def auto_prompt(self,
               posts: tuple[str], 
               prompts: tuple[str], 
               prompt_base: str, 
               tone_of_voice: str,
               words_count: int,
               use_emoji: bool, 
               use_hashtag: bool,      
    ) -> list[str]:

        if not self.base_prompt:
            raise ValueError('PromptBuilder <auto_prompt()>: \n\tbase_prompt is empty')
        
        if not self.config:
            raise ValueError('PromptBuilder <auto_prompt()>: \n\tconfig file is empty')

        prompt: str = self.base_prompt
        
        prompt_settings: dict[str, Any] = {
            'posts' : '',
            'prompts' : None,
            'prompt_base'   : self.config.get('prompt_base').get(prompt_base.lower(), 'advertising_creative'),
            'tone_of_voice' : self.config.get('ton_of_voice').get(tone_of_voice.lower(), 'serious'),

            'count_of_posts' : 0,
            'output_variation': 1,
            'words_count'    : words_count,

            'use_emoji'   : self.config.get('boolean').get(str(use_emoji).lower(), 'false'),
            'use_hashtag' : self.config.get('boolean').get(str(use_hashtag).lower(), 'false'),            
        }
        
        prompts = list(filter(None, prompts))
        
        prompt_settings['prompts'] = (
            ';'.join([f'\n\t{i + 1}. {prompts[i]}' for i in range(len(prompts))]) + ';'
            if(prompts and any(prompts))
            else 'Отсутствуют'
        )
        results = []
        
        for i in range(0, len(posts), self.max_posts):
            chunk = posts[i:i + self.max_posts]
            prompt_settings['posts'] = ''
            prompt_settings['count_of_posts'] = 0
            for j, post in enumerate(chunk, start=1):
                prompt_settings['count_of_posts'] +=1
                prompt_settings['posts'] += f'\n\t{{ "id":{post["id"]},"content":{post["content"]},"posted_at":{post["posted_at"]} }},'

            results.append(prompt.format(**prompt_settings))

        return results

    def manual_prompt(self,prompt:str)->list[str]:
        if not prompt:
            raise ValueError('PromptBuilder <manual_prompt()>: \n\tcustom_prompt is empty')

        if not self.base_prompt:
            raise ValueError('PromptBuilder <manual_prompt()>: \n\tbase_prompt is empty')

        base_prompt: str = self.base_prompt

        prompt_settings: dict[str, Any] = {
            'prompt': prompt
        }

        return base_prompt.format(**prompt_settings)

    def analytic_prompt(self,posts:list[dict[str,any]]) ->list[str]:
        if not posts:
            raise ValueError('PromptBuilder <analytic_prompt()>: \n\tposts is empty')

        if not self.base_prompt:
            raise ValueError('PromptBuilder <analytic_prompt()>: \n\tbase_prompt is empty')
        
        base_prompt: str = self.base_prompt

        results = []
        prompt_settings = {'posts':''}

        for i in range(0, len(posts), self.max_posts):
            chunk = posts[i:i + self.max_posts]
            prompt_settings['posts'] = '['

            for j, post in enumerate(chunk, start=1):
                prompt_settings['posts'] += f"""
                        {{
                        "id": {post.get('id')},
                        "channel": {post.get('channel')},
                        "content": {post.get('content')},
                        "posted_at": {post.get('posted_at')},
                        "text_urls": {post.get('text_urls')},
                        "views": {post.get('views')},
                        "forwards": {post.get('forwards')},
                        "replies_count": {post.get('replies_count')},
                        "total_reactions": {post.get('total_reactions')},
                        "stars": {post.get('stars')},
                        "reaction": {post.get('reaction')}
                        }}
                """
            
            prompt_settings['posts'] +=']'


            results.append(base_prompt.format(**prompt_settings))


        return results