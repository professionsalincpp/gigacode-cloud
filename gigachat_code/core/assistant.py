"""
Ядро приложения - работа с GigaChat API
"""

import json
import requests
from typing import List, Optional, Generator, Dict, Any
from pathlib import Path

from ..config import Config
from ..models import Message, MessageRole, ChatSession, APIResponse, FileContext


class GigaChatClient:
    """Клиент для работы с GigaChat API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Проверка конфигурации"""
        if not self.config.api_key:
            raise ValueError(
                "API key not configured. Please run 'gigachat-code setup' first "
                "or set GIGACHAT_API_KEY environment variable."
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков для запросов"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json"
        }
    
    def _prepare_request_body(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Подготовка тела запроса для API"""
        
        # Формирование сообщений с системным промптом
        api_messages = []
        if system_prompt:
            api_messages.append({
                "role": "system",
                "content": system_prompt
            })
        api_messages.extend(messages)
        
        # Параметры запроса
        body = {
            "model": kwargs.get('model', self.config.model),
            "messages": api_messages,
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature),
        }
        
        # Добавление дополнительных параметров если указаны
        if 'top_p' in kwargs:
            body['top_p'] = kwargs['top_p']
        if 'stream' in kwargs:
            body['stream'] = kwargs['stream']
        
        return body
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """Отправка запроса к API и получение ответа"""
        
        try:
            body = self._prepare_request_body(messages, system_prompt, **kwargs)
            
            response = self.session.post(
                self.config.api_url,
                headers=self._get_headers(),
                json=body,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Извлечение ответа из структуры GigaChat API
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0].get('message', {}).get('content', '')
                return APIResponse.success_response(content, data)
            else:
                return APIResponse.error_response("No response from API", data)
                
        except requests.exceptions.Timeout:
            return APIResponse.error_response("Request timed out")
        except requests.exceptions.ConnectionError as e:
            return APIResponse.error_response(f"Connection error: {str(e)}")
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {str(e)}"
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data}"
            except:
                pass
            return APIResponse.error_response(error_msg)
        except json.JSONDecodeError as e:
            return APIResponse.error_response(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            return APIResponse.error_response(f"Unexpected error: {str(e)}")
    
    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Потоковая отправка запроса к API (генератор)"""
        
        kwargs['stream'] = True
        
        try:
            body = self._prepare_request_body(messages, system_prompt, **kwargs)
            
            with self.session.post(
                self.config.api_url,
                headers=self._get_headers(),
                json=body,
                timeout=60,
                stream=True
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        # Обработка SSE формата
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                                
        except requests.exceptions.RequestException as e:
            yield f"\n[Error: {str(e)}]"
    
    def send_message(
        self,
        session: ChatSession,
        user_message: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> APIResponse:
        """Отправка сообщения в контексте сессии"""
        
        # Добавляем сообщение пользователя в историю
        session.add_message(MessageRole.USER, user_message)
        
        # Получаем историю для API
        messages = session.get_messages_for_api()
        
        # Отправляем запрос
        response = self.chat(messages, system_prompt, **kwargs)
        
        # Если успешно, добавляем ответ ассистента в историю
        if response.success and response.content:
            session.add_message(MessageRole.ASSISTANT, response.content)
        
        return response


class FileSystemTool:
    """Инструменты для работы с файловой системой"""
    
    @staticmethod
    def read_file(path: str, max_size: int = 100000) -> FileContext:
        """Чтение файла"""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not file_path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        file_size = file_path.stat().st_size
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {max_size})")
        
        return FileContext.from_file(str(file_path))
    
    @staticmethod
    def write_file(path: str, content: str) -> bool:
        """Запись файла"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*") -> List[str]:
        """Список файлов в директории"""
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        return [str(f) for f in dir_path.glob(pattern) if f.is_file()]
    
    @staticmethod
    def search_files(directory: str, pattern: str, recursive: bool = True) -> List[str]:
        """Поиск файлов по паттерну"""
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if recursive:
            return [str(f) for f in dir_path.rglob(pattern) if f.is_file()]
        else:
            return [str(f) for f in dir_path.glob(pattern) if f.is_file()]


class CodeAssistant:
    """Основной класс помощника для работы с кодом"""
    
    SYSTEM_PROMPT = """Ты опытный разработчик и помощник по коду. Твоя задача - помогать пользователю 
с написанием, анализом, рефакторингом и отладкой кода. 

Твои возможности:
- Писать новый код на различных языках программирования
- Анализировать существующий код и находить проблемы
- Рефакторить код для улучшения читаемости и производительности
- Объяснять сложные концепции простым языком
- Помогать с отладкой и поиском ошибок
- Предлагать лучшие практики и паттерны проектирования

При работе с кодом:
- Всегда пиши чистый, читаемый и поддерживаемый код
- Добавляй комментарии где это необходимо
- Следуй best practices для каждого языка
- Предлагай оптимизации когда это уместно
- Будь точен и конкретен в ответах

Форматируй код в блоках с указанием языка для подсветки синтаксиса."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = GigaChatClient(config)
        self.current_session: Optional[ChatSession] = None
        self.file_system = FileSystemTool()
        self._init_session()
    
    def _init_session(self) -> None:
        """Инициализация новой сессии"""
        import uuid
        self.current_session = ChatSession(id=str(uuid.uuid4()))
    
    def new_session(self) -> ChatSession:
        """Создание новой сессии"""
        self._init_session()
        return self.current_session
    
    def send_message(self, message: str, include_file_context: bool = True) -> APIResponse:
        """Отправка сообщения и получение ответа"""
        
        # Подготовка системного промпта
        system_prompt = self.SYSTEM_PROMPT
        
        # Добавление контекста файлов если запрошено
        if include_file_context and self.current_session:
            # Можно добавить логику для автоматического добавления контекста
            pass
        
        return self.client.send_message(
            self.current_session,
            message,
            system_prompt=system_prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    def analyze_file(self, file_path: str) -> APIResponse:
        """Анализ файла"""
        try:
            file_context = self.file_system.read_file(file_path)
            message = f"Проанализируй этот файл и дай рекомендации по улучшению:\n\n{file_context.to_prompt_snippet()}"
            return self.send_message(message)
        except Exception as e:
            return APIResponse.error_response(str(e))
    
    def explain_code(self, code: str, language: Optional[str] = None) -> APIResponse:
        """Объяснение кода"""
        lang_tag = language or ""
        message = f"Объясни подробно что делает этот код:\n\n```{lang_tag}\n{code}\n```"
        return self.send_message(message)
    
    def refactor_code(self, code: str, instructions: str, language: Optional[str] = None) -> APIResponse:
        """Рефакторинг кода"""
        lang_tag = language or ""
        message = f"Выполни рефакторинг этого кода согласно инструкции: {instructions}\n\nКод:\n```{lang_tag}\n{code}\n```"
        return self.send_message(message)
    
    def write_code(self, description: str, language: str) -> APIResponse:
        """Написание кода по описанию"""
        message = f"Напиши код на {language} который: {description}"
        return self.send_message(message)
    
    def get_session_history(self) -> List[Message]:
        """Получение истории текущей сессии"""
        if self.current_session:
            return self.current_session.messages
        return []
    
    def clear_history(self) -> None:
        """Очистка истории сессии"""
        if self.current_session:
            self.current_session.clear_history()
