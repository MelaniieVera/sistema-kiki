-- ============================================================
-- Sistema Kiki
-- Seed 001: RBAC inicial
-- ============================================================


-- ------------------------------------------------------------
-- 1. PERMISSIONS
-- ------------------------------------------------------------

INSERT INTO permissions (
    code,
    name,
    description
)
VALUES
    ('organization.view', 'Ver organización', 'Consultar información de la organización'),
    ('organization.manage', 'Administrar organización', 'Modificar configuración de la organización'),

    ('business.view', 'Ver negocios', 'Consultar negocios de la organización'),
    ('business.manage', 'Administrar negocios', 'Crear y modificar negocios'),

    ('branch.view', 'Ver sucursales', 'Consultar sucursales'),
    ('branch.manage', 'Administrar sucursales', 'Crear y modificar sucursales'),

    ('user.view', 'Ver usuarios', 'Consultar usuarios'),
    ('user.manage', 'Administrar usuarios', 'Crear, modificar y desactivar usuarios'),

    ('role.view', 'Ver roles', 'Consultar roles y permisos'),
    ('role.manage', 'Administrar roles', 'Crear roles y asignar permisos'),

    ('order.view', 'Ver pedidos', 'Consultar pedidos'),
    ('order.create', 'Crear pedidos', 'Crear y confirmar pedidos'),
    ('order.cancel', 'Cancelar productos o pedidos', 'Cancelar operaciones confirmadas'),

    ('kitchen.view', 'Ver comandas', 'Consultar comandas de producción'),
    ('kitchen.manage', 'Gestionar comandas', 'Cambiar estados de preparación'),

    ('payment.view', 'Ver pagos', 'Consultar pagos'),
    ('payment.create', 'Registrar pagos', 'Registrar pagos de clientes'),
    ('payment.refund', 'Revertir pagos', 'Registrar devoluciones o reversos autorizados'),

    ('cash.view', 'Ver caja', 'Consultar sesiones y movimientos de caja'),
    ('cash.open', 'Abrir caja', 'Abrir una sesión de caja'),
    ('cash.close', 'Cerrar caja', 'Realizar arqueo y cierre de caja'),
    ('cash.movement', 'Registrar movimientos de caja', 'Registrar ingresos y egresos'),

    ('inventory.view', 'Ver inventario', 'Consultar existencias y movimientos'),
    ('inventory.manage', 'Gestionar inventario', 'Registrar entradas y movimientos'),
    ('inventory.adjust', 'Ajustar inventario', 'Registrar ajustes de existencias'),

    ('promotion.view', 'Ver promociones', 'Consultar promociones'),
    ('promotion.manage', 'Administrar promociones', 'Crear y modificar promociones'),

    ('wallet.view', 'Ver wallets', 'Consultar saldo y movimientos'),
    ('wallet.recharge', 'Recargar wallet', 'Registrar recargas'),
    ('wallet.redeem', 'Redimir beneficios', 'Consumir saldo o derechos adquiridos'),

    ('report.view', 'Ver reportes', 'Consultar reportes operativos'),

    ('audit.view', 'Ver auditoría', 'Consultar registros de auditoría')

ON CONFLICT (code)
DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = true;


-- ------------------------------------------------------------
-- 2. ROLES DE GRUPO KIKI
-- ------------------------------------------------------------

INSERT INTO roles (
    organization_id,
    code,
    name,
    description
)
SELECT
    o.id,
    role_data.code,
    role_data.name,
    role_data.description
FROM organizations AS o
CROSS JOIN (
    VALUES
        ('administrator', 'Administrador', 'Acceso administrativo general'),
        ('manager', 'Gerente', 'Supervisión operativa de sucursal'),
        ('supervisor', 'Supervisor', 'Autoriza operaciones sensibles'),
        ('cashier', 'Cajero', 'Operación de pagos y caja'),
        ('waiter', 'Mesero', 'Registro y seguimiento de pedidos'),
        ('kitchen', 'Cocina', 'Gestión de comandas y preparación'),
        ('bartender', 'Bartender', 'Operación de barra y consumos'),
        ('inventory', 'Bodega / Inventario', 'Gestión de existencias')
) AS role_data(code, name, description)
WHERE o.code = 'grupo_kiki'

ON CONFLICT (organization_id, code)
DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = true;


-- ------------------------------------------------------------
-- 3. ADMINISTRADOR
-- Obtiene todos los permisos existentes
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
CROSS JOIN permissions AS p
JOIN organizations AS o
    ON o.id = r.organization_id
WHERE o.code = 'grupo_kiki'
  AND r.code = 'administrator'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 4. GERENTE
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'business.view',
        'branch.view',
        'user.view',
        'role.view',

        'order.view',
        'order.create',
        'order.cancel',

        'kitchen.view',
        'kitchen.manage',

        'payment.view',
        'payment.create',

        'cash.view',
        'cash.open',
        'cash.close',
        'cash.movement',

        'inventory.view',
        'inventory.manage',
        'inventory.adjust',

        'promotion.view',
        'promotion.manage',

        'wallet.view',

        'report.view',
        'audit.view'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'manager'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 5. SUPERVISOR
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'order.view',
        'order.create',
        'order.cancel',

        'payment.view',
        'payment.create',
        'payment.refund',

        'cash.view',
        'cash.open',
        'cash.close',
        'cash.movement',

        'inventory.view',
        'inventory.adjust',

        'promotion.view',

        'wallet.view',
        'wallet.recharge',
        'wallet.redeem'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'supervisor'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 6. CAJERO
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'order.view',
        'order.create',

        'payment.view',
        'payment.create',

        'cash.view',
        'cash.open',
        'cash.close',
        'cash.movement',

        'wallet.view',
        'wallet.recharge'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'cashier'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 7. MESERO
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'order.view',
        'order.create',
        'kitchen.view'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'waiter'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 8. COCINA
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'kitchen.view',
        'kitchen.manage'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'kitchen'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 9. BARTENDER
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'order.view',
        'order.create',

        'wallet.view',
        'wallet.redeem'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'bartender'

ON CONFLICT (role_id, permission_id)
DO NOTHING;


-- ------------------------------------------------------------
-- 10. INVENTARIO
-- ------------------------------------------------------------

INSERT INTO role_permissions (
    organization_id,
    role_id,
    permission_id
)
SELECT
    r.organization_id,
    r.id,
    p.id
FROM roles AS r
JOIN organizations AS o
    ON o.id = r.organization_id
JOIN permissions AS p
    ON p.code IN (
        'inventory.view',
        'inventory.manage'
    )
WHERE o.code = 'grupo_kiki'
  AND r.code = 'inventory'

ON CONFLICT (role_id, permission_id)
DO NOTHING;