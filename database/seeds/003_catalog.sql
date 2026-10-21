-- ============================================================
-- Sistema Kiki
-- Seed 003: Catálogo base de Kiki Sushi
-- ============================================================


-- ------------------------------------------------------------
-- 1. CATEGORÍAS DE KIKI SUSHI
-- ------------------------------------------------------------
BEGIN;
INSERT INTO categories (
    organization_id,
    business_id,
    code,
    name,
    display_order
)
SELECT
    o.id,
    b.id,
    category_data.code,
    category_data.name,
    category_data.display_order
FROM organizations AS o
JOIN businesses AS b
    ON b.organization_id = o.id
CROSS JOIN (
    VALUES
        ('entradas',    'Entradas',     1),
        ('makis',       'Makis',        2),
        ('onigiris',    'Onigiris',     3),
        ('nigiris',     'Nigiris',      4),
        ('rolls',       'Rolls',        5),
        ('tempura',     'Tempura',      6),
        ('especiales',  'Especiales',   7),
        ('rolls_premium','Rolls Premium',8),
        ('fuertes',     'Fuertes',      9),
        ('ramen',       'Ramen',        10),
        ('poke_bowls',  'Poke Bowls',   11),
        ('bebidas',     'Bebidas',      12),
        ('fenix',       'Fénix',        13)
) AS category_data(code, name, display_order)
WHERE o.code = 'grupo_kiki'
    AND b.code = 'kiki_sushi'

ON CONFLICT (business_id, code)
DO UPDATE SET
    name = EXCLUDED.name,
    display_order = EXCLUDED.display_order,
    is_active = true,
    updated_at = now();

-- ------------------------------------------------------------
-- 2. ÁREAS DE PREPARACIÓN DE KIKI SANTA ROSA
-- ------------------------------------------------------------

INSERT INTO preparation_areas (
    organization_id,
    branch_id,
    code,
    name
)
SELECT
    o.id,
    br.id,
    area_data.code,
    area_data.name
FROM organizations AS o
JOIN businesses AS b
    ON b.organization_id = o.id
JOIN branches AS br
    ON br.business_id = b.id
   AND br.organization_id = o.id
CROSS JOIN (
    VALUES
        ('kitchen', 'Cocina'),
        ('bar', 'Barra')
) AS area_data(code, name)
WHERE o.code = 'grupo_kiki'
  AND b.code = 'kiki_sushi'
  AND br.code = 'santa_rosa'

ON CONFLICT (branch_id, code)
DO UPDATE SET
    name = EXCLUDED.name,
    is_active = true,
    updated_at = now();

    
-- ------------------------------------------------------------
-- 3. DESACTIVAR ÁREAS DE PREPARACIÓN QUE YA NO SE UTILIZAN
-- ------------------------------------------------------------

UPDATE preparation_areas AS pa
SET
    is_active = false,
    updated_at = now()
FROM branches AS br
JOIN businesses AS b
    ON b.id = br.business_id
JOIN organizations AS o
    ON o.id = br.organization_id
WHERE pa.branch_id = br.id
  AND pa.organization_id = o.id
  AND o.code = 'grupo_kiki'
  AND b.code = 'kiki_sushi'
  AND br.code = 'santa_rosa'
  AND pa.code NOT IN (
      'kitchen',
      'bar'
  );

COMMIT;