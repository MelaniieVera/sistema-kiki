# Sistema Kiki — Instrucciones para agentes de desarrollo

## 1. Propósito del proyecto

Sistema Kiki es una plataforma de gestión para restaurantes, bares y futuros negocios del Grupo Kiki.

El sistema debe soportar múltiples:

- organizaciones;
- negocios;
- sucursales;
- usuarios;
- roles;
- catálogos;
- puntos de venta;
- áreas de preparación;
- inventarios;
- pagos;
- cajas;
- promociones;
- programas de fidelización.

Actualmente los negocios iniciales son:

- Kiki Sushi
- Rivana

Ambos pertenecen a la organización `grupo_kiki`.

---

## 2. Filosofía de desarrollo

Este proyecto también tiene un propósito educativo.

No realizar grandes implementaciones de forma automática sin explicar primero:

1. qué problema se está resolviendo;
2. qué archivos serán modificados;
3. qué decisiones técnicas se están tomando;
4. qué efectos tendrá el cambio sobre la arquitectura existente.

Preferir cambios pequeños, revisables y fáciles de entender.

No realizar refactors amplios que no hayan sido solicitados.

No cambiar decisiones arquitectónicas existentes sin justificarlo explícitamente.

---

## 3. Stack tecnológico

Backend:

- Python 3.9
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic
- PostgreSQL 18
- psycopg

Infraestructura local:

- Docker
- Docker Compose

Pruebas manuales de API:

- Postman

Frontend planificado:

- React
- TypeScript
- Next.js

---

## 4. Compatibilidad con Python

El proyecto utiliza Python 3.9.

Por lo tanto:

Usar:

```python
from typing import Optional

name: Optional[str]
```

No usar:

```python
name: str | None
```

si esa sintaxis introduce incompatibilidad con la versión actual del proyecto.

---

## 5. Arquitectura

La arquitectura inicial es un modular monolith.

No convertir el proyecto en microservicios sin una decisión arquitectónica explícita.

La separación conceptual debe mantenerse mediante módulos internos.

---

## 6. Convenciones de base de datos

Motor:

PostgreSQL 18.

Convenciones:

- nombres de tablas en plural;
- snake_case;
- claves primarias UUID;
- usar UUID v7 mediante `uuidv7()`;
- claves foráneas nombradas explícitamente;
- restricciones importantes también deben existir en PostgreSQL;
- no depender exclusivamente de validaciones del backend.

Para dinero:

Usar:

```text
NUMERIC(12,2)
```

No usar:

```text
FLOAT
REAL
DOUBLE PRECISION
```

para importes monetarios.

---

## 7. Multitenancy

La jerarquía fundamental es:

```text
Organization
    ↓
Business
    ↓
Branch
```

Actualmente:

```text
Grupo Kiki
├── Kiki Sushi
│   └── Santa Rosa
└── Rivana
    └── Santa Rosa
```

Los datos que pertenecen a un tenant deben respetar la organización, negocio y/o sucursal correspondiente.

Cuando sea necesario, utilizar foreign keys compuestas para impedir inconsistencias entre tenants.

No confiar únicamente en el backend para garantizar aislamiento organizacional.

---

## 8. Usuarios y RBAC

La identidad `User` es global.

No agregar directamente:

```text
user.role_id
```

ni roles fijos dentro de `users`.

Los roles se asignan mediante:

```text
User
    ↓
UserBranchRole
    ↓
Role
    ↓
RolePermission
    ↓
Permission
```

Esto permite que una misma persona tenga roles distintos según la sucursal.

Los permisos utilizan códigos semánticos como:

```text
order.create
order.cancel
payment.create
cash.open
cash.close
inventory.adjust
```

---

## 9. Catálogo

Mantener estrictamente esta separación:

```text
Category
    ↓
Product
    ↓
ProductVariant
    ↓
BranchProductVariant
```

### Product

Representa el concepto comercial.

Ejemplo:

```text
Gyozas
```

No contiene el precio final de venta por sucursal.

### ProductVariant

Representa una presentación vendible.

Ejemplo:

```text
5 unidades
```

Incluso los productos sin variantes comerciales deben poder manejar una variante estándar.

### BranchProductVariant

Representa cómo se comercializa una variante en una sucursal.

Aquí pertenecen:

- precio;
- disponibilidad;
- estado;
- área de preparación/despacho.

El precio NO debe trasladarse a `Product`.

---

## 10. Áreas de preparación

Actualmente Kiki Santa Rosa utiliza únicamente:

```text
kitchen → Cocina
bar     → Barra
```

El área antigua `sushi` fue desactivada.

Regla fundamental:

```text
Category != PreparationArea
```

Una categoría NO determina automáticamente dónde se prepara un producto.

Ejemplos:

```text
Fénix Blonde
Categoría: Fénix
Área: Barra

Hamburguesa Fénix
Categoría: Fénix
Área: Cocina
```

El enrutamiento se determina en `BranchProductVariant`.

---

## 11. Categorías actuales de Kiki Sushi

Orden actual:

```text
1  entradas
2  makis
3  onigiris
4  nigiris
5  rolls
6  tempura
7  especiales
8  rolls_premium
9  fuertes
10 ramen
11 poke_bowls
12 bebidas
13 fenix
```

Nombres visibles:

```text
Entradas
Makis
Onigiris
Nigiris
Rolls
Tempura
Especiales
Rolls Premium
Fuertes
Ramen
Poke Bowls
Bebidas
Fénix
```

La tabla `categories` utiliza `display_order`.

---

## 12. Migraciones Alembic

Las migraciones deben considerarse transformaciones versionadas del esquema.

Reglas:

