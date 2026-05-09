"""Контроллер для настройки API."""
from ..models.config import ConfigManager, GigaChatConfig
from ..views.terminal_view import TerminalView


class SetupController:
    """Контроллер для настройки API ключей."""
    
    def __init__(self, view: TerminalView, config_manager: ConfigManager):
        self.view = view
        self.config_manager = config_manager
    
    def run_setup(self) -> bool:
        """Запустить мастер настройки."""
        try:
            # Показываем мастер настройки
            credentials = self.view.show_setup_wizard()
            
            # Проверяем введенные данные
            if not credentials.get('client_id') or not credentials.get('client_secret'):
                self.view.print_error("Client ID и Client Secret должны быть заполнены")
                return False
            
            # Создаем конфигурацию
            config = GigaChatConfig(
                client_id=credentials['client_id'],
                client_secret=credentials['client_secret']
            )
            
            # Сохраняем конфигурацию
            if self.config_manager.save(config):
                self.view.print_success("Конфигурация успешно сохранена!")
                self.view.print_info(f"Файл конфигурации: {self.config_manager.config_path}")
                return True
            else:
                self.view.print_error("Не удалось сохранить конфигурацию")
                return False
                
        except KeyboardInterrupt:
            self.view.print_info("\nНастройка отменена пользователем")
            return False
        except Exception as e:
            self.view.print_error(f"Ошибка при настройке: {str(e)}")
            return False
    
    def show_config(self):
        """Показать текущую конфигурацию."""
        config = self.config_manager.load()
        self.view.show_config(config.to_dict())
    
    def clear_config(self) -> bool:
        """Удалить конфигурацию."""
        if self.view.confirm("Вы уверены, что хотите удалить сохраненные учетные данные?"):
            if self.config_manager.clear():
                self.view.print_success("Конфигурация удалена")
                return True
            else:
                self.view.print_error("Не удалось удалить конфигурацию")
                return False
        return False
    
    def verify_config(self) -> bool:
        """Проверить валидность конфигурации."""
        config = self.config_manager.load()
        return config.is_valid()
