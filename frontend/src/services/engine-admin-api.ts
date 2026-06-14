type Fetcher = typeof fetch;


function resolveFetcher(fetcher?: Fetcher): Fetcher {
  return fetcher ?? globalThis.fetch.bind(globalThis);
}

export type ProductResponse = {
  id: string;
  productCode: string;
  name: string;
  description?: string | null;
  status: string;
};

export type WorkflowResponse = {
  id: string;
  productCode: string;
  workflowCode: string;
  name: string;
  description?: string | null;
  status: string;
};

export type ProductVariableResponse = {
  id: string;
  productCode: string;
  variableKey: string;
  name: string;
  businessMeaning: string;
  description?: string | null;
  dataType: string;
  required: boolean;
  allowedSource: string;
  status: string;
};

export type VariableCatalogResponse = {
  id: string;
  productCode: string;
  versionNumber: number;
  status: string;
};

export type ParameterSetResponse = {
  id: string;
  productCode: string;
  workflowCode: string;
  versionNumber: number;
  status: string;
  payload: Record<string, unknown>;
};

export type PipelineStrategyResponse = {
  id: string;
  productCode: string;
  versionNumber: number;
  status: string;
};

export type RuleResponse = {
  id: string;
  productCode: string;
  workflowId: string;
  name: string;
  status: string;
  activeVersion: {
    id: string;
    versionNumber: number;
    status: string;
  };
};

export type WorkflowVersionResponse = {
  id: string;
  workflowId: string;
  versionNumber: number;
  status: string;
  variableCatalogVersionId: string;
  parameterSetId: string;
  pipelineStrategyId: string;
  ruleVersionIds: string[];
  changeNotes?: string | null;
};

export type PermissionResponse = {
  code: string;
  name: string;
  description?: string | null;
};

export type ProfilePermissionResponse = {
  roleCode: string;
  permissions: PermissionResponse[];
};

export type EngineAdminWorkspaceState = {
  productCode: string;
  productName: string;
  workflowCode: string;
  workflowId: string | null;
  variableId: string | null;
  catalogId: string | null;
  parameterSetId: string | null;
  pipelineStrategyId: string | null;
  ruleId: string | null;
  ruleVersionId: string | null;
  workflowVersionId: string | null;
  selectedRoleCode: string;
  selectedPermissionCodes: string[];
};

export const emptyEngineAdminWorkspaceState: EngineAdminWorkspaceState = {
  productCode: "",
  productName: "",
  workflowCode: "",
  workflowId: null,
  variableId: null,
  catalogId: null,
  parameterSetId: null,
  pipelineStrategyId: null,
  ruleId: null,
  ruleVersionId: null,
  workflowVersionId: null,
  selectedRoleCode: "admin_negocio",
  selectedPermissionCodes: [],
};

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { error?: { message?: string } }
      | null;
    throw new Error(payload?.error?.message ?? `La operacion fallo con estado ${response.status}.`);
  }

  return (await response.json()) as T;
}

export class EngineAdminApiClient {
  private readonly fetcher: Fetcher;

  constructor(
    private readonly accessToken: string,
    fetcher?: Fetcher,
  ) {
    this.fetcher = resolveFetcher(fetcher);
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await this.fetcher(path, {
      ...init,
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    });
    return readJson<T>(response);
  }

  createProduct(input: { productCode: string; name: string; description?: string }): Promise<ProductResponse> {
    return this.request("/api/v1/admin/engine/products", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  activateProduct(productCode: string): Promise<ProductResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/activation`, { method: "POST" });
  }

  retireProduct(productCode: string): Promise<ProductResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/retirement`, { method: "POST" });
  }

  async deleteProduct(productCode: string): Promise<void> {
    await this.request(`/api/v1/admin/engine/products/${productCode}`, { method: "DELETE" });
  }

  createWorkflow(productCode: string, input: { workflowCode: string; name: string; description?: string }): Promise<WorkflowResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/workflows`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  async deleteWorkflow(workflowId: string): Promise<void> {
    await this.request(`/api/v1/admin/engine/workflows/${workflowId}`, { method: "DELETE" });
  }

  createVariable(productCode: string, input: Record<string, unknown>): Promise<ProductVariableResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/variables`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  activateVariable(variableId: string): Promise<ProductVariableResponse> {
    return this.request(`/api/v1/admin/engine/variables/${variableId}/activation`, { method: "POST" });
  }

