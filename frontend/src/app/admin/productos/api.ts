export type Option = { id: string; name: string };

export type Variant = {
  id: string;
  name: string;
  price: string;
  preparation_area_id: string | null;
  is_available: boolean;
};

export type Product = {
  id: string;
  category_id: string;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
  variants: Variant[];
};

export async function catalogRequest<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/kiki/${path}`, { cache: "no-store", ...options });
  } catch {
    throw new Error("No se pudo conectar al catálogo. Intenta de nuevo.");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const messages: Record<string, string> = {
      "Category not found": "La categoría ya no está disponible.",
      "Preparation area not found": "El área de preparación ya no está disponible.",
      "Product not found": "No se encontró el producto.",
      "Variant not found": "No se encontró la presentación en esta sucursal.",
      "Variant code already exists for this product": "Dos presentaciones tienen el mismo código. Usa nombres distintos.",
      "Branch not found": "No se encontró la sucursal Santa Rosa.",
      "Product code already exists for this business": "Ya existe un producto con ese código.",
    };
    const message = typeof body?.detail === "string" ? messages[body.detail] : undefined;
    throw new Error(message ?? (response.status === 422
      ? "Revisa los datos del producto y el formato del precio."
      : "No se pudo completar la operación. Comprueba que la API esté disponible."));
  }
  return response.json();
}

export function messageOf(error: unknown) {
  return error instanceof Error ? error.message : "Ocurrió un error al consultar el catálogo.";
}

export const dollars = new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" });
