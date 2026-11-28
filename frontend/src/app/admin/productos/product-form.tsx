"use client";

import { useState, type FormEvent } from "react";
import { catalogRequest, messageOf, type Option, type Product, type Variant } from "./api";
import styles from "./products.module.css";

export function ProductForm({ product, categories, areas, onCancel, onSaved }: {
  product?: Product;
  categories: Option[];
  areas: Option[];
  onCancel: () => void;
  onSaved: (id: string) => void;
}) {
  const [presentations, setPresentations] = useState<{ key: string; variant?: Variant }[]>(
    () => product ? product.variants.map((variant) => ({ key: variant.id, variant })) : [{ key: "initial" }],
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (saving) return;
    const fields = new FormData(event.currentTarget);
    const name = String(fields.get("name")).trim();
    if (!name) {
      setError("Escribe el nombre del producto.");
      return;
    }
    const productFields = {
      name,
      description: String(fields.get("description")).trim() || null,
      category_id: String(fields.get("category")),
      is_active: fields.has("active"),
    };
    const productChanges = Object.fromEntries(Object.entries(productFields).filter(([key, value]) =>
      !product || product[key as keyof typeof productFields] !== value,
    ));
    const variants = [];
    for (const [index, { key, variant }] of presentations.entries()) {
      const values = {
        name: String(fields.get(`${key}-name`) ?? "").trim(),
        price: String(fields.get(`${key}-price`) ?? "").trim().replace(",", "."),
        preparation_area_id: String(fields.get(`${key}-area`) ?? ""),
        is_available: fields.has(`${key}-available`),
      };
      if (!values.name || !/^\d{1,10}(\.\d{1,2})?$/.test(values.price)) {
        setError(`Revisa el nombre y el precio de la presentación ${index + 1}. Usa hasta dos decimales, por ejemplo 4,50.`);
        return;
      }
      if (!variant) {
        variants.push(values);
        continue;
      }
      const changes = Object.fromEntries(Object.entries(values).filter(([field, value]) => {
        if (field === "price") return Number(value) !== Number(variant.price);
        if (field === "preparation_area_id") return value !== (variant.preparation_area_id ?? "");
        return variant[field as keyof typeof values] !== value;
      }));
      if (Object.keys(changes).length) variants.push({ id: variant.id, ...changes });
    }
    const body = { ...productChanges, ...(variants.length ? { variants } : {}) };

    setSaving(true);
    setError("");
    try {
      const saved = await catalogRequest<{ id: string }>(product ? `products/${product.id}` : "products", {
        method: product ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      onSaved(saved.id);
    } catch (failure) {
      setError(messageOf(failure));
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className={styles.card}>
      <h2>{product ? "Editar producto" : "Nuevo producto"}</h2>
      {error && <p className={styles.error} role="alert">{error}</p>}
      <fieldset disabled={saving} className={styles.fields}>
        <label>Nombre<input name="name" required maxLength={125} defaultValue={product?.name} /></label>
        <label>Categoría
          <select name="category" required defaultValue={product?.category_id ?? ""}>
            <option value="" disabled>Seleccionar categoría</option>
            {product && !categories.some(({ id }) => id === product.category_id) &&
              <option value={product.category_id}>Categoría actual inactiva</option>}
            {categories.map(({ id, name }) => <option key={id} value={id}>{name}</option>)}
          </select>
        </label>
        <label className={styles.full}>Descripción<textarea name="description" rows={3} maxLength={500} defaultValue={product?.description ?? ""} /></label>
        <label className={styles.check}><input name="active" type="checkbox" defaultChecked={product?.is_active ?? true} /> Producto activo</label>
      </fieldset>
      <section aria-labelledby="presentation-title">
        <h3 id="presentation-title">Presentaciones en Santa Rosa</h3>
        {presentations.map(({ key, variant }, index) => (
          <fieldset key={key} disabled={saving} className={styles.fields}>
            <legend>{variant?.name ?? `Presentación ${index + 1}`}</legend>
            <label>Nombre de la presentación
              <input name={`${key}-name`} required maxLength={125} defaultValue={variant?.name ?? (key === "initial" ? "Estándar" : "")} />
            </label>
            <label>Precio (USD)<input name={`${key}-price`} required inputMode="decimal" maxLength={13} defaultValue={variant?.price} /></label>
            <label>Área de preparación
              <select name={`${key}-area`} required={!variant} defaultValue={variant?.preparation_area_id ?? ""}>
                <option value="" disabled>{variant ? "Sin área asignada" : "Seleccionar área"}</option>
                {variant?.preparation_area_id && !areas.some(({ id }) => id === variant.preparation_area_id) &&
                  <option value={variant.preparation_area_id}>Área actual inactiva</option>}
                {areas.map(({ id, name }) => <option key={id} value={id}>{name}</option>)}
              </select>
            </label>
            <label className={styles.check}><input name={`${key}-available`} type="checkbox" defaultChecked={variant?.is_available ?? true} /> Disponible para venta</label>
            {!variant && (product || presentations.length > 1) &&
              <div><button type="button" onClick={() => setPresentations((items) => items.filter((item) => item.key !== key))}>Quitar presentación</button></div>}
          </fieldset>
        ))}
      </section>
      <div className={styles.actions}>
        <button type="button" disabled={saving} onClick={() => {
          const key = crypto.randomUUID();
          setPresentations((items) => [...items, { key }]);
        }}>Agregar presentación</button>
        <button className={styles.primary} disabled={saving}>{saving ? "Guardando…" : "Guardar producto"}</button>
        <button type="button" disabled={saving} onClick={onCancel}>Cancelar</button>
      </div>
    </form>
  );
}
