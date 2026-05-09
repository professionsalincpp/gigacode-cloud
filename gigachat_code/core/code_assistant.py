"""Основной класс бизнес-логики для работы с кодом."""
import os
from pathlib import Path
from typing import Optional, List
from ..models.config import GigaChatConfig, ConfigManager
from ..models.message import ChatSession, APIResponse, FileContext
from ..core.api_client import GigaChatClient


class FileSystemTool:
    """Инструменты для работы с файловой системой."""
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """Прочитать содержимое файла."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            if not path.is_file():
                return None
            
            # Проверка размера файла (не более 100KB)
            max_size = 100 * 1024
            if path.stat().st_size > max_size:
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError, Exception):
            return None
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Проверить существование файла."""
        return Path(file_path).exists() and Path(file_path).is_file()
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """Получить информацию о файле."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            ext_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.go': 'Go',
                '.rs': 'Rust',
                '.rb': 'Ruby',
                '.php': 'PHP',
                '.html': 'HTML',
                '.css': 'CSS',
                '.json': 'JSON',
                '.yaml': 'YAML',
                '.yml': 'YAML',
                '.md': 'Markdown',
                '.sh': 'Bash',
                '.txt': 'Text',
            }
            
            ext = path.suffix.lower()
            language = ext_map.get(ext, 'Unknown')
            
            return {
                'name': path.name,
                'path': str(path.absolute()),
                'size': path.stat().st_size,
                'extension': ext,
                'language': language
            }
        except Exception:
            return None


class CodeAssistant:
    """Основной класс бизнес-логики ассистента."""
    
    def __init__(self, config: Optional[GigaChatConfig] = None):
        self.config = config
        self.client: Optional[GigaChatClient] = None
        self.current_session: Optional[ChatSession] = None
        self.sessions: List[ChatSession] = []
        self.fs_tool = FileSystemTool()
        
        if config and config.is_valid():
            self.client = GigaChatClient(config)
    
    def initialize(self, config: GigaChatConfig) -> bool:
        """Инициализировать ассистента с конфигурацией."""
        self.config = config
        
        if not config.is_valid():
            return False
        
        self.client = GigaChatClient(config)
        return True
    
    def create_new_session(self, title: str = "Новый чат") -> ChatSession:
        """Создать новую сессию чата."""
        import uuid
        session = ChatSession(
            id=str(uuid.uuid4()),
            title=title
        )
        self.sessions.append(session)
        self.current_session = session
        return session
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Получить текущую сессию."""
        if not self.current_session and self.sessions:
            self.current_session = self.sessions[-1]
        return self.current_session
    
    def switch_session(self, session_id: str) -> bool:
        """Переключиться на другую сессию."""
        for session in self.sessions:
            if session.id == session_id:
                self.current_session = session
                return True
        return False
    
    def clear_current_session(self):
        """Очистить историю текущей сессии."""
        session = self.get_current_session()
        if session:
            session.clear_history()
    
    def send_message(self, message: str) -> APIResponse:
        """
        Отправить сообщение и получить ответ.
        
        Args:
            message: Сообщение пользователя
        
        Returns:
            APIResponse с ответом от модели
        """
        if not self.client:
            return APIResponse(
                success=False,
                content="",
                model="unknown",
                error="API клиент не инициализирован. Выполните настройку через /setup"
            )
        
        session = self.get_current_session()
        if not session:
            session = self.create_new_session()
        
        # Добавляем сообщение пользователя в историю
        session.add_message("user", message)
        
        # Получаем контекст истории
        history = session.get_context_messages(max_messages=10)
        # Удаляем последнее сообщение (только что добавленное), т.к. client.chat сам его добавит
        history = history[:-1]
        
        # Отправляем запрос к API
        response = self.client.chat(message, conversation_history=history)
        
        if response.success:
            # Добавляем ответ ассистента в историю
            session.add_message("assistant", response.content)
        
        return response
    
    def analyze_file(self, file_path: str, task: str = "analyze") -> APIResponse:
        """
        Анализировать файл.
        
        Args:
            file_path: Путь к файлу
            task: Тип задачи (analyze, explain, refactor, test)
        
        Returns:
            APIResponse с результатом анализа
        """
        if not self.client:
            return APIResponse(
                success=False,
                content="",
                model="unknown",
                error="API клиент не инициализирован"
            )
        
        content = self.fs_tool.read_file(file_path)
        if not content:
            return APIResponse(
                success=False,
                content="",
                model="unknown",
                error=f"Не удалось прочитать файл: {file_path}. Возможно файл слишком большой или недоступен."
            )
        
        return self.client.analyze_file(content, file_path, task)
    
    def explain_code(self, code: str) -> APIResponse:
        """Объяснить код."""
        prompt = f"Объясни подробно, что делает этот код, как он работает, какие паттерны используются:\n\n```python\n{code}\n```"
        return self.send_message(prompt)
    
    def refactor_code(self, code: str) -> APIResponse:
        """Предложить рефакторинг кода."""
        prompt = f"Предложи рефакторинг этого кода для улучшения читаемости, производительности и поддерживаемости. Покажи исходный и улучшенный вариант:\n\n```python\n{code}\n```"
        return self.send_message(prompt)
    
    def generate_tests(self, code: str) -> APIResponse:
        """Сгенерировать тесты для кода."""
        prompt = f"Напиши comprehensive тесты для этого кода, используя pytest. Включи тесты для граничных случаев:\n\n```python\n{code}\n```"
        return self.send_message(prompt)
