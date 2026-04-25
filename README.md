# Запуск
- Заполнить .env файл в корне проекта по примеру .env.example
- `docker compose -f .docker/docker-compose.yml up -d --build`

# Адреса
- http://127.0.0.1/admin/ - Админка
- http://127.0.0.1/api/movies/doc/ - Документация апи по фильмам
- http://127.0.0.1/api/api/auth/doc/ - Документация апи по авторизации


# Тесты
Movies API функциональные тесты:
```
docker compose -f movies_api/src_api/tests/functional/docker-compose.yml \
    run --build --rm movies_api_run_tests \
&& docker compose -f movies_api/src_api/tests/functional/docker-compose.yml \
    down
```

Auth API функциональные тесты:
```
docker compose -f auth_api/src_auth/tests/functional/docker-compose.yml \
    run --build --rm auth_api_run_tests \
&& docker compose -f auth_api/src_auth/tests/functional/docker-compose.yml \
    down
```