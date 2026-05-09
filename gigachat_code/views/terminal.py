"""
Представления (Views) для терминального интерфейса с использованием Rich
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, List


class TerminalView:
    """Класс для отображения информации в терминале с использованием Rich"""
    
    def __init__(self):
        self.console = Console()
    
    def clear(self) -> None:
        """Очистка экрана"""
        self.console.clear()
    
    def print_welcome(self) -> None:
        """Приветственное сообщение"""
        welcome_text = Text()
        welcome_text.append("GigaChat Code", style="bold magenta")
        welcome_text.append(" - ваш AI помощник для работы с кодом\n", style="dim")
        welcome_text.append("Аналог Claude Code на базе GigaChat API", style="italic cyan")
        
        panel = Panel(
            welcome_text,
            title="[bold green]Добро пожаловать[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def print_error(self, message: str) -> None:
        """Вывод сообщения об ошибке"""
        panel = Panel(
            f"[bold red]Ошибка:[/bold red] {message}",
            border_style="red",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_success(self, message: str) -> None:
        """Вывод сообщения об успехе"""
        panel = Panel(
            f"[bold green]✓[/bold green] {message}",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_info(self, message: str) -> None:
        """Вывод информационной информации"""
        panel = Panel(
            f"[bold blue]ℹ[/bold blue] {message}",
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_warning(self, message: str) -> None:
        """Вывод предупреждения"""
        panel = Panel(
            f"[bold yellow]⚠[/bold yellow] {message}",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_code(self, code: str, language: str = "python") -> None:
        """Вывод кода с подсветкой синтаксиса"""
        syntax = Syntax(
            code,
            language,
            theme="monokai",
            line_numbers=True,
            word_wrap=False
        )
        self.console.print(syntax)
    
    def print_markdown(self, markdown_text: str) -> None:
        """Вывод текста в формате Markdown"""
        md = Markdown(markdown_text)
        self.console.print(md)
    
    def print_response(self, content: str) -> None:
        """Вывод ответа от ассистента"""
        # Попытка определить и красиво вывести код
        if "```" in content:
            parts = content.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Это блок кода
                    # Извлечение языка если указан
                    lines = part.strip().split('\n')
                    if lines and not lines[0].startswith(('import', 'def ', 'class ', 'return', 'if ', 'for ', 'while ')):
                        language = lines[0].strip()
                        code = '\n'.join(lines[1:])
                    else:
                        language = "text"
                        code = part.strip()
                    
                    if code.strip():
                        self.print_code(code, language)
                else:  # Это обычный текст
                    if part.strip():
                        self.print_markdown(part)
        else:
            self.print_markdown(content)
    
    def show_loading(self, message: str = "Загрузка...") -> Spinner:
        """Создание индикатора загрузки"""
        return Spinner("dots", text=message, style="cyan")
    
    def live_loading(self, message: str = "Обработка..."):
        """Контекстный менеджер для анимации загрузки"""
        return Live(
            Spinner("dots", text=message, style="cyan"),
            console=self.console,
            transient=True
        )
    
    def prompt_input(self, message: str, default: str = "", password: bool = False) -> str:
        """Запрос ввода от пользователя"""
        return Prompt.ask(message, default=default, password=password)
    
    def prompt_confirm(self, message: str, default: bool = True) -> bool:
        """Запрос подтверждения"""
        return Confirm.ask(message, default=default)
    
    def prompt_choice(self, message: str, choices: List[str]) -> str:
        """Выбор из списка опций"""
        return Prompt.ask(message, choices=choices)
    
    def show_config(self, config_data: dict) -> None:
        """Отображение текущей конфигурации"""
        table = Table(title="Текущая конфигурация", show_header=True, header_style="bold magenta")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        for key, value in config_data.items():
            # Скрытие чувствительных данных
            if 'key' in key.lower() and value:
                value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            table.add_row(key, str(value))
        
        self.console.print(table)
    
    def show_help(self) -> None:
        """Отображение справки"""
        help_text = """
# Доступные команды

## Основные команды
- **/help** - Показать эту справку
- **/exit**, **/quit** - Выход из программы
- **/clear**, **/cls** - Очистить историю чата
- **/new** - Начать новую сессию

## Настройки
- **/config** - Показать текущую конфигурацию
- **/setup** - Настроить API ключ и параметры

## Работа с кодом
- **/analyze <file>** - Анализировать файл
- **/explain** - Объяснить последний ответ
- **/refactor** - Рефакторить код
- **/write <description>** - Написать код по описанию

## Системные команды
- **/history** - Показать историю сессии
- **/tokens** - Показать статистику использования токенов

Просто введите ваш вопрос или задачу, и я помогу вам с кодом!
"""
        self.print_markdown(help_text)
    
    def show_session_info(self, session_id: str, message_count: int) -> None:
        """Отображение информации о сессии"""
        info = Text()
        info.append("Сессия: ", style="dim")
        info.append(f"{session_id[:8]}...", style="cyan")
        info.append(" | Сообщений: ", style="dim")
        info.append(str(message_count), style="green")
        self.console.print(info)
    
    def print_usage_stats(self, usage: dict) -> None:
        """Отображение статистики использования токенов"""
        if not usage:
            return
        
        table = Table(title="Статистика использования токенов", show_header=False)
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", style="green")
        
        if 'prompt_tokens' in usage:
            table.add_row("Входные токены", str(usage['prompt_tokens']))
        if 'completion_tokens' in usage:
            table.add_row("Выходные токены", str(usage['completion_tokens']))
        if 'total_tokens' in usage:
            table.add_row("Всего токенов", str(usage['total_tokens']))
        
        self.console.print(table)
