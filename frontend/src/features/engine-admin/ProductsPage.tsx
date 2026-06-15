import { FormEvent, useEffect, useState } from "react";

import {
  AdminArtifactState,
  EngineAdminApiClient,
  EngineAdminWorkspaceState,
  ProductDetailResponse,
  ProductResponse,
} from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function ProductsPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [viewState, setViewState] = useState<AdminArtifactState>("active");
  const [products, setProducts] = useState<ProductResponse[]>([]);
  const [detail, setDetail] = useState<ProductDetailResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      try {
        const response = await client.listProducts(viewState);
        if (!cancelled) {
          setProducts(response.items);
        }
      } catch (error) {
        if (!cancelled) {
          onNotice(error instanceof Error ? error.message : "No se pudo cargar productos.");
        }
      }
    }

    void loadProducts();
    return () => {
      cancelled = true;
    };
  }, [client, onNotice, viewState]);

  async function handleRefresh() {
    const response = await client.listProducts(viewState);
    setProducts(response.items);
  }

  async function handleLoadDetail(productCode: string) {
    try {
      const response = await client.getProductDetail(productCode);
      setDetail(response);
      onWorkspaceChange({ productCode: response.productCode, productName: response.name });
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo cargar el detalle del producto.");
    }
  }

  async function handleCreateProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      const product = await client.createProduct({
        productCode: workspace.productCode,
        name: workspace.productName,
        description: "Producto administrado desde UI.",
      });
      await handleRefresh();
      await handleLoadDetail(product.productCode);
      onNotice(`Producto ${product.productCode} creado en draft.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear el producto.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivateProduct() {
    setIsSubmitting(true);
    try {
      const product = await client.activateProduct(workspace.productCode);
      await handleRefresh();
      await handleLoadDetail(product.productCode);
      onNotice(`Producto ${product.productCode} activado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar el producto.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRetireProduct() {
    setIsSubmitting(true);
    try {
      const product = await client.retireProduct(workspace.productCode);
      await handleRefresh();
      setDetail(null);
      onNotice(`Producto ${product.productCode} retirado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo retirar el producto.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteProduct() {
    setIsSubmitting(true);
    try {
      await client.deleteProduct(workspace.productCode);
      setDetail(null);
      await handleRefresh();
      onNotice(`Producto ${workspace.productCode} eliminado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo eliminar el producto.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCreateWorkflow(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      const workflow = await client.createWorkflow(workspace.productCode, {
        workflowCode: workspace.workflowCode,
        name: "Workflow estandar",
        description: "Workflow operativo inicial.",
      });
      onWorkspaceChange({ workflowId: workflow.id });
      onNotice(`Workflow ${workflow.workflowCode} creado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear el workflow.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Productos y workflows</h2>
      <div className="action-row">
        <button className="secondary-button" type="button" onClick={() => setViewState("active")} disabled={viewState === "active"}>
          Ver activos
        </button>
        <button className="secondary-button" type="button" onClick={() => setViewState("draft")} disabled={viewState === "draft"}>
          Ver draft
        </button>
      </div>

      <div className="workspace-hint">Vista actual: {viewState}</div>
      <form className="admin-form" onSubmit={handleCreateProduct}>
        <label className="field">
          <span>Codigo de producto</span>
          <input
            value={workspace.productCode}
            onChange={(event) => onWorkspaceChange({ productCode: event.target.value.toUpperCase() })}
          />
        </label>
        <label className="field">
          <span>Nombre del producto</span>
          <input
            value={workspace.productName}
            onChange={(event) => onWorkspaceChange({ productName: event.target.value })}
          />
        </label>
        <button className="primary-button" type="submit" disabled={isSubmitting}>
          Crear producto draft
        </button>
      </form>

      <div className="action-row">
        <button className="secondary-button" type="button" onClick={handleActivateProduct} disabled={isSubmitting}>
          Activar producto
        </button>
        <button className="secondary-button" type="button" onClick={handleRetireProduct} disabled={isSubmitting}>
          Retirar producto
        </button>
        <button className="secondary-button" type="button" onClick={handleDeleteProduct} disabled={isSubmitting}>
          Eliminar producto draft
        </button>
      </div>

      <form className="admin-form" onSubmit={handleCreateWorkflow}>
        <label className="field">
          <span>Workflow code</span>
          <input
            value={workspace.workflowCode}
            onChange={(event) => onWorkspaceChange({ workflowCode: event.target.value })}
          />
        </label>
        <button className="primary-button" type="submit" disabled={isSubmitting}>
          Crear workflow draft
        </button>
      </form>

      <p className="workspace-hint">Workflow actual: {workspace.workflowId ?? "pendiente"}</p>

      <div className="workspace-hint">Productos visibles: {products.length}</div>
      <ul className="feature-list">
        {products.map((product) => (
          <li key={product.id}>
            {product.productCode} · {product.name} · {product.status}{" "}
            <button className="secondary-button" type="button" onClick={() => void handleLoadDetail(product.productCode)}>
              Ver detalle
            </button>
          </li>
        ))}
      </ul>

      {detail ? (
        <div className="session-panel">
          <h3>Detalle del producto</h3>
          <p>
            {detail.productCode} · {detail.name}
          </p>
          <p>Aprobacion: {detail.approval.status === "pending" ? "pendiente" : detail.approval.approvedBy ?? "aprobado"}</p>
          <p>Retiro: {detail.retirement.performedAt ? detail.retirement.performedAt : "sin registro"}</p>
          <p>Eliminacion: {detail.deletion.performedAt ? detail.deletion.performedAt : "sin registro"}</p>
          <p>Workflows activos asociados: {detail.activeWorkflows.length}</p>
        </div>
      ) : null}
    </section>
  );
}
