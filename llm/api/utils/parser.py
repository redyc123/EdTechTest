from uuid import UUID
import aiohttp
from config import config


async def convert_file_async(file: bytes, file_name: str | None) -> str | None:
    url = f'{config.docling_url}/v1/convert/file/async'
    headers = {
        'accept': 'application/json',
        'X-Api-Key': config.docling_serve_api_key,
    }
    data = {
        'ocr_engine': 'easyocr',
        'pdf_backend': 'dlparse_v4',
        'from_formats': 'pdf',
        'force_ocr': 'false',
        'image_export_mode': 'embedded',
        'ocr_lang': 'en',
        'table_mode': 'fast',
        'abort_on_error': 'false',
        'to_formats': 'md',
        'do_ocr': 'true',
    }

    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        for key, value in data.items():
            form.add_field(key, value)
        form.add_field('files', file, filename=file_name, content_type='application/pdf')

        async with session.post(url, headers=headers, data=form) as response:
            resp_json = await response.json()
            return resp_json.get("task_id")


async def get_result_task_convert(task_id: str | UUID) -> tuple[str, str | None] | None:
    url = f"{config.docling_url}/v1/result/{task_id}"
    task_id = str(task_id)
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'application/json',
            'X-Api-Key': config.docling_serve_api_key,
        }
        async with session.get(url, headers=headers) as response:
            resp_json = await response.json()
            if resp_json.get("status", "pending") != "success":
                return None
            document = resp_json.get("document", {})
            return document.get("md_content"), document.get("filename", None)
