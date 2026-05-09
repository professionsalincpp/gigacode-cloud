"""Клиент для работы с GigaChat API."""
import requests
import base64
import warnings
from typing import List, Optional
from ..models.config import GigaChatConfig
from ..models.message import APIResponse

# Отключаем предупреждения о самоподписанных SSL сертификатах
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3 = requests.packages.urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GigaChatClient:
    """Клиент для взаимодействия с GigaChat API."""
    
    def __init__(self, config: GigaChatConfig):
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires: Optional[float] = None
    
    def _get_auth_header(self) -> str:
        """Получить заголовок авторизации."""
        credentials = f"{self.config.client_id}:{self.config.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _get_access_token(self) -> str:
        """Получить access token для API."""
        # Если токен еще действителен, возвращаем его
        if self._access_token and self._token_expires:
            import time
            if time.time() < self._token_expires - 60:  # 60 секунд запаса
                return self._access_token
        
        headers = {
            "Authorization": self._get_auth_header(),
            "RqUID": "00000000-0000-0000-0000-000000000000",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "scope": "GIGACHAT_API_PERS"
        }
        
        try:
            response = requests.post(
                self.config.auth_url,
                headers=headers,
                data=data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 401:
                raise RuntimeError(
                    "Ошибка аутентификации (401): Неверные Client ID или Client Secret.\n"
                    "Проверьте ваши учетные данные в настройках.\n"
                    "Запустите: python -m gigachat_code.cli setup"
                )
            
            if response.status_code == 403:
                raise RuntimeError(
                    "Доступ запрещен (403): Возможно, ваш аккаунт не активирован для GigaChat API.\n"
                    "Убедитесь, что:\n"
                    "  1. Вы получили credentials в SberBank Developer Portal\n"
                    "  2. Ваш проект имеет доступ к GigaChat API\n"
                    "  3. Квоты API не исчерпаны"
                )
            
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get('access_token')
            
            if not self._access_token:
                raise ValueError("Не удалось получить access token из ответа API")
            
            # Сохраняем время истечения токена (если есть в ответе)
            expires_in = token_data.get('expires_in', 3600)
            import time
            self._token_expires = time.time() + expires_in
            
            return self._access_token
            
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "Ошибка подключения к серверу аутентификации.\n"
                "Проверьте интернет-соединение и URL сервера."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                "Превышено время ожидания от сервера аутентификации.\n"
                "Попробуйте позже."
            )
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "403" in error_msg:
                raise
            raise RuntimeError(f"Ошибка аутентификации: {error_msg}")
    
    def send_message(self, messages: List[dict], temperature: float = 0.7) -> APIResponse:
        """
        Отправить сообщение в GigaChat API.
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            temperature: Параметр креативности (0.0 - 1.0)
        
        Returns:
            APIResponse с ответом от модели
        """
        try:
            access_token = self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=120,
                verify=False
            )
            
            if response.status_code == 401:
                # Токен мог истечь, пробуем получить новый
                self._access_token = None
                access_token = self._get_access_token()
                headers["Authorization"] = f"Bearer {access_token}"
                response = requests.post(
                    self.config.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120,
                    verify=False
                )
            
            if response.status_code == 403:
                return APIResponse(
                    success=False,
                    content="",
                    model=self.config.model,
                    error=(
                        "Доступ запрещен (403): Проверьте права доступа к API.\n"
                        "Убедитесь, что ваш проект имеет доступ к GigaChat API."
                    )
                )
            
            response.raise_for_status()
            
            return APIResponse.from_json(response.json())
            
        except requests.exceptions.Timeout:
            return APIResponse(
                success=False,
                content="",
                model=self.config.model,
                error="Превышено время ожидания ответа от API"
            )
        except requests.exceptions.ConnectionError:
            return APIResponse(
                success=False,
                content="",
                model=self.config.model,
                error="Ошибка подключения к API"
            )
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP ошибка: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                if 'error' in error_detail:
                    error_msg += f" - {error_detail['error'].get('message', '')}"
            except:
                pass
            return APIResponse(
                success=False,
                content="",
                model=self.config.model,
                error=error_msg
            )
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                model=self.config.model,
                error=f"Неизвестная ошибка: {str(e)}"
            )
    
    def chat(self, user_message: str, conversation_history: Optional[List[dict]] = None) -> APIResponse:
        """
        Отправить сообщение в чате с учетом истории.
        
        Args:
            user_message: Сообщение пользователя
            conversation_history: История предыдущих сообщений
        
        Returns:
            APIResponse с ответом от модели
        """
        messages = []
        
        # Добавляем системный промпт для роли ассистента по коду
        system_prompt = {
            "role": "system",
            "content": (
                "Ты опытный разработчик и помощник по программированию. "
                "Твоя задача - помогать пользователям с написанием, анализом, объяснением и рефакторингом кода. "
                "Отвечай подробно, но структурированно. "
                "Используй блоки кода с указанием языка для примеров кода. "
                "Объясняй сложные концепции простым языком. "
                "Предлагай лучшие практики и оптимизации где это уместно."
            )
        }
        messages.append(system_prompt)
        
        # Добавляем историю если есть
        if conversation_history:
            messages.extend(conversation_history)
        
        # Добавляем текущее сообщение
        messages.append({"role": "user", "content": user_message})
        
        return self.send_message(messages)
    
    def analyze_file(self, file_content: str, file_path: str, task: str = "analyze") -> APIResponse:
        """
        Анализировать файл с кодом.
        
        Args:
            file_content: Содержимое файла
            file_path: Путь к файлу
            task: Тип задачи (analyze, explain, refactor, test)
        
        Returns:
            APIResponse с результатом анализа
        """
        task_prompts = {
            "analyze": "Проанализируй этот код. Оцени его качество, найди потенциальные проблемы и предложи улучшения.",
            "explain": "Объясни подробно, что делает этот код, как он работает.",
            "refactor": "Предложи рефакторинг этого кода для улучшения читаемости, производительности и поддерживаемости.",
            "test": "Напиши comprehensive тесты для этого кода."
        }
        
        prompt = f"{task_prompts.get(task, 'Проанализируй код.')}\n\nФайл: {file_path}\n\nКод:\n```{file_path.split('.')[-1]}\n{file_content}\n```"
        
        return self.chat(prompt)
