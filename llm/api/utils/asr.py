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

    async def transcribe(self, file_path: str):
        token = self.__get_token()
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field('file', f, filename=file_path, content_type='audio/type')
                async with session.post(self.__transcribe_url, headers=headers, data=form) as response:
                    response_json = await response.json()
                    return response_json