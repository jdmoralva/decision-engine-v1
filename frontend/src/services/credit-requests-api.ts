type Fetcher = typeof fetch;


function resolveFetcher(fetcher?: Fetcher): Fetcher {
  return fetcher ?? globalThis.fetch.bind(globalThis);
}


async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { error?: { message?: string } }
      | null;
    throw new Error(payload?.error?.message ?? `La operacion fallo con estado ${response.status}.`);
  }
  return (await response.json()) as T;
}


async function readText(response: Response): Promise<string> {
  if (!response.ok) {
    const payload = await response.text();
    throw new Error(payload || `La operacion fallo con estado ${response.status}.`);
  }
  return response.text();
}


export type CreditRequestDocumentRef = {
  document_type: string;
  document_number: string;
};

export type CreditRequestSummary = {
  request_id: string;
  product_code: string;
  evaluation_id?: string | null;
  workflow_code?: string | null;
  status: string;
  document: CreditRequestDocumentRef;
  campaign_code?: string | null;
  requested_amount: number;
  comment: string;
  created_by: {
    user_id?: string | null;
    username: string;
  };
};

export type CreditRequestDetail = CreditRequestSummary & {
  customer_name?: string | null;
  created_at: string;
  updated_at: string;
  offered_amount?: number | null;
  installment_amount?: number | null;
  term_months?: number | null;
  rate?: number | null;
  status_history: Array<{
    status: string;
    comment?: string | null;
    changed_by: {
      user_id?: string | null;
      username: string;
    };
    changed_at: string;
  }>;
  attachments: Array<{
    attachment_id: string;
    original_filename: string;
    mime_type: string;
    uploaded_at: string;
  }>;
};

export type CreditRequestQueueItem = {
  request_id: string;
  product_code: string;
  workflow_code?: string | null;
  evaluation_id?: string | null;
  document: CreditRequestDocumentRef;
  customer_name?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  available_actions: string[];
};

export type CreditRequestQueueResponse = {
  applied_filters: Record<string, string>;
  items: CreditRequestQueueItem[];
};

export class CreditRequestsApiClient {
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

  create(payload: Record<string, unknown>): Promise<CreditRequestSummary> {
    return this.request("/api/v1/credit-requests", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  getDetail(requestId: string): Promise<CreditRequestDetail> {
    return this.request(`/api/v1/credit-requests/${requestId}`);
  }

  listQueue(status?: string): Promise<CreditRequestQueueResponse> {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this.request(`/api/v1/credit-requests${query}`);
  }

  async exportQueue(status?: string): Promise<string> {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    const response = await this.fetcher(`/api/v1/credit-requests/export${query}`, {
      headers: { Authorization: `Bearer ${this.accessToken}` },
    });
    return readText(response);
  }

  transition(requestId: string, targetStatus: string, changedBy: string, comment?: string): Promise<CreditRequestSummary> {
    return this.request(`/api/v1/credit-requests/${requestId}/status-transitions`, {
      method: "POST",
      body: JSON.stringify({
        target_status: targetStatus,
        comment,
        changed_by: { username: changedBy },
      }),
    });
  }
}
