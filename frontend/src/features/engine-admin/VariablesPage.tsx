import { FormEvent, useState } from "react";

import { EngineAdminApiClient, EngineAdminWorkspaceState } from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function VariablesPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleCreateVariable(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const variableKey = String(formData.get("variableKey") ?? "").trim();
    const name = String(formData.get("name") ?? "").trim();
    const businessMeaning = String(formData.get("businessMeaning") ?? "").trim();
    const dataType = String(formData.get("dataType") ?? "").trim();
    const allowedSource = String(formData.get("allowedSource") ?? "").trim();
    const required = formData.get("required") === "on";

    setIsSubmitting(true);
    try {
      const variable = await client.createVariable(workspace.productCode, {
        variableKey,
        name,
        businessMeaning,
        dataType,
        required,
        allowedSource,
      });
      onWorkspaceChange({ variableId: variable.id });
      onNotice(`Variable ${variable.variableKey} creada.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear la variable.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivateVariable() {
    if (workspace.variableId === null) {
      onNotice("Primero crea una variable.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.activateVariable(workspace.variableId);
      onNotice("Variable activada.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar la variable.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCreateCatalog() {
    if (workspace.variableId === null) {
      onNotice("Primero crea una variable.");
      return;
    }

    setIsSubmitting(true);
    try {
      const catalog = await client.createVariableCatalog(workspace.productCode, [
        {
          productVariableId: workspace.variableId,
          requiredInRuntime: true,
          sourcePolicyPayload: { allowedSource: "campaign_db" },
        },
      ]);
      onWorkspaceChange({ catalogId: catalog.id });
      onNotice(`Catalogo v${catalog.versionNumber} creado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear el catalogo.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivateCatalog() {
    if (workspace.catalogId === null) {
      onNotice("Primero crea un catalogo.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.activateVariableCatalog(workspace.catalogId);
      onNotice("Catalogo activado.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar el catalogo.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Variables y catalogos</h2>
      <p className="workspace-hint">
        Las variables y catalogos se administran sobre el producto actual. Los retirados o eliminados quedan fuera de esta vista operativa.
      </p>
      <form className="admin-form" onSubmit={handleCreateVariable}>
        <label>
          Clave de variable
          <input name="variableKey" type="text" defaultValue="validated_income" />
        </label>
        <label>
          Nombre
          <input name="name" type="text" defaultValue="Ingreso validado" />
        </label>
        <label>
          Significado de negocio
          <textarea name="businessMeaning" defaultValue="Ingreso aprobado para reglas." />
        </label>
        <label>
          Tipo de dato
          <select name="dataType" defaultValue="number">
            <option value="number">number</option>
            <option value="integer">integer</option>
            <option value="string">string</option>
            <option value="boolean">boolean</option>
          </select>
        </label>
        <label>
          <input
            name="required"
            type="checkbox"
            defaultChecked={true}
          />
          Requerida en runtime
        </label>
        <label>
          Origen permitido
          <select name="allowedSource" defaultValue="campaign_db">
            <option value="campaign_db">campaign_db</option>
            <option value="user_input">user_input</option>
            <option value="both">both</option>
          </select>
        </label>
        <button className="primary-button" type="submit" disabled={isSubmitting}>
          Crear variable draft
        </button>
      </form>
      <div className="action-row">
        <button className="secondary-button" type="button" onClick={handleActivateVariable} disabled={isSubmitting}>
          Activar variable
        </button>
        <button className="secondary-button" type="button" onClick={handleCreateCatalog} disabled={isSubmitting}>
          Crear catalogo
        </button>
        <button className="secondary-button" type="button" onClick={handleActivateCatalog} disabled={isSubmitting}>
          Activar catalogo
        </button>
      </div>
      <p className="workspace-hint">Variable: {workspace.variableId ?? "pendiente"}</p>
      <p className="workspace-hint">Catalogo: {workspace.catalogId ?? "pendiente"}</p>
      <p className="workspace-hint">Workflow alineado: {workspace.workflowCode || "sin definir"}</p>
    </section>
  );
}
