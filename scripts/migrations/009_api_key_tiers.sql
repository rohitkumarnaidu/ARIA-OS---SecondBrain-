-- ARIA OS — API Key Tiers Migration
-- Adds tier field to api_keys table and seeds default plans

ALTER TABLE IF EXISTS api_keys
  ADD COLUMN IF NOT EXISTS tier TEXT NOT NULL DEFAULT 'free',
  ADD COLUMN IF NOT EXISTS last_used_at TIMESTAMPTZ;

-- Create index for tier-based queries
CREATE INDEX IF NOT EXISTS idx_api_keys_tier ON api_keys(tier);

-- Seed reference data for tier definitions (for documentation / admin UI)
CREATE TABLE IF NOT EXISTS api_key_tiers (
  name TEXT PRIMARY KEY,
  max_requests INTEGER NOT NULL,
  window_seconds INTEGER NOT NULL DEFAULT 60,
  concurrent_limit INTEGER NOT NULL DEFAULT 1,
  price_per_month_usd DECIMAL(10,2) NOT NULL DEFAULT 0,
  description TEXT
);

INSERT INTO api_key_tiers (name, max_requests, window_seconds, concurrent_limit, price_per_month_usd, description)
VALUES
  ('free', 10, 60, 1, 0.00, 'Free tier — 10 requests per minute, 1 concurrent connection'),
  ('pro', 100, 60, 10, 9.99, 'Pro tier — 100 requests per minute, 10 concurrent connections'),
  ('enterprise', 1000, 60, 100, 49.99, 'Enterprise tier — 1000 requests per minute, 100 concurrent connections'),
  ('internal', 10000, 60, 500, 0.00, 'Internal tier — for first-party apps and internal services')
ON CONFLICT (name) DO UPDATE
SET
  max_requests = EXCLUDED.max_requests,
  concurrent_limit = EXCLUDED.concurrent_limit,
  price_per_month_usd = EXCLUDED.price_per_month_usd,
  description = EXCLUDED.description;
