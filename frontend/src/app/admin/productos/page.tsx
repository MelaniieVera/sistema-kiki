"use client";

import { useEffect, useState } from "react";
import { catalogRequest, dollars, messageOf, type Option, type Product } from "./api";
import { ProductForm } from "./product-form";
import styles from "./products.module.css";

type View =
  | { kind: "list" | "create" }
  | { kind: "detail"; id: string }
  | { kind: "edit"; product: Product };

function ProductDetail({ id, categories, areas, edit }: {
  id: string;
  categories: Option[];
  areas: Option[];
  edit: (product: Product) => void;
}) {
  const [product, setProduct] = useState<Product>();
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    catalogRequest<Product>(`products/${id}`, { signal: controller.signal })
      .then(setProduct)
      .catch((failure) => { if (!controller.signal.aborted) setError(messageOf(failure)); });
    return () => controller.abort();
  }, [id, attempt]);

  if (error) return <div className={styles.card}>
    <p role="alert" className={styles.error}>{error}</p>
    <button onClick={() => { setError(""); setAttempt(attempt + 1); }}>Reintentar</button>
  </div>;
  if (!product) return <p role="status">Cargando producto…</p>;

  return <section className={styles.card}>
    <div className={styles.heading}>
      <div><p className={styles.muted}>{categories.find(({ id }) => id === product.category_id)?.name ?? "Categoría inactiva"}</p><h2>{product.name}</h2></div>
      <button onClick={() => edit(product)}>Editar producto</button>
    </div>
    <p className={styles.muted}>{product.code} · {product.is_active ? "Activo" : "Inactivo"}</p>
    {product.description && <p className={styles.description}>{product.description}</p>}
    <h3>Presentaciones en Santa Rosa</h3>
    {product.variants.length === 0 && <p className={styles.muted}>Sin presentaciones asignadas a esta sucursal.</p>}
    {product.variants.map((variant) => <div className={styles.variant} key={variant.id}>
      <div><strong>{variant.name}</strong><div className={styles.muted}>
        {dollars.format(Number(variant.price))} · {areas.find(({ id }) => id === variant.preparation_area_id)?.name ??
          (variant.preparation_area_id ? "Área inactiva" : "Sin área asignada")} · {variant.is_available ? "Disponible" : "No disponible"}
      </div></div>
    </div>)}
  </section>;
}

export default function ProductsPage() {
  const [view, setView] = useState<View>({ kind: "list" });
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Option[]>([]);
  const [areas, setAreas] = useState<Option[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (view.kind !== "list") return;
    const controller = new AbortController();
    const options = { signal: controller.signal };
    Promise.all([
      catalogRequest<Product[]>("products", options),
      catalogRequest<Option[]>("categories", options),
      catalogRequest<Option[]>("preparation-areas", options),
    ]).then(([catalog, categoryOptions, areaOptions]) => {
      setProducts(catalog);
      setCategories(categoryOptions);
      setAreas(areaOptions);
    }).catch((failure) => {
      if (!controller.signal.aborted) setError(messageOf(failure));
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [view.kind, attempt]);

  function showList() {
    if (view.kind === "list") return;
    setLoading(true);
    setError("");
    setNotice("");
    setView({ kind: "list" });
  }

  function save(id: string) {
    setNotice(view.kind === "create" ? "Producto creado." : "Cambios guardados.");
    setView({ kind: "detail", id });
  }

  const visible = products.filter((product) =>
    `${product.name} ${product.code}`.toLocaleLowerCase("es").includes(search.trim().toLocaleLowerCase("es")),
  );

  return <div className={styles.shell}>
    <aside className={styles.sidebar}>
      <strong className={styles.brand}>Kiki Sushi</strong>
      <span className={styles.location}>Santa Rosa · Administración</span>
      <nav aria-label="Administración"><button onClick={showList}>Catálogo de productos</button></nav>
    </aside>
    <main className={styles.main}>
      <div className={styles.heading}>
        <h1>Productos</h1>
        {view.kind === "list"
          ? <button className={styles.primary} disabled={loading || !!error} onClick={() => {
            setNotice("");
            setView({ kind: "create" });
          }}>Nuevo producto</button>
          : <button onClick={showList}>Volver al catálogo</button>}
      </div>
      {notice && <p role="status" className={styles.notice}>{notice}</p>}
      {view.kind === "list" && (
        loading ? <p role="status">Cargando catálogo…</p> : error
          ? <div className={styles.card}>
            <p role="alert" className={styles.error}>{error}</p>
            <button onClick={() => { setLoading(true); setError(""); setAttempt(attempt + 1); }}>Reintentar</button>
          </div>
          : <section className={styles.card} aria-label="Listado de productos">
            <div className={styles.heading}>
              <label className={styles.search}>Buscar producto<input type="search" value={search} onChange={(event) => setSearch(event.target.value)} /></label>
              <span className={styles.muted}>{visible.length} de {products.length} productos</span>
            </div>
            {visible.length === 0 ? <p>{products.length ? "No hay resultados para esa búsqueda." : "Todavía no hay productos. Crea el primero desde este panel."}</p> :
              <div className={styles.tableWrap}><table>
                <thead><tr><th>Producto</th><th>Categoría</th><th>Precio (USD)</th><th>Estado</th><th>Acción</th></tr></thead>
                <tbody>{visible.map((product) => <tr key={product.id}>
                  <td><strong>{product.name}</strong><div className={styles.muted}>{product.code}</div></td>
                  <td>{categories.find(({ id }) => id === product.category_id)?.name ?? "Inactiva"}</td>
                  <td>{product.variants.map(({ price }) => dollars.format(Number(price))).join(" / ") || "—"}</td>
                  <td><span className={product.is_active ? styles.active : styles.inactive}>{product.is_active ? "Activo" : "Inactivo"}</span></td>
                  <td><button aria-label={`Ver ${product.name}`} onClick={() => setView({ kind: "detail", id: product.id })}>Ver</button></td>
                </tr>)}</tbody>
              </table></div>}
          </section>
      )}
      {view.kind === "detail" && <ProductDetail key={view.id} id={view.id} categories={categories} areas={areas}
        edit={(product) => { setNotice(""); setView({ kind: "edit", product }); }} />}
      {view.kind === "create" && <ProductForm categories={categories} areas={areas} onCancel={showList} onSaved={save} />}
      {view.kind === "edit" && <ProductForm product={view.product} categories={categories} areas={areas}
        onCancel={() => setView({ kind: "detail", id: view.product.id })} onSaved={save} />}
    </main>
  </div>;
}
