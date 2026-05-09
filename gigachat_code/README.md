# GigaChat Code

Аналог Claude Code с использованием GigaChat API. MVC архитектура с удобным терминальным интерфейсом на базе библиотеки Rich.

## Возможности

- 🎨 Красивый терминальный интерфейс с использованием Rich
- 🔐 Удобная настройка API ключа через интерактивный мастер
- 💬 Интерактивный чат с историей сообщений
- 📁 Анализ файлов и работа с кодом
- 🔄 Поддержка сессий
- ⚙️ Гибкая конфигурация параметров генерации

## Установка

```bash
cd gigachat_code
pip install -e .
```

## Использование

### Настройка API

Первый запуск требует настройки API ключа:

```bash
gigachat-code setup
```

Или используйте команду `/setup` внутри чата.

### Запуск чата

```bash
gigachat-code chat
# или просто
gigachat-code
```

### Доступные команды в чате

- `/help` - Показать справку
- `/exit`, `/quit` - Выход из программы
- `/clear` - Очистить историю чата
- `/new` - Начать новую сессию
- `/config` - Показать текущую конфигурацию
- `/setup` - Настроить API ключ
- `/analyze <file>` - Анализировать файл
- `/history` - Показать историю сессии
- `/session` - Информация о сессии

## Структура проекта

```
gigachat_code/
├── __init__.py          # Инициализация пакета
├── main.py              # Точка входа
├── cli.py               # CLI интерфейс
├── config/
│   ├── __init__.py
│   └── settings.py      # Управление конфигурацией
├── models/
│   ├── __init__.py
│   └── entities.py      # Модели данных
├── core/
│   ├── __init__.py
│   └── assistant.py     # Ядро: GigaChatClient, CodeAssistant
├── views/
│   ├── __init__.py
│   └── terminal.py      # TerminalView на базе Rich
└── controllers/
    ├── __init__.py
    └── main.py          # SetupController, ChatController
```

## MVC Архитектура

- **Model** (`models/`) - Модели данных: Message, ChatSession, APIResponse, FileContext
- **View** (`views/`) - Терминальный интерфейс с использованием Rich
- **Controller** (`controllers/`) - Логика приложения: SetupController, ChatController
- **Core** (`core/`) - Ядро: работа с API, файловые операции, бизнес-логика

## Конфигурация

Конфигурация хранится в `~/.gigachat_code/config.json`:

- `api_key` - Ключ доступа к GigaChat API
- `api_url` - URL эндпоинта API
- `model` - Используемая модель
- `max_tokens` - Максимальное количество токенов
- `temperature` - Температура генерации

Также можно использовать переменную окружения `GIGACHAT_API_KEY`.

## Требования

- Python 3.8+
- rich >= 13.0.0
- requests >= 2.28.0

## Лицензия

MIT
