# Sistema Kiki — Estado actual del proyecto

## 1. Estado general

Sistema Kiki ya cuenta con una base sólida de:

- PostgreSQL;
- SQLAlchemy;
- Alembic;
- multitenancy;
- RBAC;
- catálogo base;
- FastAPI;
- Pydantic;
- endpoints iniciales;
- pruebas manuales con Postman.

El proyecto está en transición desde la fase de infraestructura/base de datos hacia la fase de API funcional y panel administrativo.

---

## 2. Estructura organizacional actual

La estructura real inicial es:

```text
Grupo Kiki
├── Kiki Sushi
│   └── Santa Rosa
└── Rivana
    └── Santa Rosa
```

Los códigos utilizados son:

```text
organization:
grupo_kiki

businesses:
kiki_sushi
rivana

branch:
santa_rosa
```

---

## 3. Tablas existentes

Actualmente existen, entre otras, las siguientes tablas:

```text
organizations
businesses
branches

users
roles
permissions
role_permissions
user_branch_roles

categories
preparation_areas

products
product_variants
branch_product_variants
```

---

## 4. Multitenancy

El sistema ya protege relaciones importantes mediante foreign keys y constraints.

Jerarquía:

```text
Organization
    ↓
Business
    ↓
Branch
```

Se han utilizado foreign keys compuestas en varias partes del esquema para evitar referencias cruzadas entre organizaciones, negocios o sucursales incorrectas.

---

## 5. RBAC

El núcleo de roles y permisos está creado.

Modelo:

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

Esto permite asignar roles diferentes al mismo usuario según la sucursal.

El seed correspondiente es:

```text
database/seeds/002_rbac.sql
```

---

## 6. Seeds actuales

Actualmente el proyecto utiliza:

```text
database/seeds/
├── 001_core.sql
├── 002_rbac.sql
└── 003_catalog.sql
```

### 001_core.sql

Crea de forma idempotente:

- Grupo Kiki;
- Kiki Sushi;
- Rivana;
- Kiki Sushi / Santa Rosa;
- Rivana / Santa Rosa.

Este archivo fue creado posteriormente porque esos registros originalmente habían sido insertados manualmente en PostgreSQL.

### 002_rbac.sql

Inicializa:

- permisos;
- roles;
- relaciones rol-permiso.

### 003_catalog.sql

Inicializa el catálogo base de Kiki Sushi:

Categorías:

```text
1  Entradas
2  Makis
3  Onigiris
4  Nigiris
5  Rolls
6  Tempura
7  Especiales
8  Rolls Premium
9  Fuertes
10 Ramen
11 Poke Bowls
12 Bebidas
13 Fénix
```

Áreas activas:

```text
kitchen → Cocina
bar     → Barra
```

El área antigua `sushi` permanece en la base como registro inactivo.

---

## 7. Diseño del catálogo

La estructura definida es:

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

Representa el producto comercial.

Ejemplo:

```text
Gyozas
```

### ProductVariant

Representa una presentación vendible.

Ejemplo:

```text
5 unidades
```

### BranchProductVariant

Contiene información dependiente de sucursal:

- precio;
- disponibilidad;
- estado;
- área de preparación.

El precio no debe almacenarse directamente en `Product`.

---

## 8. Áreas de preparación

Kiki Santa Rosa utiliza únicamente:

```text
Cocina
Barra
```

La categoría no determina automáticamente el área.

Ejemplos:

```text
Fénix Blonde
Categoría: Fénix
Área: Barra

Hamburguesa Fénix
Categoría: Fénix
Área: Cocina
```

La asignación se realiza mediante:

```text
branch_product_variants.preparation_area_id
```

---

## 9. FastAPI

La aplicación FastAPI está funcionando.

Archivo principal:

```text
backend/app/main.py
```

Endpoint de salud:

```http
GET /health
```

Probado correctamente desde navegador y Postman.

---

## 10. API v1

La API utiliza el prefijo:

```text
/api/v1
```

Estructura aproximada:

```text
backend/app/
├── main.py
├── api/
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           ├── categories.py
│           ├── preparation_areas.py
│           └── products.py
├── database/
│   ├── connection.py
│   └── models/
└── schemas/
    ├── category.py
    ├── preparation_area.py
    └── product.py
```

---

## 11. Endpoints funcionales

Funcionan y fueron probados con Postman:

```http
GET /health

GET /api/v1/categories

GET /api/v1/preparation-areas
```

### GET /api/v1/categories

Devuelve únicamente categorías activas de:

