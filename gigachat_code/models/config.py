"""Конфигурация приложения."""
import os
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class GigaChatConfig:
    """Конфигурация GigaChat API."""
    client_id: str = ""
    client_secret: str = ""
    model: str = "GigaChat"
    api_url: str = "https://gigachat.devices.sberbank.ru/api/v2/chat/completions"
    auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    def is_valid(self) -> bool:
        """Проверить, настроены ли учетные данные."""
        return bool(self.client_id and self.client_secret)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GigaChatConfig':
        return cls(**data)


class ConfigManager:
    """Менеджер конфигурации."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Сохраняем в домашней директории пользователя
            home = Path.home()
            self.config_path = home / ".gigachat_code" / "config.json"
    
    def load(self) -> GigaChatConfig:
        """Загрузить конфигурацию из файла."""
        if not self.config_path.exists():
            return GigaChatConfig()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return GigaChatConfig.from_dict(data)
        except (json.JSONDecodeError, Exception):
            return GigaChatConfig()
    
    def save(self, config: GigaChatConfig) -> bool:
        """Сохранить конфигурацию в файл."""
        try:
            # Создаем директорию если не существует
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Устанавливаем безопасные права доступа (только владелец)
            os.chmod(self.config_path, 0o600)
            
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Удалить конфигурацию."""
        try:
            if self.config_path.exists():
                self.config_path.unlink()
            return True
        except Exception:
            return False
