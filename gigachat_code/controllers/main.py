"""
Контроллеры для управления приложением
"""

from ..config import Config
from ..core import CodeAssistant
from ..views import TerminalView


class SetupController:
    """Контроллер для настройки приложения"""
    
    def __init__(self, config: Config, view: TerminalView):
        self.config = config
        self.view = view
    
    def run_setup(self) -> bool:
        """Запуск процесса настройки"""
        self.view.clear()
        self.view.print_welcome()
        
        self.view.print_info("Настройка GigaChat Code")
        self.view.console.print()
        
        # Проверка существующей конфигурации
        if self.config.is_configured():
            self.view.print_warning("Конфигурация уже существует!")
            if not self.view.prompt_confirm("Перенастроить?", default=False):
                return True
        
        try:
            # Запрос API ключа
            self.view.console.print("[bold]Шаг 1/4: API ключ[/bold]")
            api_key = self.view.prompt_input(
                "Введите ваш GigaChat API ключ",
                password=True
            )
            
            if not api_key or len(api_key.strip()) < 10:
                self.view.print_error("Некорректный API ключ")
                return False
            
            self.config.api_key = api_key.strip()
            self.view.print_success("API ключ сохранён")
            
            # Запрос URL API (опционально)
            self.view.console.print()
            self.view.console.print("[bold]Шаг 2/4: URL API[/bold]")
            default_url = self.config.api_url
            custom_url = self.view.prompt_input(
                f"URL API (оставьте пустым для значения по умолчанию: {default_url})",
                default=""
            )
            
            if custom_url.strip():
                self.config.api_url = custom_url.strip()
                self.view.print_success(f"URL установлен: {custom_url}")
            else:
                self.view.print_info(f"Используется URL по умолчанию: {default_url}")
            
            # Запрос модели
            self.view.console.print()
            self.view.console.print("[bold]Шаг 3/4: Модель[/bold]")
            default_model = self.config.model
            model = self.view.prompt_input(
                f"Название модели (по умолчанию: {default_model})",
                default=default_model
            )
            
            if model.strip():
                self.config.model = model.strip()
                self.view.print_success(f"Модель установлена: {model}")
            
            # Запрос максимального количества токенов
            self.view.console.print()
            self.view.console.print("[bold]Шаг 4/4: Параметры генерации[/bold]")
            max_tokens = self.view.prompt_input(
                f"Максимум токенов (по умолчанию: {self.config.max_tokens})",
                default=str(self.config.max_tokens)
            )
            
            try:
                self.config.max_tokens = int(max_tokens)
                self.view.print_success(f"Максимум токенов: {max_tokens}")
            except ValueError:
                self.view.print_warning(f"Некорректное значение, используется: {self.config.max_tokens}")
            
            # Температура
            temperature = self.view.prompt_input(
                f"Температура (0.0-1.0, по умолчанию: {self.config.temperature})",
                default=str(self.config.temperature)
            )
            
            try:
                temp = float(temperature)
                if 0.0 <= temp <= 2.0:
                    self.config.temperature = temp
                    self.view.print_success(f"Температура: {temp}")
                else:
                    self.view.print_warning("Температура должна быть от 0.0 до 2.0")
            except ValueError:
                self.view.print_warning(f"Некорректное значение, используется: {self.config.temperature}")
            
            self.view.console.print()
            self.view.print_success("Настройка завершена успешно!")
            self.view.show_config(self.config.get_all())
            
            return True
            
        except KeyboardInterrupt:
            self.view.console.print()
            self.view.print_warning("Настройка прервана")
            return False


