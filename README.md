# Запуск
- Заполнить .env файлы, путь от корня проекта:
- - `./.env` по примеру `./.env.example`
- - `./movies_api/.env` по примеру `./movies_api/.env.example`
- - `./etl/.env` по примеру `./etl/.env.example`
- - `./auth_api/.env` по примеру `./auth_api/.env.example`
- - `./admin_panel/.env` по примеру `./admin_panel/.env.example`
- Выполнить из корня:  `docker compose -f .docker/docker-compose.yml up -d --build`

# Адреса / Документация
- http://127.0.0.1/admin/ - Админка
- http://127.0.0.1/api/movies/doc/ - Документация апи по фильмам
- http://127.0.0.1/api/api/auth/doc/ - Документация апи по авторизации
* [Документация Auth API.](auth_api/README.md)
* [Документация Movies API](movies_api/README.md)


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

## Доступ к фильмам
Просмотр детализации фильма по id датой выхода менее 3 лет назад: `/api/movies/v1/movies/{movie_id}` доступно только авторизованному пользователю с ролью `subscriber` в токене.