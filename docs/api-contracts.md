# API-контракты Shortcuter v1.0

> Заморожено: 2026-09-21. Меняется только согласованием всех троих в чате.
> Источник требований: ТЗ, разделы 4.1.1–4.1.3 (`latex/tz_shortcuter.tex`).
> Решение команды 25.09: монолит FastAPI (полиглот отклонён). Разделы 1–2, 4–5,
> 9 переписаны под монолит; остальное без изменений.

## 1. Архитектура: монолит FastAPI

Решение команды (25.09): монолит на Python / FastAPI. Полиглот (C++ guest,
отдельные сервисы, nginx-маршрутизация) отклонён: тройная кодовая база и стыки
не окупаются в рамках 8 лаб. ТЗ при этом остаётся валидным — оно описывало
монолит изначально.

Один процесс `app` (порт 8000) + PostgreSQL (5432, только внутри compose).
Зоны ответственности внутри кода (по роутерам):

| Зона | Владелец | Что делает |
|---|---|---|
| гость (без входа) | Стёпа | `POST /api/links` без токена, `GET /{code}` |
| пользователь | Иван | `auth`, `/api/my/*` |
| админ | Саня | `/api/admin/*` |

Схему БД (`users`, `links`) меняет только миграция (ЛР8), код — никогда напрямую.

## 2. Маршруты приложения

nginx нет — один процесс отвечает на всё напрямую (порт 8000).

| Запрос | Зона |
|---|---|
| `POST /api/links` | создание ссылки: без токена — гостевая (`owner_id NULL`), с токеном — своя |
| `GET /{code}` | редирект 301 |
| `POST /api/auth/register`, `POST /api/auth/login` | вход |
| `GET /api/my/links`, `DELETE /api/my/links/{id}`, `PUT /api/my/links/{id}/alias` | ссылки пользователя |
| `GET /api/admin/users`, `POST /api/admin/users/{id}/block` | админка |

Соответствует ТЗ 4.1.1 один в один: там `POST /api/links` — «гость, пользователь».
Отдельного `POST /api/my/links` нет (был нужен только полиглоту, чтобы C++-сервис
не проверял чужой JWT, — решение 25.09 его отменило).

## 3. Формат кода и алиаса

- Автокод: 6 символов `[A-Za-z0-9]`, криптографический RNG.
- Алиас: 3–32 символа `[A-Za-z0-9_-]`, задаёт пользователь.
- Запрещены алиасы: `api`, `admin`, `my`, `auth`, `static`, `favicon.ico`
  (конфликт с маршрутизацией) — ответ `400`.
- Коллизия кода/алиаса (`UNIQUE`): повторить генерацию (автокод) или `409` (алиас).

## 4. Авторизация

- Схема: `Authorization: Bearer <JWT>`, алгоритм HS256, секрет — только в env
  (`JWT_SECRET`), в репозитории секретов нет (ТЗ 4.1.5).
- Выдаётся при входе (`POST /api/auth/login`). Срок жизни: 24 часа, claim `sub` = id.
- Проверяется на каждый запрос к `/api/my/*` и `/api/admin/*`: подпись + `is_blocked`
  из БД. Заблокированный — `403` даже с валидным токеном.
- `POST /api/links` и `GET /{code}` — без входа; приложенный токен задаёт владельца.

## 5. Эндпоинты

Тела — JSON. `id` — int. Даты — ISO 8601 UTC.

### 5.1. Без входа

**`POST /api/links`** — создать ссылку. Без токена — гостевая, с токеном — своя
(`owner_id` из токена). Один путь на всех, как в ТЗ 4.1.1.
```json
// request
{ "url": "https://example.com/long/path" }
// response 201
{ "id": 17, "code": "aB3x9Q", "url": "https://example.com/long/path",
  "short_url": "http://<host>/aB3x9Q", "owner_id": null }
```
Ошибки: `400` (не http(s), мусор), `401` (токен приложен, но бит),
`403` (заблокирован), `500`.

**`GET /{code}`** — редирект.
- Нашёл: `301`, заголовок `Location: <url>`, пустое тело.
- Нет кода: `404` в едином формате ошибок (см. п.6).

### 5.2. Пользователь (вход)

