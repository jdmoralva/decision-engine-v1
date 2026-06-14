type Fetcher = typeof fetch;


function resolveFetcher(fetcher?: Fetcher): Fetcher {
  return fetcher ?? globalThis.fetch.bind(globalThis);
}


async function readJson<T>(responseOrPromise: Response | Promise<Response>): Promise<T> {
  const response = await responseOrPromise;
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { error?: { message?: string } }
      | null;
    throw new Error(payload?.error?.message ?? `La operacion fallo con estado ${response.status}.`);
  }
  return (await response.json()) as T;
}


export type AttachmentMetadata = {
  attachment_id: string;
  request_id: string;
  original_filename: string;
  mime_type: string;
  uploaded_at: string;
  uploaded_by: {
    user_id?: string | null;
    username: string;
  };
  entry_count: number;
};


export type AttachmentManifest = {
  attachment_id: string;
  request_id: string;
  original_filename: string;
  entries: Array<{
    path: string;
    size: number;
    compressed_size: number;
  }>;
};


export class AttachmentsApiClient {
  private readonly fetcher: Fetcher;

  constructor(
    private readonly accessToken: string,
    fetcher?: Fetcher,
  ) {
    this.fetcher = resolveFetcher(fetcher);
  }

  list(requestId: string): Promise<AttachmentMetadata[]> {
    return readJson<AttachmentMetadata[]>(
      this.fetcher(`/api/v1/credit-requests/${requestId}/attachments`, {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      }),
    );
  }

  upload(requestId: string, file: File): Promise<AttachmentMetadata> {
    const form = new FormData();
    form.set("file", file);
    return readJson<AttachmentMetadata>(
      this.fetcher(`/api/v1/credit-requests/${requestId}/attachments`, {
        method: "POST",
        headers: { Authorization: `Bearer ${this.accessToken}` },
        body: form,
      }),
    );
  }

  getManifest(requestId: string, attachmentId: string): Promise<AttachmentManifest> {
    return readJson<AttachmentManifest>(
      this.fetcher(`/api/v1/credit-requests/${requestId}/attachments/${attachmentId}/manifest`, {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      }),
    );
  }

  async download(requestId: string, attachmentId: string): Promise<Blob> {
    const response = await this.fetcher(
      `/api/v1/credit-requests/${requestId}/attachments/${attachmentId}/download`,
      { headers: { Authorization: `Bearer ${this.accessToken}` } },
    );
    if (!response.ok) {
      throw new Error(`La operacion fallo con estado ${response.status}.`);
    }
    return response.blob();
  }
}
