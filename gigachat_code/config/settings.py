"""
Конфигурация и управление секретами API
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict


class Config:
    """Класс для управления конфигурацией приложения"""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".gigachat_code"
    CONFIG_FILE = "config.json"
    
    def __init__(self):
        self.config_dir = self.DEFAULT_CONFIG_DIR
        self.config_file_path = self.config_dir / self.CONFIG_FILE
        self._config: Dict = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Загрузка конфигурации из файла"""
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                self._config = {}
        else:
            self._config = {}
    
    def _save_config(self) -> None:
        """Сохранение конфигурации в файл"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    @property
    def api_key(self) -> Optional[str]:
        """Получение API ключа"""
        return self._config.get('api_key') or os.environ.get('GIGACHAT_API_KEY')
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        """Установка API ключа"""
        self._config['api_key'] = value
        self._save_config()
    
    @property
    def api_url(self) -> str:
        """Получение URL API"""
        return self._config.get('api_url', 'https://gigachat.devices.sberbank.ru/api/v2/chat/completions')
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        """Установка URL API"""
        self._config['api_url'] = value
        self._save_config()
    
    @property
    def model(self) -> str:
        """Получение модели по умолчанию"""
        return self._config.get('model', 'GigaChat')
    
    @model.setter
    def model(self, value: str) -> None:
        """Установка модели по умолчанию"""
        self._config['model'] = value
        self._save_config()
    
    @property
    def max_tokens(self) -> int:
        """Получение максимального количества токенов"""
        return self._config.get('max_tokens', 4096)
    
    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Установка максимального количества токенов"""
        self._config['max_tokens'] = value
        self._save_config()
    
    @property
    def temperature(self) -> float:
        """Получение температуры генерации"""
        return self._config.get('temperature', 0.7)
    
    @temperature.setter
    def temperature(self, value: float) -> None:
        """Установка температуры генерации"""
        self._config['temperature'] = value
        self._save_config()
    
    def is_configured(self) -> bool:
        """Проверка наличия конфигурации"""
        return bool(self.api_key)
    
    def clear_config(self) -> None:
        """Очистка всей конфигурации"""
        self._config = {}
        if self.config_file_path.exists():
            self.config_file_path.unlink()
    
    def get_all(self) -> Dict:
        """Получение всей конфигурации"""
        return self._config.copy()
