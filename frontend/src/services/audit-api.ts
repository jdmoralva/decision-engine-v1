import type { DecisionTraceResponse } from "./runtime-api";

type Fetcher = typeof fetch;


function resolveFetcher(fetcher?: Fetcher): Fetcher {
  return fetcher ?? globalThis.fetch.bind(globalThis);
}


async function readJson<T>(responsePromise: Promise<Response>): Promise<T> {
  const response = await responsePromise;
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { error?: { message?: string } }
      | null;
    throw new Error(payload?.error?.message ?? `La operacion fallo con estado ${response.status}.`);
  }
  return (await response.json()) as T;
}


export type AuditEventPage = {
  page: number;
  page_size: number;
  total: number;
  items: Array<{
    event_id: string;
    aggregate_id: string;
    aggregate_type: string;
    event_type: string;
    event_payload: Record<string, unknown>;
    created_by: {
      user_id?: string | null;
      username: string;
    };
    created_at: string;
  }>;
};


export class AuditApiClient {
  private readonly fetcher: Fetcher;

  constructor(
    private readonly accessToken: string,
    fetcher?: Fetcher,
  ) {
    this.fetcher = resolveFetcher(fetcher);
  }

  list(requestId: string, evaluationId?: string | null): Promise<AuditEventPage> {
    const query = new URLSearchParams({ request_id: requestId });
    if (evaluationId) {
      query.set("evaluation_id", evaluationId);
    }
    return readJson<AuditEventPage>(
      this.fetcher(`/api/v1/audit?${query.toString()}`, {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      }),
    );
  }

  getTrace(productCode: string, evaluationId: string): Promise<DecisionTraceResponse> {
    return readJson<DecisionTraceResponse>(
      this.fetcher(`/api/v1/loans/${productCode}/evaluaciones/${evaluationId}/trace`, {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      }),
    );
  }
}
