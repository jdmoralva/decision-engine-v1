import { useState, type MouseEvent } from "react";

import type { PlatformProduct, PlatformProductAction } from "../platform/catalog-types";

type ProductCardProps = {
  product: PlatformProduct;
  onOpenProduct: (productCode: string) => void;
};

export function ProductCard({ product, onOpenProduct }: ProductCardProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  function handleOpenProduct() {
    onOpenProduct(product.productCode);
    setIsMenuOpen(false);
  }

  function handleQuickActionClick(action: PlatformProductAction) {
    if (action.key === "services") {
      handleOpenProduct();
    }
  }

  function handleMenuToggle(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation();
    setIsMenuOpen((current) => !current);
  }

  function handleMenuAction(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation();
  }

  return (
    <article className="product-card">
      <div className="product-card-header">
        <div>
          <p className="product-card-code">{product.productCode}</p>
          <h3>{product.name}</h3>
        </div>

        <div className="product-card-toolbar">
          <span className={`environment-pill environment-pill--${product.environmentTone}`}>
            {product.environmentLabel}
          </span>
          <button
            aria-expanded={isMenuOpen}
            aria-label={`Acciones de ${product.name}`}
            className="icon-button"
            type="button"
            onClick={handleMenuToggle}
          >
            ...
          </button>
        </div>
      </div>

      <p className="workspace-hint">
        Entrada visual al producto con accesos rapidos y navegacion protegida.
      </p>

      <div className="product-quick-actions">
        {product.quickActions.map((action) => (
          <button
            className={action.key === "services" ? "primary-button" : "secondary-button"}
            key={action.key}
            type="button"
            onClick={() => handleQuickActionClick(action)}
          >
            {action.label}
          </button>
        ))}
      </div>

      {isMenuOpen ? (
        <div className="product-menu" role="menu">
          {product.menuActions.map((action) => (
            <button
              className="product-menu-action"
              key={action.key}
              role="menuitem"
              type="button"
              onClick={handleMenuAction}
            >
              {action.label}
            </button>
          ))}
        </div>
      ) : null}

      <button
        aria-label={`Abrir producto ${product.name}`}
        className="product-open-button"
        type="button"
        onClick={handleOpenProduct}
      >
        Abrir producto
      </button>
    </article>
  );
}
