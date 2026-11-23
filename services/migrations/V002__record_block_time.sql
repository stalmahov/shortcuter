SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '10s';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS blocked_at timestamptz;
