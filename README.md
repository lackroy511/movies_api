# Запуск
- Заполнить .env файл в корне проекта по примеру .env.example
- `docker compose -f .docker/docker-compose.yml up -d --build`

# Адреса
- http://127.0.0.1/admin/ - Админка
- http://127.0.0.1/api/doc - Документация апи
- http://127.0.0.1/api/... - API Эндпоинты


# Тесты
Movies API функциональные тесты:
- `docker compose -f api/src_api/tests/functional/docker-compose.yml run --rm movies_api_run_tests && docker compose -f api/src_api/tests/functional/docker-compose.yml down`