  createVariableCatalog(productCode: string, items: unknown[]): Promise<VariableCatalogResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/variable-catalogs`, {
      method: "POST",
      body: JSON.stringify({ items }),
    });
  }

  activateVariableCatalog(catalogId: string): Promise<VariableCatalogResponse> {
    return this.request(`/api/v1/admin/engine/variable-catalogs/${catalogId}/activation`, { method: "POST" });
  }

  createParameterSet(productCode: string, workflowCode: string, payload: Record<string, unknown>): Promise<ParameterSetResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/parameter-sets`, {
      method: "POST",
      body: JSON.stringify({ workflowCode, payload }),
    });
  }

  activateParameterSet(parameterSetId: string): Promise<ParameterSetResponse> {
    return this.request(`/api/v1/admin/engine/parameter-sets/${parameterSetId}/activation`, { method: "POST" });
  }

  createPipelineStrategy(
    productCode: string,
    input: { graphDefinition: Record<string, unknown>; nodes: unknown[] },
  ): Promise<PipelineStrategyResponse> {
    return this.request(`/api/v1/admin/engine/products/${productCode}/pipeline-strategies`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  activatePipelineStrategy(strategyId: string): Promise<PipelineStrategyResponse> {
    return this.request(`/api/v1/admin/engine/pipeline-strategies/${strategyId}/activation`, { method: "POST" });
  }

  createRule(workflowId: string, input: Record<string, unknown>): Promise<RuleResponse> {
    return this.request(`/api/v1/admin/engine/workflows/${workflowId}/rules`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  activateRuleVersion(ruleVersionId: string): Promise<RuleResponse> {
    return this.request(`/api/v1/admin/engine/rule-versions/${ruleVersionId}/activation`, { method: "POST" });
  }

  async deleteRule(ruleId: string): Promise<void> {
    await this.request(`/api/v1/admin/engine/rules/${ruleId}`, { method: "DELETE" });
  }

  createWorkflowVersion(workflowId: string, input: Record<string, unknown>): Promise<WorkflowVersionResponse> {
    return this.request(`/api/v1/admin/engine/workflows/${workflowId}/versions`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  activateWorkflowVersion(versionId: string): Promise<WorkflowVersionResponse> {
    return this.request(`/api/v1/admin/engine/workflow-versions/${versionId}/activation`, { method: "POST" });
  }

  getProfilePermissions(roleCode: string): Promise<ProfilePermissionResponse> {
    return this.request(`/api/v1/admin/engine/profiles/${roleCode}/permissions`);
  }

  replaceProfilePermissions(
    roleCode: string,
    permissionCodes: string[],
  ): Promise<ProfilePermissionResponse> {
    return this.request(`/api/v1/admin/engine/profiles/${roleCode}/permissions`, {
      method: "PUT",
      body: JSON.stringify({ permissionCodes }),
    });
  }
}

export async function runEngineAdminLifecycle(client: EngineAdminApiClient, state: EngineAdminWorkspaceState) {
  const product = await client.createProduct({
    productCode: state.productCode,
    name: state.productName,
    description: "Alta administrativa del producto.",
  });
  await client.activateProduct(product.productCode);
  const workflow = await client.createWorkflow(product.productCode, {
    workflowCode: state.workflowCode,
    name: "Workflow estandar",
    description: "Version inicial",
  });
  const variable = await client.createVariable(product.productCode, {
    variableKey: "validated_income",
    name: "Ingreso validado",
    businessMeaning: "Ingreso usado en la evaluacion",
    dataType: "number",
    required: true,
    allowedSource: "campaign_db",
  });
  await client.activateVariable(variable.id);
  const catalog = await client.createVariableCatalog(product.productCode, [
    {
      productVariableId: variable.id,
      requiredInRuntime: true,
      sourcePolicyPayload: { allowedSource: "campaign_db" },
    },
  ]);
  await client.activateVariableCatalog(catalog.id);
  const parameterSet = await client.createParameterSet(product.productCode, workflow.workflowCode, {
    min_score: 500,
  });
  await client.activateParameterSet(parameterSet.id);
  const pipeline = await client.createPipelineStrategy(product.productCode, {
    graphDefinition: { entryNode: "eligibility" },
    nodes: [{ nodeKey: "eligibility", nodeType: "rule_group", configPayload: { mode: "all" } }],
  });
  await client.activatePipelineStrategy(pipeline.id);
  const rule = await client.createRule(workflow.id, {
    name: "Regla base",
    ruleType: "eligibility",
    conditionExpression: "validated_income > 0",
    actionExpression: "allow",
    parameters: { threshold: 0 },
  });
  await client.activateRuleVersion(rule.activeVersion.id);
  const workflowVersion = await client.createWorkflowVersion(workflow.id, {
    variableCatalogVersionId: catalog.id,
    parameterSetId: parameterSet.id,
    pipelineStrategyId: pipeline.id,
    ruleVersionIds: [rule.activeVersion.id],
    changeNotes: "Publicacion inicial",
  });
  await client.activateWorkflowVersion(workflowVersion.id);

  return {
    product,
    workflow,
    variable,
    catalog,
    parameterSet,
    pipeline,
    rule,
    workflowVersion,
  };
}
