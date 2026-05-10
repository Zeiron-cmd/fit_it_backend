# Frontend API contract

## Backend URL

If backend runs on another computer, frontend `.env` must use the ngrok URL:

```env
VITE_API_URL=https://YOUR-NGROK.ngrok-free.dev
```

Do not use `http://localhost:8000` unless backend is running on the same computer as frontend.

## Auth

### Register

`POST /auth/register`

```json
{ "email": "test@test.com", "password": "123456" }
```

### Login

`POST /auth/login`

```json
{ "email": "test@test.com", "password": "123456" }
```

Response:

```json
{ "access_token": "...", "token_type": "bearer" }
```

Save `access_token` and send protected requests with:

```http
Authorization: Bearer ACCESS_TOKEN
```

### Current user

`GET /auth/me`

## OAuth buttons

Open these URLs in the browser:

```js
window.location.href = `${API_URL}/auth/oauth/google/login`;
window.location.href = `${API_URL}/auth/oauth/github/login`;
window.location.href = `${API_URL}/auth/oauth/yandex/login`;
```

The backend redirects to:

```text
http://localhost:5173/oauth/callback?access_token=...&token_type=bearer
```

Frontend page `/oauth/callback` should read `access_token` from query params and save it.

## Meal photo

`POST /meals/photo` with `FormData` field `file` and Bearer token.
