import { useNavigate } from "react-router-dom";

import { platformProducts } from "../platform/platform-seed-data";
import { ProductCard } from "./ProductCard";

export function ProductCatalogPage() {
  const navigate = useNavigate();

  function handleOpenProduct(productCode: string) {
    navigate(`/productos/${productCode}/servicios`);
  }

  return (
    <section className="product-catalog-page">
      <div className="catalog-header">
        <div>
          <p className="eyebrow">Plataforma</p>
          <h2>Productos</h2>
          <p className="workspace-hint">
            Explora los productos disponibles y entra a sus servicios con una sesion valida.
          </p>
        </div>
        <button className="secondary-button" type="button">
          Crear producto
        </button>
      </div>

      <div className="product-catalog-grid">
        {platformProducts.map((product) => (
          <ProductCard key={product.productCode} product={product} onOpenProduct={handleOpenProduct} />
        ))}
      </div>
    </section>
  );
}
