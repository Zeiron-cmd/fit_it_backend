# Fit it Backend

FastAPI backend для авторизации, профиля пользователя, загрузки фото еды, распознавания еды через Gemini и дневника питания.

## Реализовано

- регистрация пользователя
- вход пользователя по email/password
- `POST /auth/token` — стандартная OAuth2-compatible выдача JWT bearer-токена
- JWT-авторизация
- получение текущего пользователя
- OAuth login: Google, GitHub, Yandex через Authlib
- PostgreSQL вместо SQLite
- получение и редактирование профиля
- загрузка фото еды
- распознавание еды через Gemini при наличии `GEMINI_API_KEY`
- fallback-заглушка распознавания без `GEMINI_API_KEY`, чтобы локальная разработка не ломалась
- сохранение результата в базу
- ручное исправление результата
- дневник питания за день
- подсчёт калорий за день
- подсчёт калорий за неделю
- удаление записи питания

## Быстрый запуск

```bash
cp .env.example .env
# заполнить JWT_SECRET_KEY, SESSION_SECRET_KEY, при необходимости OAuth и GEMINI_API_KEY
docker compose up --build
```

API будет доступен на `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`.

## Auth endpoints

- `POST /auth/register`
- `POST /auth/login` — JSON `{ "email": "...", "password": "..." }`
- `POST /auth/token` — form-data для OAuth2 Password Flow: `username`, `password`
- `GET /auth/me`
- `GET /auth/oauth/providers`
- `GET /auth/oauth/google/login`
- `GET /auth/oauth/github/login`
- `GET /auth/oauth/yandex/login`

OAuth callback URL в настройках провайдеров:

- Google: `http://localhost:8000/auth/oauth/google/callback`
- GitHub: `http://localhost:8000/auth/oauth/github/callback`
- Yandex: `http://localhost:8000/auth/oauth/yandex/callback`

Если `FRONTEND_OAUTH_REDIRECT_URL` задан, backend после OAuth перенаправит пользователя туда с query-параметрами `access_token` и `token_type`. Если не задан — callback вернёт JSON с токеном.

## Profile endpoints

- `GET /profile/me`
- `PATCH /profile/me`

## Meals endpoints

- `POST /meals/photo`
- `GET /meals/day`
- `GET /meals/calories/day`
- `GET /meals/calories/week`
- `PATCH /meals/{meal_id}`
- `DELETE /meals/{meal_id}`

## Gemini

Для реального распознавания еды укажите в `.env`:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3-flash-preview
```

Без ключа backend вернёт демо-результат, как раньше.

## Ngrok example

```bash
ngrok http 8000
```
