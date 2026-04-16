-- =============================================================
-- Net Worth Tracker — Supabase Schema
-- Run this entire file in:
--   Supabase Dashboard → SQL Editor → New Query → Run
-- =============================================================


-- -------------------------------------------------------------
-- ASSETS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assets (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID    NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS asset_values (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id    UUID    NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    month       INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    year        INTEGER NOT NULL CHECK (year > 2000),
    value       NUMERIC(15,2) NOT NULL DEFAULT 0,
    UNIQUE (asset_id, month, year)
);


-- -------------------------------------------------------------
-- LIABILITIES
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS liabilities (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID    NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS liability_values (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    liability_id    UUID    NOT NULL REFERENCES liabilities(id) ON DELETE CASCADE,
    month           INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    year            INTEGER NOT NULL CHECK (year > 2000),
    value           NUMERIC(15,2) NOT NULL DEFAULT 0,
    UNIQUE (liability_id, month, year)
);


-- -------------------------------------------------------------
-- GOALS
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS goals (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID    NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name            TEXT    NOT NULL,
    target_amount   NUMERIC(15,2) NOT NULL,
    current_amount  NUMERIC(15,2) NOT NULL DEFAULT 0,
    deadline        DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =============================================================
-- ROW LEVEL SECURITY (RLS)
-- Each user can only see and modify their own data.
-- =============================================================

-- Assets
ALTER TABLE assets         ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_values   ENABLE ROW LEVEL SECURITY;
ALTER TABLE liabilities    ENABLE ROW LEVEL SECURITY;
ALTER TABLE liability_values ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals          ENABLE ROW LEVEL SECURITY;

-- Assets policies
CREATE POLICY "Users manage own assets"
    ON assets FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users manage own asset values"
    ON asset_values FOR ALL
    USING (
        asset_id IN (SELECT id FROM assets WHERE user_id = auth.uid())
    );

-- Liabilities policies
CREATE POLICY "Users manage own liabilities"
    ON liabilities FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users manage own liability values"
    ON liability_values FOR ALL
    USING (
        liability_id IN (SELECT id FROM liabilities WHERE user_id = auth.uid())
    );

-- Goals policies
CREATE POLICY "Users manage own goals"
    ON goals FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
