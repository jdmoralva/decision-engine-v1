import { FormEvent, useState } from "react";

import { EngineAdminApiClient, EngineAdminWorkspaceState } from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function ProductsPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleCreateProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      const product = await client.createProduct({
        productCode: workspace.productCode,
        name: workspace.productName,
        description: "Producto administrado desde UI.",
      });
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
      onNotice(`Producto ${product.productCode} activado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar el producto.");
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
    </section>
  );
}
