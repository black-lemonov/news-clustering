"""
Конфигурация приложения

Содержит аргументы для таймеров, пути к базе данных и конфигурации логгера.
"""

# таймер для запуска парсеров:
parser_timeout: int = 3600 # сек

# интервал с которым парсеры будут отправлять запросы:
parsers_interval: int = 2 # сек

# таймер для клинера:
cleaner_timeout: int = 2 * 24 * 3600 # сек

# путь к базе данных:
db_path: str = "articles.db"

# путь к файлу с конфигурацией логгера:
logger_config_path: str = "logging.conf"