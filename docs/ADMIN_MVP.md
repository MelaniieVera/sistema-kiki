# Panel administrativo de Kiki Sushi

El catálogo de Santa Rosa permite listar y buscar productos, consultar su ficha, crear un producto con una o más presentaciones y editar el producto y todas sus presentaciones desde un solo formulario. La API resuelve el negocio y la sucursal. El precio, el área y la disponibilidad se guardan por presentación en la sucursal.

## Ejecutar para pruebas locales

Con PostgreSQL local ya inicializado y la configuración existente en el archivo `.env` del repositorio, inicia el backend desde la raíz.

```sh
cd backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal, desde la raíz, inicia el frontend.

```sh
cd frontend
npm run dev -- --hostname 127.0.0.1
```

Abre [Productos](http://127.0.0.1:3000/admin/productos). Si FastAPI usa otro puerto, configura `KIKI_API_ORIGIN` antes de iniciar Next.js. El panel está previsto para el entorno local de pruebas mientras se implementa la autenticación y el control de acceso.

## Verificar el flujo

1. Comprueba que el listado refleje el catálogo y que la búsqueda encuentre un producto por nombre o código.
2. Crea un producto con dos presentaciones y áreas válidas. Confirma sus precios en la ficha. Repite el nombre para verificar el aviso de duplicado.
3. Abre «Editar producto», cambia el nombre, ajusta el precio de una presentación y agrega otra. Recarga el listado y abre de nuevo la ficha para comprobar que se guardaron.
4. Cambia la disponibilidad de una presentación y vuelve a abrir la ficha para verificar el cambio.

El POST acepta una lista `variants` y sigue aceptando `variant` para clientes existentes. El listado y la ficha muestran las presentaciones asignadas a Santa Rosa. En el PATCH, cada entrada de `variants` con ID actualiza una presentación y cada entrada sin ID crea una nueva. El producto y sus presentaciones se guardan en la misma transacción. Los códigos son estables después de la creación.

## Siguientes entregas

- Autenticación, permisos y contexto de sucursal por usuario.
- Interfaz operativa POS independiente.
