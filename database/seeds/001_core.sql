-- ============================================================
-- Sistema Kiki
-- Seed 001: Datos base de la organización
-- ============================================================
--
-- Este seed crea la estructura organizacional inicial necesaria
-- para que los demás seeds puedan ejecutarse.
--
-- Orden:
--   1. Organization
--   2. Businesses
--   3. Branches
--
-- Es idempotente: puede ejecutarse varias veces sin duplicar datos.
-- ============================================================


-- ------------------------------------------------------------
-- 1. ORGANIZATION
-- ------------------------------------------------------------

INSERT INTO organizations (
    code,
    name,
    is_active
)
VALUES (
    'grupo_kiki',
    'Grupo Kiki',
    true
)

ON CONFLICT (code)
DO UPDATE SET
    name = EXCLUDED.name,
    is_active = true,
    updated_at = now();


-- ------------------------------------------------------------
-- 2. BUSINESSES
-- ------------------------------------------------------------

INSERT INTO businesses (
    organization_id,
    code,
    name,
    is_active
)
SELECT
    o.id,
    business_data.code,
    business_data.name,
    true
FROM organizations AS o
CROSS JOIN (
    VALUES
        ('kiki_sushi', 'Kiki Sushi'),
        ('rivana',     'Rivana')
) AS business_data(code, name)
WHERE o.code = 'grupo_kiki'

ON CONFLICT (organization_id, code)
DO UPDATE SET
    name = EXCLUDED.name,
    is_active = true,
    updated_at = now();


-- ------------------------------------------------------------
-- 3. BRANCHES
-- ------------------------------------------------------------

INSERT INTO branches (
    organization_id,
    business_id,
    code,
    name,
    is_active
)
SELECT
    o.id,
    b.id,
    branch_data.code,
    branch_data.name,
    true
FROM organizations AS o
JOIN businesses AS b
    ON b.organization_id = o.id
CROSS JOIN (
    VALUES
        ('santa_rosa', 'Santa Rosa')
) AS branch_data(code, name)
WHERE o.code = 'grupo_kiki'
  AND b.code IN (
      'kiki_sushi',
      'rivana'
  )

ON CONFLICT (business_id, code)
DO UPDATE SET
    name = EXCLUDED.name,
    is_active = true,
    updated_at = now();