# Base de Datos — Sistema Kiki

## Objetivo

Esta carpeta contiene todo lo relacionado con el diseño, evolución y documentación de la base de datos del Sistema Kiki.

La base de datos será diseñada para soportar múltiples negocios y sucursales, incluyendo inicialmente Kiki Sushi y Rivana.

---

## Motor de base de datos

**PostgreSQL 18**

PostgreSQL será la fuente principal de verdad para:

- usuarios;
- negocios;
- sucursales;
- productos;
- pedidos;
- ventas;
- pagos;
- caja;
- inventario;
- promociones;
- wallet;
- auditoría.

---

## Estructura

```text
database/
├── diagrams/
├── migrations/
├── seeds/
└── README.md
```

### `migrations/`

Contendrá los cambios versionados de la estructura de la base de datos.

Ejemplo:

```text
001_foundation.sql
002_catalog.sql
003_sales.sql
```

### `seeds/`

Contendrá datos iniciales necesarios para el funcionamiento del sistema.

Ejemplos:

- permisos;
- roles base;
- tipos de movimiento;
- configuraciones iniciales.

### `diagrams/`

Contendrá los diagramas del modelo de datos.

Principalmente:

- modelo entidad-relación;
- diagramas por dominio.

---

# Convenciones

## Nombres

Se utilizará `snake_case`.

Ejemplo:

```text
organization_id
created_at
payment_method
inventory_movement
```

---

## Tablas

Los nombres de las tablas se escribirán en plural.

Ejemplos:

```text
organizations
businesses
branches
users
orders
payments
```

---

## Claves primarias

Las entidades principales utilizarán UUID.

Convención:

```text
id
```

Ejemplo:

```text
id UUID PRIMARY KEY
```

La estrategia prevista será UUID versión 7.

---

## Claves foráneas

Las claves foráneas utilizarán el nombre de la entidad seguido de `_id`.

Ejemplo:

```text
organization_id
business_id
branch_id
user_id
order_id
```

---

## Fechas

Las tablas transaccionales deberán almacenar sus fechas utilizando zona horaria.

Convención:

```text
created_at
updated_at
```

Tipo esperado:

```text
TIMESTAMPTZ
```

---

## Dinero

Los valores monetarios nunca deberán utilizar tipos de punto flotante.

Se utilizarán tipos decimales exactos.

Ejemplo:

```text
NUMERIC(12,2)
```

Nunca:

```text
FLOAT
```

---

## Estados

Las entidades que posean ciclo de vida deberán utilizar estados explícitos.

Ejemplo:

```text
OPEN
CLOSED
CANCELLED
```

No deberá determinarse un estado únicamente por ausencia de información.

---

## Eliminaciones

Los datos históricos o transaccionales importantes no deberán eliminarse físicamente durante la operación normal.

Ejemplos:

- pedidos;
- ventas;
- pagos;
- cierres de caja;
- movimientos de inventario;
- transacciones wallet;
- auditorías.

Cuando corresponda se utilizarán:

- estados;
- anulaciones;
- reversos;
- registros compensatorios.

---

## Migraciones

Cada modificación estructural de la base de datos deberá realizarse mediante una migración versionada.

Una migración ya utilizada en un entorno compartido no deberá modificarse.

Se deberá crear una nueva migración para introducir cambios posteriores.

---

## Integridad

Las reglas críticas deberán protegerse tanto en la aplicación como en PostgreSQL mediante mecanismos como:

- `PRIMARY KEY`;
- `FOREIGN KEY`;
- `UNIQUE`;
- `NOT NULL`;
- `CHECK`;
- transacciones.

La aplicación no será la única responsable de proteger la integridad de los datos.

---

## Principio fundamental

La estructura de la base de datos deberá permitir reconstruir y explicar las operaciones importantes del negocio.

Por ejemplo:

```text
Venta
→ Pedido
→ Productos
→ Pago
→ Caja
→ Inventario
→ Usuario responsable
```

La trazabilidad tendrá prioridad sobre la conveniencia de modificar o eliminar registros.