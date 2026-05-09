"""Модели данных для GigaChat Code Assistant."""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class Message:
    """Сообщение в чате."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class ChatSession:
    """Сессия чата с историей сообщений."""
    id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    title: str = "Новый чат"
    
    def add_message(self, role: str, content: str) -> Message:
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message
    
    def get_context_messages(self, max_messages: int = 10) -> List[dict]:
        """Получить последние сообщения для контекста API."""
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [msg.to_dict() for msg in recent]
    
    def clear_history(self):
        """Очистить историю сообщений."""
        self.messages = []
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages]
        }


@dataclass
class APIResponse:
    """Ответ от GigaChat API."""
    success: bool
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    error: Optional[str] = None
    
    @classmethod
    def from_json(cls, json_data: dict) -> 'APIResponse':
        if 'error' in json_data:
            return cls(
                success=False,
                content="",
                model="unknown",
                error=json_data.get('error', {}).get('message', 'Неизвестная ошибка')
            )
        
        choices = json_data.get('choices', [])
        content = ""
        if choices and len(choices) > 0:
            content = choices[0].get('message', {}).get('content', '')
        
        return cls(
            success=True,
            content=content,
            model=json_data.get('model', 'unknown'),
            usage=json_data.get('usage', {})
        )


@dataclass
class FileContext:
    """Контекст файла для анализа."""
    path: str
    content: str
    language: str = ""
    
    def get_language(self) -> str:
        """Определить язык программирования по расширению."""
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
        import os
        ext = os.path.splitext(self.path)[1].lower()
        return ext_map.get(ext, 'text')
