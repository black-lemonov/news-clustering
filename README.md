### Команды
- Создание БД:
```shell
flask -A flaskr init-db
```
- Запуск приложения:
```shell
flask -A flaskr run
```
- Запуск парсеров:
```shell
flask -A flaskr run-parsers
```
- Запуск алгоритма кластеризации:
```shell
flask -A flaskr run-algorithm
```

### Запуск celery:
Сначала запустить рабочих:
```shell
celery -A flaskr.make_celery worker --loglevel=INFO
```
Затем запустить фоновые задачи
```shell
celery -A flaskr.make_celery beat --loglevel=INFO
```
