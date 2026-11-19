SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '10s';
ALTER TABLE public.links ADD COLUMN IF NOT EXISTS title text;
