"""
Модели данных для GigaChat Code
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class MessageRole(Enum):
    """Роли сообщений в чате"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Сообщение в чате"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        """Конвертация в словарь для API"""
        return {
            "role": self.role.value,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Создание из словаря"""
        return cls(
            role=MessageRole(data.get('role', 'user')),
            content=data.get('content', '')
        )


@dataclass
class ChatSession:
    """Сессия чата с историей сообщений"""
    id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    title: Optional[str] = None
    
    def add_message(self, role: MessageRole, content: str) -> Message:
        """Добавление сообщения в историю"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Получение сообщений в формате для API"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear_history(self) -> None:
        """Очистка истории сообщений"""
        self.messages = []
        self.updated_at = datetime.now()
    
    def get_last_message(self, role: Optional[MessageRole] = None) -> Optional[Message]:
        """Получение последнего сообщения (опционально по роли)"""
        if not self.messages:
            return None
        if role is None:
            return self.messages[-1]
        for msg in reversed(self.messages):
            if msg.role == role:
                return msg
        return None


@dataclass
class APIResponse:
    """Ответ от API"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    raw_response: Optional[Dict] = None
    usage: Optional[Dict] = None
    
    @classmethod
    def success_response(cls, content: str, raw_response: Optional[Dict] = None) -> 'APIResponse':
        """Создание успешного ответа"""
        usage = None
        if raw_response and 'usage' in raw_response:
            usage = raw_response['usage']
        return cls(success=True, content=content, raw_response=raw_response, usage=usage)
    
    @classmethod
    def error_response(cls, error: str, raw_response: Optional[Dict] = None) -> 'APIResponse':
        """Создание ответа с ошибкой"""
        return cls(success=False, error=error, raw_response=raw_response)


@dataclass
class FileContext:
    """Контекст файла для работы с кодом"""
    path: str
    content: str
    language: Optional[str] = None
    
    def to_prompt_snippet(self) -> str:
        """Конвертация в сниппет для промпта"""
        return f"```{self.language or ''}\n{self.content}\n```"
    
    @classmethod
    def from_file(cls, path: str) -> 'FileContext':
        """Чтение файла с диска"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Определение языка по расширению
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sh': 'bash',
        }
        ext = '.' + path.split('.')[-1] if '.' in path else ''
        language = ext_map.get(ext.lower())
        
        return cls(path=path, content=content, language=language)