**`POST /api/auth/register`** — `{ "email", "password" }` (пароль ≥ 8 символов).
`201`: `{ "id", "email" }`. Дубликат email: `409`. Пароль хранить только хешем
(bcrypt/argon2, на выбор реализующего).

**`POST /api/auth/login`** — `{ "email", "password" }`.
`200`: `{ "token", "token_type": "Bearer", "expires_in": 86400 }`.
Неверная пара: `401`. Заблокированный: `403`.

**`GET /api/my/links`** (auth) — `200`: `{ "links": [ { "id", "code", "url", "short_url", "created_at" } ] }`.
Только свои, сортировка — новые первые.

**`DELETE /api/my/links/{id}`** (auth) — `204` без тела. Чужая/нет: `404`
(не `403` — не раскрываем существование чужих ссылок).

**`PUT /api/my/links/{id}/alias`** (auth) — `{ "alias": "moy-kursach" }`.
`200`: полный объект ссылки. Занят: `409`. Недопустимый: `400`. Чужая: `404`.

### 5.3. Админ

**`GET /api/admin/users`** (auth + `role=admin`) —
`200`: `{ "users": [ { "id", "email", "role", "is_blocked", "created_at" } ] }`.
Не админ: `403`.

**`POST /api/admin/users/{id}/block`** (auth + `role=admin`) —
`{ "is_blocked": true|false }` → `200`: объект пользователя. Себя блокировать
нельзя: `400`. Нет пользователя: `404`.

Роль `admin` выставляется вручную через БД (SQL в `services/db/schema.sql`, не через API).

## 6. Единый формат ошибок (хуки, ТЗ 4.1.3)

Каждый сервис реализует обработчики на уровне приложения, ответ всегда JSON:

```json
// status 404
{ "error": { "code": "LINK_NOT_FOUND", "message": "Ссылка не найдена" } }
```

| HTTP | Когда | Примеры `code` |
|---|---|---|
| 400 | плохой URL, плохой алиас, короткий пароль, блокировка себя | `BAD_URL`, `BAD_ALIAS`, `RESERVED_ALIAS`, `WEAK_PASSWORD`, `SELF_BLOCK` |
| 401 | нет/битый токен | `UNAUTHORIZED` |
| 403 | чужая ссылка (там где уместно), заблокированный, не админ | `FORBIDDEN`, `USER_BLOCKED` |
| 404 | нет кода/ссылки/пользователя | `LINK_NOT_FOUND`, `USER_NOT_FOUND` |
| 409 | дубликат email, занятый алиас | `EMAIL_TAKEN`, `ALIAS_TAKEN` |
| 500 | всё остальное + запись в журнал | `INTERNAL_ERROR` |

Сообщения — на русском, понятные пользователю. `500` без деталей наружу.

## 7. База данных (общая, PostgreSQL 14+)

```sql
CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  email        TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role         TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user','admin')),
  is_blocked   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE links (
  id         SERIAL PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  url        TEXT NOT NULL,
  owner_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Правила: `owner_id NULL` = гостевая ссылка (удалить может только админ,
отдельного эндпоинта нет — через БД; в API не добавляем). Миграции — в ЛР8,
пока схему поднимаем SQL-файлом `services/db/schema.sql` (шаг 1).

## 8. Проверка готовности (e2e-критерий шага 0→1)

```bash
# 1. создать без входа
curl -X POST localhost:8000/api/links -d '{"url":"https://example.com"}'
# → 201, code
# 2. перейти
curl -o /dev/null -s -w "%{http_code} %{redirect_url}\n" localhost:8000/<code>
# → 301 https://example.com
# 3. несуществующий код → 404 JSON, не пустая страница
curl -s localhost:8000/nope123
# → {"error":{"code":"LINK_NOT_FOUND",...}}
```

## 9. Открытые вопросы (добить в чате)

1. Язык админки — решено 25.09: Python (монолит FastAPI), один набор анализаторов в ЛР6.
2. JWT-секрет и пароли Postgres: общий `.env` (в `.gitignore`) + `.env.example` в репо — ок?
3. Валидация «достижимости» URL (ТЗ 4.1.3 упоминает): делаем best-effort HEAD-запрос или только синтаксис? Предложение: только синтаксис (проверка достижимости флакает в тестах ЛР7).
