import aiohttp
import uuid
from typing import Optional, Dict, Any, List


class LLMServiceClient:
    def __init__(self, base_url: str, access_token: Optional[str] = None):
        """
        Инициализация клиента для работы с LLM API
        
        Args:
            base_url: Базовый URL API сервера
            access_token: Токен доступа (опционально, можно установить позже)
        """
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.headers = {}
        self._update_headers()
    
    def _update_headers(self):
        """Обновление заголовков с токеном авторизации"""
        self.headers = {
            'Accept': 'application/json',
        }
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
    
    def set_access_token(self, access_token: str):
        """Установка токена доступа"""
        self.access_token = access_token
        self._update_headers()
    
    async def generate_token(self, secret_token: str) -> Dict[str, Any]:
        """
        Генерация токена доступа
        
        Args:
            secret_token: Секретный токен для генерации access token
            
        Returns:
            Ответ сервера с сгенерированным токеном
        """
        url = f"{self.base_url}/generate-token"
        
        data = {
            "secret_token": secret_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                return await response.json()
    
    async def text_completion(
        self,
        dialog_id: uuid.UUID,
        query: str = "",
        picture: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Обработка текстового запроса
        
        Args:
            dialog_id: UUID диалога
            query: Текстовый запрос (по умолчанию пустая строка)
            picture: Изображение в бинарном формате (опционально)
            
        Returns:
            Ответ от языковой модели в формате AIMessage
        """
        url = f"{self.base_url}/v1/chat/completion/text"
        
        # Параметры запроса
        params = {
            "dialog_id": str(dialog_id),
            "query": query
        }
        
        # Подготовка multipart данных
        data = aiohttp.FormData()
        
        # Добавляем файл с изображением, если есть
        if picture:
            data.add_field(
                'picture',
                picture,
                filename='picture.jpg',
                content_type='image/jpeg'
            )
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, params=params, data=data) as response:
                response.raise_for_status()
                return await response.json()
    
    async def audio_completion(
        self,
        dialog_id: uuid.UUID,
        audio_data: bytes,
        picture: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Обработка аудиозапроса
        
        Args:
            dialog_id: UUID диалога
            audio_data: Аудиофайл в бинарном формате
            picture: Изображение в бинарном формате (опционально)
            
        Returns:
            Ответ от языковой модели
        """
        url = f"{self.base_url}/v1/chat/completion/audio"
        
        # Параметры запроса
        params = {
            "dialog_id": str(dialog_id)
        }
        
        # Подготовка multipart данных
        data = aiohttp.FormData()
        
        # Добавляем аудиофайл
        data.add_field(
            'audio',
            audio_data,
            filename='audio.mp3',
            content_type='audio/mpeg'
        )
        
        # Добавляем файл с изображением, если есть
        if picture:
            data.add_field(
                'picture',
                picture,
                filename='picture.jpg',
                content_type='image/jpeg'
            )
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, params=params, data=data) as response:
                response.raise_for_status()
                return await response.json()
    
    async def clear_chat(self, dialog_id: uuid.UUID) -> Dict[str, Any]:
        """
        Очистка истории чата
        
        Args:
            dialog_id: UUID диалога для очистки
            
        Returns:
            Ответ сервера
        """
        url = f"{self.base_url}/v1/chat/clear"
        
        params = {
            "dialog_id": str(dialog_id)
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    async def parse_document(
        self,
        dialog_id: uuid.UUID,
        file_data: bytes,
        filename: str = "document.pdf"
    ) -> Dict[str, Any]:
        """
        Парсинг и добавление документа в векторное хранилище
        
        Args:
            dialog_id: UUID диалога
            file_data: Файл документа в бинарном формате
            filename: Имя файла (опционально)
            
        Returns:
            Ответ с идентификаторами добавленных документов
        """
        url = f"{self.base_url}/v1/parse/document"
        
        params = {
            "dialog_id": str(dialog_id)
        }
        
        # Определяем content type на основе расширения файла
        content_type = self._get_content_type(filename)
        
        # Подготовка multipart данных
        data = aiohttp.FormData()
        data.add_field(
            'file',
            file_data,
            filename=filename,
            content_type=content_type
        )
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, params=params, data=data) as response:
                response.raise_for_status()
                return await response.json()
    
    async def remove_documents(
        self,
        dialog_id: uuid.UUID,
        document_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Удаление документов из векторного хранилища
        
        Args:
            dialog_id: UUID диалога
            document_ids: Список идентификаторов документов для удаления
            
        Returns:
            Ответ сервера
        """
        url = f"{self.base_url}/v1/remove/documents"
        
        data = {
            "dialog_id": str(dialog_id),
            "ids": document_ids
        }
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                return await response.json()
    
    def _get_content_type(self, filename: str) -> str:
        """
        Определение content type по расширению файла
        
        Args:
            filename: Имя файла
            
        Returns:
            Content type для файла
        """
        extension = filename.lower().split('.')[-1]
        
        content_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    async def check_connection(self) -> bool:
        """
        Проверка подключения к серверу
        
        Returns:
            True если сервер доступен, False в противном случае
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, timeout=5) as response:
                    return response.status < 500
        except:
            return False
