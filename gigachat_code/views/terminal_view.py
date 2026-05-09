"""View слой для терминального интерфейса с использованием Rich."""
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner


class TerminalView:
    """Представление для терминального интерфейса."""
    
    def __init__(self):
        self.console = Console()
        self.width = self.console.width
    
    def print_welcome(self):
        """Показать приветственное сообщение."""
        welcome_text = """
# 🤖 GigaChat Code Assistant

Ваш персональный помощник для работы с кодом на базе GigaChat API.

**Доступные команды:**
- `/help` - Показать справку
- `/setup` - Настроить API ключи
- `/config` - Показать текущую конфигурацию
- `/analyze <файл>` - Анализировать файл
- `/explain <код>` - Объяснить код
- `/refactor <код>` - Предложить рефакторинг
- `/clear` - Очистить историю чата
- `/new` - Начать новый чат
- `/history` - Показать историю сообщений
- `/quit` или `/exit` - Выйти из программы
        """
        panel = Panel(
            Markdown(welcome_text),
            title="[bold blue]GigaChat Code[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def print_error(self, message: str):
        """Показать сообщение об ошибке."""
        panel = Panel(
            f"[red]❌ {message}[/red]",
            border_style="red",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_success(self, message: str):
        """Показать сообщение об успехе."""
        panel = Panel(
            f"[green]✅ {message}[/green]",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_info(self, message: str):
        """Показать информационное сообщение."""
        self.console.print(f"[cyan]ℹ️  {message}[/cyan]")
    
    def print_warning(self, message: str):
        """Показать предупреждение."""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")
    
    def print_user_message(self, content: str):
        """Показать сообщение пользователя."""
        panel = Panel(
            content,
            title="[bold green]👤 Вы[/bold green]",
            title_align="left",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_assistant_message(self, content: str):
        """Показать ответ ассистента с поддержкой markdown и подсветкой кода."""
        # Проверяем есть ли блоки кода
        if "```" in content:
            parts = content.split("```")
            output_parts = []
            
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Блок кода
                    # Определяем язык (первая строка до пробела или новой строки)
                    lines = part.strip().split('\n', 1)
                    lang = lines[0].strip() if lines else ""
                    code = lines[1] if len(lines) > 1 else ""
                    
                    if code.strip():
                        syntax = Syntax(code.strip(), lang or "text", theme="monokai", line_numbers=True)
                        output_parts.append(syntax)
                    else:
                        output_parts.append(Text(part.strip()))
                else:  # Обычный текст
                    if part.strip():
                        output_parts.append(Markdown(part.strip()))
            
            panel = Panel(
                *output_parts,
                title="[bold blue]🤖 GigaChat[/bold blue]",
                title_align="left",
                border_style="blue",
                padding=(0, 1)
            )
        else:
            panel = Panel(
                Markdown(content),
                title="[bold blue]🤖 GigaChat[/bold blue]",
                title_align="left",
                border_style="blue",
                padding=(0, 1)
            )
        
        self.console.print(panel)
    
    def get_input(self, prompt_text: str = "> ", password: bool = False) -> str:
        """Получить ввод от пользователя."""
        return Prompt.ask(prompt_text, password=password)
    
    def confirm(self, message: str) -> bool:
        """Запросить подтверждение."""
        return Confirm.ask(message)
    
    def show_setup_wizard(self) -> dict:
        """Показать мастер настройки API."""
        self.console.print()
        panel = Panel(
            "[bold]Настройка GigaChat API[/bold]\n\n"
            "Для работы вам понадобятся [italic]Client ID[/italic] и [italic]Client Secret[/italic].\n\n"
            "[yellow]Где получить:[/yellow]\n"
            "1. Зайдите в портал разработчика Sber (https://developers.sber.ru/)\n"
            "2. Создайте новый проект или выберите существующий\n"
            "3. Перейдите в раздел 'Продукты' → 'GigaChat'\n"
            "4. Подключите продукт к проекту\n"
            "5. Скопируйте Client ID и Client Secret\n",
            title="🔑 Мастер настройки",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(panel)
        
        self.console.print()
        
        # Запрашиваем только Client ID и Client Secret
        client_id = self.get_input("[bold]Client ID[/bold]: ", password=False)
        client_secret = self.get_input("[bold]Client Secret[/bold]: ", password=True)
        
        return {
            "client_id": client_id.strip(),
            "client_secret": client_secret.strip()
        }
    
    def show_config(self, config: dict):
        """Показать текущую конфигурацию."""
        table = Table(title="📋 Текущая конфигурация", show_header=True, header_style="bold cyan")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        is_configured = bool(config.get('client_id') and config.get('client_secret'))
        status = "[green]✅ Настроено[/green]" if is_configured else "[red]❌ Не настроено[/red]"
        
        table.add_row("Статус", status)
        
        if is_configured:
            # Показываем только часть ключа для безопасности
            client_id = config.get('client_id', '')
            masked_id = f"{client_id[:4]}...{client_id[-4:]}" if len(client_id) > 8 else "***"
            table.add_row("Client ID", masked_id)
            table.add_row("Client Secret", "************")
        else:
            table.add_row("Client ID", "не установлен")
            table.add_row("Client Secret", "не установлен")
        
        table.add_row("Модель", config.get('model', 'GigaChat'))
        table.add_row("API URL", config.get('api_url', 'не указан'))
        
        self.console.print(table)
    
    def show_help(self):
        """Показать справку по командам."""
        help_text = """
## 📚 Справка по командам

### Основные команды
| Команда | Описание |
|---------|----------|
| `/help` | Показать эту справку |
| `/setup` | Запустить мастер настройки API |
| `/config` | Показать текущую конфигурацию |
| `/quit`, `/exit` | Выйти из программы |

### Команды чата
| Команда | Описание |
|---------|----------|
| `/clear` | Очистить историю текущего чата |
| `/new` | Начать новый чат |
| `/history` | Показать историю сообщений |

### Команды работы с кодом
| Команда | Описание |
|---------|----------|
| `/analyze <путь>` | Анализировать файл с кодом |
| `/explain <код>` | Объяснить, что делает код |
| `/refactor <код>` | Предложить улучшения кода |
| `/test <код>` | Создать тесты для кода |

### Примеры использования
```
/analyze my_script.py
/explain def factorial(n): return 1 if n <= 1 else n * factorial(n-1)
/refactor x = [i*2 for i in range(10) if i > 5]
```

**Просто напишите свой вопрос или задачу**, и я постараюсь помочь!
        """
        panel = Panel(
            Markdown(help_text),
            title="❓ Справка",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def show_typing_indicator(self):
        """Показать индикатор набора текста."""
        spinner = Spinner("dots", text="[cyan]GigaChat думает...[/cyan]")
        return Live(spinner, console=self.console, transient=True)
    
    def print_file_analysis(self, file_path: str, analysis: str):
        """Показать результат анализа файла."""
        panel = Panel(
            f"[bold]Файл:[/bold] {file_path}\n\n{analysis}",
            title="📁 Анализ файла",
            border_style="magenta",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def print_history(self, messages: list):
        """Показать историю сообщений."""
        if not messages:
            self.print_info("История пуста")
            return
        
        table = Table(title="📜 История сообщений", show_header=True, header_style="bold")
        table.add_column("#", style="dim")
        table.add_column("Роль", style="cyan")
        table.add_column("Сообщение", style="white", max_width=60)
        
        for i, msg in enumerate(messages, 1):
            role = "👤" if msg['role'] == 'user' else "🤖"
            content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            content = content.replace('\n', ' ')
            table.add_row(str(i), role, content)
        
        self.console.print(table)
