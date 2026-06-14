type Fetcher = typeof fetch;


function resolveFetcher(fetcher?: Fetcher): Fetcher {
  return fetcher ?? globalThis.fetch.bind(globalThis);
}

export type RuntimeDocumentRef = {
  document_type: string;
  document_number: string;
};

export type ConsultationResponse = {
  product_code: string;
  document: RuntimeDocumentRef;
  customer: {
    customer_id: string;
    full_name: string;
    customer_type?: string | null;
    profile_code?: string | null;
    sunedu_flag?: string | null;
    employment_status?: string | null;
    validated_income?: number | null;
  };
  campaigns: Array<{
    campaign_code: string;
    offered_amount?: number | null;
    rate?: number | null;
    term_months?: number | null;
    installment_amount?: number | null;
    metadata?: Record<string, string>;
  }>;
};

export type EvaluationResponse = {
  evaluation_id: string;
  product_code: string;
  eligible: boolean;
  alerts: string[];
  blocks: string[];
  applied_versions: {
    rule_set_version?: string | null;
    parameter_version?: string | null;
    pipeline_version?: string | null;
  };
  decision_trace_id: string;
  product_result?: Record<string, unknown> | null;
};

export type DecisionTraceResponse = {
  trace_id: string;
  evaluation_id: string;
  product_code: string;
  applied_versions: EvaluationResponse["applied_versions"];
  alerts: string[];
  blocks: string[];
  rules_applied: string[];
  consumed_variables: string[];
  produced_variables: string[];
  produced_effects: string[];
  nodes_executed: Array<{
    node_key: string;
    node_type: string;
    outcome: string;
    rules_applied: string[];
    consumed_variables: string[];
    produced_variables: string[];
    produced_effects: string[];
  }>;
  evidence: Array<{
    source_type: string;
    source_key: string;
    field_name: string;
    field_value: string;
    used_by_engine: boolean;
  }>;
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

export class RuntimeApiClient {
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

  consult(productCode: string, document: RuntimeDocumentRef): Promise<ConsultationResponse> {
    return this.request(`/api/v1/loans/${productCode}/consultas`, {
      method: "POST",
      body: JSON.stringify({ document }),
    });
  }

  evaluate(productCode: string, payload: Record<string, unknown>): Promise<EvaluationResponse> {
    return this.request(`/api/v1/loans/${productCode}/evaluaciones`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  getTrace(productCode: string, evaluationId: string): Promise<DecisionTraceResponse> {
    return this.request(`/api/v1/loans/${productCode}/evaluaciones/${evaluationId}/trace`);
  }
}
