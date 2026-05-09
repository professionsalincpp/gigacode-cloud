#!/usr/bin/env python3
"""
GigaChat Code - аналог Claude Code с использованием GigaChat API
Главный файл запуска приложения
"""

import sys
import argparse

from .config import Config
from .controllers import SetupController, ChatController
from .views import TerminalView


def setup_command(args, config: Config, view: TerminalView) -> int:
    """Команда настройки"""
    controller = SetupController(config, view)
    success = controller.run_setup()
    return 0 if success else 1


def chat_command(args, config: Config, view: TerminalView) -> int:
    """Команда чата"""
    controller = ChatController(config, view)
    controller.run()
    return 0


def config_command(args, config: Config, view: TerminalView) -> int:
    """Показать конфигурацию"""
    if config.is_configured():
        view.show_config(config.get_all())
    else:
        view.print_info("Конфигурация не выполнена. Используйте 'gigachat-code setup'")
    return 0


def version_command(args, config: Config, view: TerminalView) -> int:
    """Показать версию"""
    from . import __version__
    view.console.print(f"[bold magenta]GigaChat Code[/bold magenta] v{__version__}")
    return 0


COMMANDS = {
    'setup': {
        'help': 'Настроить API ключ и параметры',
        'func': setup_command
    },
    'chat': {
        'help': 'Запустить интерактивный чат',
        'func': chat_command
    },
    'config': {
        'help': 'Показать текущую конфигурацию',
        'func': config_command
    },
    'version': {
        'help': 'Показать версию приложения',
        'func': version_command
    }
}


def main():
    """Точка входа в приложение"""
    parser = argparse.ArgumentParser(
        prog='gigachat-code',
        description='GigaChat Code - аналог Claude Code с использованием GigaChat API'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    for cmd_name, cmd_info in COMMANDS.items():
        subparsers.add_parser(cmd_name, help=cmd_info['help'])
    
    # Если команда не указана, показываем справку
    args = parser.parse_args()
    
    # Инициализация общих компонентов
    config = Config()
    view = TerminalView()
    
    if args.command is None:
        # Запуск чата по умолчанию
        args.command = 'chat'
    
    # Выполнение команды
    if args.command in COMMANDS:
        try:
            return COMMANDS[args.command]['func'](args, config, view)
        except KeyboardInterrupt:
            view.console.print("\n[yellow]Прервано пользователем[/yellow]")
            return 130
        except Exception as e:
            view.print_error(f"Произошла ошибка: {str(e)}")
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