class ChatController:
    """Контроллер для управления чатом"""
    
    def __init__(self, config: Config, view: TerminalView):
        self.config = config
        self.view = view
        self.assistant: CodeAssistant = None
        self._init_assistant()
    
    def _init_assistant(self) -> None:
        """Инициализация ассистента"""
        if self.config.is_configured():
            try:
                self.assistant = CodeAssistant(self.config)
            except ValueError as e:
                self.view.print_error(str(e))
                self.assistant = None
        else:
            self.assistant = None
    
    def reload_assistant(self) -> bool:
        """Перезагрузка ассистента"""
        try:
            self.assistant = CodeAssistant(self.config)
            return True
        except ValueError as e:
            self.view.print_error(str(e))
            self.assistant = None
            return False
    
    def process_command(self, command: str) -> bool:
        """Обработка команд пользователя"""
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in ['/exit', '/quit', '/q']:
            return False
        
        elif cmd in ['/help', '/h', '?']:
            self.view.show_help()
        
        elif cmd in ['/clear', '/cls']:
            if self.assistant:
                self.assistant.clear_history()
                self.view.print_success("История очищена")
            else:
                self.view.print_error("Ассистент не инициализирован")
        
        elif cmd == '/new':
            if self.assistant:
                self.assistant.new_session()
                self.view.print_success("Новая сессия создана")
            else:
                self.view.print_error("Ассистент не инициализирован")
        
        elif cmd == '/config':
            self.view.show_config(self.config.get_all())
        
        elif cmd == '/setup':
            setup_ctrl = SetupController(self.config, self.view)
            setup_ctrl.run_setup()
            self.reload_assistant()
        
        elif cmd == '/analyze':
            if not args:
                self.view.print_error("Укажите путь к файлу: /analyze <file>")
            elif self.assistant:
                with self.view.live_loading("Анализ файла..."):
                    response = self.assistant.analyze_file(args)
                if response.success:
                    self.view.print_response(response.content)
                    if response.usage:
                        self.view.print_usage_stats(response.usage)
                else:
                    self.view.print_error(response.error)
            else:
                self.view.print_error("Ассистент не инициализирован. Выполните /setup")
        
        elif cmd == '/history':
            if self.assistant:
                history = self.assistant.get_session_history()
                if history:
                    self.view.print_info(f"В истории {len(history)} сообщений")
                    for msg in history[-5:]:  # Последние 5 сообщений
                        role = "Вы" if msg.role.value == "user" else "Ассистент"
                        preview = msg.content[:100].replace('\n', ' ')
                        self.view.console.print(f"  [cyan]{role}:[/cyan] {preview}...")
                else:
                    self.view.print_info("История пуста")
            else:
                self.view.print_error("Ассистент не инициализирован")
        
        elif cmd == '/tokens':
            if self.assistant and self.assistant.current_session:
                # Получаем последнее сообщение для статистики
                last_msg = self.assistant.current_session.get_last_message()
                if last_msg and hasattr(last_msg, 'usage'):
                    self.view.print_usage_stats({})
                else:
                    self.view.print_info("Статистика пока недоступна")
            else:
                self.view.print_info("Нет активной сессии")
        
        elif cmd == '/session':
            if self.assistant and self.assistant.current_session:
                session = self.assistant.current_session
                self.view.show_session_info(session.id, len(session.messages))
            else:
                self.view.print_info("Нет активной сессии")
        
        else:
            self.view.print_warning(f"Неизвестная команда: {cmd}. Введите /help для справки.")
        
        return True
    
    def send_message(self, message: str) -> bool:
        """Отправка сообщения ассистенту"""
        if not self.assistant:
            self.view.print_error("Ассистент не инициализирован. Выполните /setup")
            return True
        
        with self.view.live_loading("Думаю..."):
            response = self.assistant.send_message(message)
        
        if response.success:
            self.view.print_response(response.content)
            if response.usage:
                self.view.print_usage_stats(response.usage)
        else:
            self.view.print_error(response.error)
        
        return True
    
    def run(self) -> None:
        """Запуск интерактивного режима чата"""
        self.view.clear()
        self.view.print_welcome()
        
        # Проверка конфигурации
        if not self.config.is_configured():
            self.view.print_warning("Приложение не настроено")
            if self.view.prompt_confirm("Выполнить настройку сейчас?"):
                setup_ctrl = SetupController(self.config, self.view)
                if setup_ctrl.run_setup():
                    self.reload_assistant()
            else:
                self.view.print_info("Вы можете выполнить настройку позже командой /setup")
        
        # Основной цикл чата
        running = True
        while running:
            try:
                # Отображение информации о сессии
                if self.assistant and self.assistant.current_session:
                    session = self.assistant.current_session
                    self.view.show_session_info(session.id, len(session.messages))
                
                # Запрос ввода
                user_input = self.view.prompt_input("Вы")
                
                if not user_input.strip():
                    continue
                
                # Обработка команд
                if user_input.startswith('/'):
                    running = self.process_command(user_input)
                else:
                    running = self.send_message(user_input)
                
                self.view.console.print()  # Пустая строка для разделения
                
            except KeyboardInterrupt:
                self.view.console.print()
                if self.view.prompt_confirm("Выйти из программы?", default=False):
                    running = False
                else:
                    self.view.console.print()
                    continue
            except EOFError:
                break
        
        self.view.print_info("До свидания!")
