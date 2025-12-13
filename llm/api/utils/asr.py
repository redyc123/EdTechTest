import uuid
import aiohttp
from config import config

class ASR:
    __transcribe_url = config.asr_url.removesuffix("/") + "/transcribe"
    __get_token_url = config.asr_url.removesuffix("/") + "/generate-token"
    
    
    async def __get_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.__get_token_url, 
                json={"secret_token": config.secret_token}
            ) as response:
                response_json = await response.json()
                return response_json

    async def transcribe(self, file: bytes):
        token = await self.__get_token()
        print(token)
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token.get('access_token')}",
        }

        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field('file', file, filename=f"{uuid.uuid4()}", content_type='audio/type')
            async with session.post(self.__transcribe_url, headers=headers, data=form) as response:
                response_json = await response.json()
                return response_json