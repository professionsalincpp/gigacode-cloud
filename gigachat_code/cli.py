#!/usr/bin/env python3
"""GigaChat Code Assistant - CLI приложение."""
import sys
import argparse

from gigachat_code.models.config import ConfigManager
from gigachat_code.views.terminal_view import TerminalView
from gigachat_code.controllers.setup_controller import SetupController
from gigachat_code.controllers.chat_controller import ChatController


def main():
    """Точка входа приложения."""
    parser = argparse.ArgumentParser(
        description="GigaChat Code Assistant - ваш помощник для работы с кодом",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s setup     - Запустить мастер настройки API
  %(prog)s chat      - Запустить интерактивный чат
  %(prog)s config    - Показать текущую конфигурацию
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда setup
    setup_parser = subparsers.add_parser('setup', help='Настроить API ключи GigaChat')
    
    # Команда chat
    chat_parser = subparsers.add_parser('chat', help='Запустить интерактивный чат')
    
    # Команда config
    config_parser = subparsers.add_parser('config', help='Показать текущую конфигурацию')
    
    args = parser.parse_args()
    
    # Создаем общие компоненты
    view = TerminalView()
    config_manager = ConfigManager()
    
    if args.command == 'setup':
        # Запуск мастера настройки
        controller = SetupController(view, config_manager)
        success = controller.run_setup()
        sys.exit(0 if success else 1)
    
    elif args.command == 'chat':
        # Запуск чата
        controller = ChatController(view, config_manager)
        controller.run_chat_loop()
        sys.exit(0)
    
    elif args.command == 'config':
        # Показать конфигурацию
        config = config_manager.load()
        view.show_config(config.to_dict())
        sys.exit(0)
    
    else:
        # По умолчанию показываем приветствие и справку
        view.print_welcome()
        
        # Проверяем настроен ли API
        config = config_manager.load()
        if not config.is_valid():
            view.print_warning("API не настроен!")
            view.print_info("Запустите настройку командой:")
            print("\n  python -m gigachat_code.cli setup\n")
            view.print_info("Или используйте /setup внутри чата")
        else:
            view.print_success("API настроен и готов к работе!")
            view.print_info("Запустите чат командой:")
            print("\n  python -m gigachat_code.cli chat\n")
        
        sys.exit(0)


if __name__ == '__main__':
    main()
