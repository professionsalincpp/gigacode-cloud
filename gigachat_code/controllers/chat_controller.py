"""Контроллер для чата."""
from typing import Optional
from ..models.config import ConfigManager, GigaChatConfig
from ..models.message import ChatSession
from ..core.code_assistant import CodeAssistant
from ..views.terminal_view import TerminalView


class ChatController:
    """Контроллер для управления чатом."""
    
    def __init__(self, view: TerminalView, config_manager: ConfigManager):
        self.view = view
        self.config_manager = config_manager
        self.assistant: Optional[CodeAssistant] = None
    
    def initialize(self) -> bool:
        """Инициализировать контроллер чата."""
        config = self.config_manager.load()
        
        if not config.is_valid():
            self.view.print_warning("API не настроен. Выполните настройку через команду /setup")
            return False
        
        self.assistant = CodeAssistant()
        if not self.assistant.initialize(config):
            self.view.print_error("Не удалось инициализировать API клиент")
            return False
        
        # Создаем первую сессию
        self.assistant.create_new_session()
        
        return True
    
    def process_command(self, command: str) -> bool:
        """
        Обработать команду пользователя.
        
        Args:
            command: Команда пользователя (начинается с /)
        
        Returns:
            True если программа должна продолжить работу, False для выхода
        """
        cmd = command.lower().strip()
        
        if cmd in ['/quit', '/exit']:
            self.view.print_info("До свидания!")
            return False
        
        elif cmd == '/help':
            self.view.show_help()
        
        elif cmd == '/setup':
            from .setup_controller import SetupController
            setup = SetupController(self.view, self.config_manager)
            setup.run_setup()
            
            # Переинициализируем после настройки
            self.initialize()
        
        elif cmd == '/config':
            config = self.config_manager.load()
            self.view.show_config(config.to_dict())
        
        elif cmd == '/clear':
            if self.assistant:
                self.assistant.clear_current_session()
                self.view.print_success("История чата очищена")
            else:
                self.view.print_warning("Чат не активен")
        
        elif cmd == '/new':
            if self.assistant:
                self.assistant.create_new_session()
                self.view.print_success("Начат новый чат")
            else:
                self.view.print_warning("Чат не активен")
        
        elif cmd == '/history':
            if self.assistant:
                session = self.assistant.get_current_session()
                if session and session.messages:
                    messages = [msg.to_dict() for msg in session.messages]
                    self.view.print_history(messages)
                else:
                    self.view.print_info("История пуста")
            else:
                self.view.print_warning("Чат не активен")
        
        elif cmd.startswith('/analyze '):
            file_path = command[len('/analyze '):].strip()
            if self.assistant:
                self._handle_file_analysis(file_path, 'analyze')
            else:
                self.view.print_warning("Чат не активен")
        
        elif cmd.startswith('/explain '):
            code = command[len('/explain '):].strip()
            if self.assistant and code:
                self._handle_code_explanation(code)
            else:
                self.view.print_warning("Укажите код для объяснения")
        
        elif cmd.startswith('/refactor '):
            code = command[len('/refactor '):].strip()
            if self.assistant and code:
                self._handle_code_refactor(code)
            else:
                self.view.print_warning("Укажите код для рефакторинга")
        
        elif cmd.startswith('/test '):
            code = command[len('/test '):].strip()
            if self.assistant and code:
                self._handle_test_generation(code)
            else:
                self.view.print_warning("Укажите код для генерации тестов")
        
        else:
            self.view.print_warning(f"Неизвестная команда: {command}")
            self.view.print_info("Введите /help для списка доступных команд")
        
        return True
    
    def send_message(self, message: str):
        """Отправить сообщение в чат."""
        if not self.assistant:
            self.view.print_error("Чат не инициализирован. Выполните /setup для настройки API")
            return
        
        # Показываем сообщение пользователя
        self.view.print_user_message(message)
        
        # Показываем индикатор набора
        with self.view.show_typing_indicator():
            response = self.assistant.send_message(message)
        
        # Обрабатываем ответ
        if response.success:
            self.view.print_assistant_message(response.content)
        else:
            self.view.print_error(f"Ошибка: {response.error}")
    
    def _handle_file_analysis(self, file_path: str, task: str = 'analyze'):
        """Обработать анализ файла."""
        self.view.print_info(f"Анализирую файл: {file_path}")
        
        with self.view.show_typing_indicator():
            response = self.assistant.analyze_file(file_path, task)
        
        if response.success:
            self.view.print_assistant_message(response.content)
        else:
            self.view.print_error(f"Ошибка анализа: {response.error}")
    
    def _handle_code_explanation(self, code: str):
        """Обработать объяснение кода."""
        self.view.print_info("Объясняю код...")
        
        with self.view.show_typing_indicator():
            response = self.assistant.explain_code(code)
        
        if response.success:
            self.view.print_assistant_message(response.content)
        else:
            self.view.print_error(f"Ошибка: {response.error}")
    
    def _handle_code_refactor(self, code: str):
        """Обработать рефакторинг кода."""
        self.view.print_info("Анализирую возможности рефакторинга...")
        
        with self.view.show_typing_indicator():
            response = self.assistant.refactor_code(code)
        
        if response.success:
            self.view.print_assistant_message(response.content)
        else:
            self.view.print_error(f"Ошибка: {response.error}")
    
    def _handle_test_generation(self, code: str):
        """Обработать генерацию тестов."""
        self.view.print_info("Генерирую тесты...")
        
        with self.view.show_typing_indicator():
            response = self.assistant.generate_tests(code)
        
        if response.success:
            self.view.print_assistant_message(response.content)
        else:
            self.view.print_error(f"Ошибка: {response.error}")
    
    def run_chat_loop(self):
        """Запустить основной цикл чата."""
        if not self.initialize():
            return
        
        self.view.print_success("Чат активен. Введите /help для списка команд или напишите сообщение.")
        self.view.print_info("-" * 50)
        
        while True:
            try:
                user_input = self.view.get_input("> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith('/'):
                    if not self.process_command(user_input):
                        break
                else:
                    self.send_message(user_input)
                    
            except KeyboardInterrupt:
                self.view.print_info("\nДля выхода используйте команду /exit")
            except EOFError:
                break