```text
Grupo Kiki
→ Kiki Sushi
```

ordenadas por:

```text
display_order
```

### GET /api/v1/preparation-areas

Devuelve únicamente áreas activas de:

```text
Grupo Kiki
→ Kiki Sushi
→ Santa Rosa
```

Actualmente devuelve:

```text
Barra
Cocina
```

---

## 12. Schemas Pydantic existentes

Existen schemas para:

```text
CategoryRead
PreparationAreaRead

ProductCreate
ProductVariantCreate

ProductRead
ProductVariantRead
```

---

## 13. Request previsto para crear productos

El request conceptual actual es:

```json
{
  "category_id": "UUID",
  "name": "Gyozas",
  "description": "Gyozas rellenas de cerdo...",
  "is_active": true,
  "variant": {
    "name": "5 unidades",
    "price": 4.50,
    "preparation_area_id": "UUID",
    "is_available": true
  }
}
```

El frontend no debe enviar directamente:

```text
organization_id
business_id
branch_id
```

El backend debe resolver y validar ese contexto.

---

## 14. Endpoint actualmente en desarrollo

El siguiente endpoint está iniciado pero no terminado:

```http
POST /api/v1/products
```

Archivo:

```text
backend/app/api/v1/endpoints/products.py
```

Actualmente ya se empezó a implementar:

### Validación de categoría

Debe comprobar que:

- `category_id` existe;
- pertenece a `grupo_kiki`;
- pertenece a `kiki_sushi`;
- está activa.

### Validación de área de preparación

Debe comprobar que:

- `preparation_area_id` existe;
- pertenece a `grupo_kiki`;
- pertenece a `kiki_sushi`;
- pertenece a `santa_rosa`;
- está activa.

---

## 15. Punto exacto donde continuar

El siguiente trabajo debe comenzar después de las validaciones anteriores.

Debe resolverse el contexto:

```text
organization_id
business_id
branch_id
```

a partir de los registros ya validados.

Después implementar, en este orden:

```text
1. Resolver/generar code del Product.
2. Resolver/generar code del ProductVariant.
3. Crear Product.
4. Crear ProductVariant.
5. Crear BranchProductVariant.
6. Ejecutar todo dentro de una sola transacción.
7. Hacer COMMIT únicamente si toda la operación funciona.
8. Hacer ROLLBACK si ocurre un error.
9. Construir ProductRead.
10. Registrar el router de products.
11. Probar POST /api/v1/products con Postman.
```

No saltar directamente al frontend antes de comprobar correctamente el endpoint en Postman.

---

## 16. Primer producto real previsto para pruebas

Los primeros productos reales disponibles para pruebas pertenecen a la categoría:

```text
Entradas
```

Ejemplo útil:

```text
Gyozas
Presentación: 5 unidades
Precio: 4.50
Área: Cocina
```

Este producto puede utilizarse como primer caso de prueba de `POST /api/v1/products`.

---

## 17. Frontend

Todavía no se ha comenzado la implementación funcional del frontend administrativo.

La intención es desarrollar backend y frontend por pequeñas rebanadas verticales:

```text
Endpoint
↓
Postman
↓
Frontend que consume el endpoint
↓
siguiente funcionalidad
```

El primer formulario previsto es:

```text
Nuevo producto
```

con campos como:

```text
Categoría
Nombre
Descripción
Presentación
Precio
Área de preparación
Disponibilidad
```

---

## 18. Próxima fase después de POST /products

Una vez que la creación de productos funcione:

```text
GET /api/v1/products
PATCH /api/v1/products/{id}
```

y comenzar el formulario administrativo de catálogo.

Después se avanzará hacia:

```text
Orders
OrderItems
Kitchen Tickets
Payments
Cash Sessions
Inventory
Promotions
Wallet / Loyalty
```

---

## 19. Estado resumido

```text
PostgreSQL                  ✓
SQLAlchemy                  ✓
Alembic                     ✓
Multitenancy                ✓
RBAC                        ✓
Seeds reproducibles         ✓
Catálogo estructural        ✓
Categorías reales           ✓
Áreas reales                ✓
FastAPI                     ✓
Postman                     ✓
GET categories              ✓
GET preparation-areas       ✓
Schemas products            ✓
POST products               EN DESARROLLO
Frontend admin              PENDIENTE
POS                         PENDIENTE
Orders                      PENDIENTE
KDS                         PENDIENTE
Caja                        PENDIENTE
Inventario                  PENDIENTE
Loyalty                     PENDIENTE
```