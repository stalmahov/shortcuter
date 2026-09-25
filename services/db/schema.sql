-- Схема БД Shortcuter (PostgreSQL 14+).
--
-- Источники: ТЗ разд. 4.1.2, docs/api-contracts.md разд. 7,
-- openapi.yaml (схемы User, Link).
--
-- Правила:
--   1. owner_id NULL = гостевая ссылка (владельца нет).
--   2. Роль admin выставляется вручную через БД, не через API.
--   3. Схему меняет только миграция (ЛР8); сервисы чужие таблицы не трогают.
--
-- Поднятие с нуля:
--   psql -h localhost -U shortcuter -d shortcuter -f services/db/schema.sql

CREATE TABLE IF NOT EXISTS users (
  id            SERIAL PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  is_blocked    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS links (
  id         SERIAL PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  url        TEXT NOT NULL,
  owner_id   INTEGER REFERENCES users (id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Выборка «мои ссылки, новые первые» (GET /api/my/links).
-- UNIQUE по email и code уже дают индексы, отдельно нужен только этот.
CREATE INDEX IF NOT EXISTS idx_links_owner ON links (owner_id, created_at DESC);