- revisar manualmente cada migración autogenerada;
- no ejecutar automáticamente `alembic upgrade head` después de generar una migración;
- verificar dependencias y orden de constraints;
- no modificar migraciones que ya hayan sido aplicadas y compartidas;
- si una migración aplicada necesita corrección, crear una nueva migración.

Alembic ya ha generado en ocasiones operaciones en un orden incorrecto con foreign keys compuestas y unique constraints.

Por ello siempre revisar:

```text
upgrade()
downgrade()
```

antes de aplicar.

---

## 13. Seeds

Los seeds representan datos iniciales reproducibles.

Actualmente:

```text
database/seeds/
├── 001_core.sql
├── 002_rbac.sql
└── 003_catalog.sql
```

### 001_core.sql

Inicializa:

- Grupo Kiki;
- Kiki Sushi;
- Rivana;
- sucursal Santa Rosa de Kiki Sushi;
- sucursal Santa Rosa de Rivana.

Debe permanecer idempotente.

### 002_rbac.sql

Inicializa roles, permisos y sus relaciones.

Debe permanecer idempotente.

### 003_catalog.sql

Inicializa:

- categorías base de Kiki Sushi;
- áreas Cocina y Barra.

Debe permanecer idempotente.

Los productos reales no deben cargarse masivamente mediante seeds salvo que exista una razón explícita.

El catálogo operativo debe administrarse progresivamente mediante la API y el panel administrativo.

---

## 14. API

La API se versiona bajo:

```text
/api/v1
```

Estructura actual aproximada:

```text
app/
├── main.py
├── api/
│   └── v1/
│       ├── router.py
│       └── endpoints/
├── database/
└── schemas/
```

Endpoints funcionales actuales:

```text
GET /health
GET /api/v1/categories
GET /api/v1/preparation-areas
```

El endpoint actualmente en desarrollo es:

```text
POST /api/v1/products
```

---

## 15. SQLAlchemy vs Pydantic

No confundir modelos SQLAlchemy con schemas Pydantic.

Modelos SQLAlchemy:

```text
Product
Category
PreparationArea
```

Se utilizan para:

```python
select(...)
where(...)
join(...)
order_by(...)
db.add(...)
```

Schemas Pydantic:

```text
ProductCreate
ProductRead
CategoryRead
PreparationAreaRead
```

Se utilizan para:

- validar requests;
- definir response models;
- serializar respuestas de la API.

No usar schemas Pydantic dentro de consultas SQLAlchemy.

---

## 16. Sesiones de base de datos

La aplicación utiliza `SessionLocal` y una dependencia `get_db()`.

Las sesiones deben cerrarse correctamente después de cada request.

No crear conexiones globales manuales para cada endpoint.

---

## 17. Escrituras transaccionales

Las operaciones que crean múltiples registros relacionados deben ser atómicas.

Ejemplo:

Crear un producto implica potencialmente:

```text
Product
ProductVariant
BranchProductVariant
```

La operación completa debe seguir:

```text
todo funciona → COMMIT
algo falla    → ROLLBACK
```

No dejar registros parcialmente creados.

---

## 18. Seguridad del contexto

El frontend no debe ser considerado una fuente confiable para determinar el tenant.

No confiar libremente en valores enviados por frontend como:

```text
organization_id
business_id
branch_id
```

El backend debe resolver y validar el contexto organizacional.

Actualmente algunos endpoints utilizan temporalmente:

```text
grupo_kiki
kiki_sushi
santa_rosa
```

porque autenticación/contexto todavía no está implementado.

Esta solución es temporal.

---

## 19. Frontend

El sistema tendrá interfaces diferenciadas.

### Admin Dashboard

Administración de:

- catálogo;
- usuarios;
- inventario;
- reportes;
- configuración;
- promociones;
- sucursales.

### POS

Interfaz operativa distinta para:

- meseros;
- cajeros;
- cobros;
- pedidos;
- comandas.

No asumir que administrador, cajero y mesero utilizan la misma experiencia de usuario.

---

## 20. Flujo de desarrollo recomendado

Para cada nueva funcionalidad:

```text
1. Entender el problema.
2. Revisar modelo de dominio.
3. Diseñar request/response.
4. Implementar backend.
5. Probar con Postman.
6. Verificar PostgreSQL cuando corresponda.
7. Crear o conectar frontend.
8. Probar flujo extremo a extremo.
9. Revisar cambios.
10. Commit.
```

No implementar varias funcionalidades grandes simultáneamente.

---

## 21. Git

Antes de cambios importantes:

```text
git status
git diff
```

No incluir:

```text
.env
credenciales
contraseñas
secretos
```

No hacer `git push` automáticamente salvo instrucción explícita.

No realizar commits automáticos salvo instrucción explícita.

---

## 22. Acciones que requieren revisión explícita

No ejecutar automáticamente:

```text
DROP
DELETE destructivos
alembic downgrade
alembic upgrade head
eliminación de volúmenes Docker
reset de PostgreSQL
reescritura de migraciones aplicadas
force push
```

Presentar primero el cambio y explicar sus consecuencias.

---

## 23. Dependencias

No instalar nuevas dependencias sin:

1. explicar por qué son necesarias;
2. comprobar que no existe ya una solución en el stack;
3. actualizar `requirements.txt` cuando corresponda.

---

## 24. Regla general para agentes

Antes de modificar código:

1. inspeccionar los archivos relacionados;
2. respetar la arquitectura existente;
3. implementar únicamente el alcance solicitado;
4. mantener cambios pequeños;
5. ejecutar las pruebas pertinentes;
6. informar qué se modificó y por qué.

Si existe una discrepancia entre estas reglas y el código existente, señalarla antes de realizar un cambio arquitectónico.