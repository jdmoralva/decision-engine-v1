import { useEffect, useState } from "react";

import {
  AttachmentsApiClient,
  type AttachmentManifest,
  type AttachmentMetadata,
} from "../../services/attachments-api";
import { UploadForm } from "./upload-form";


type AttachmentsPanelProps = {
  client: AttachmentsApiClient;
  requestId: string;
  canUpload: boolean;
};


export function AttachmentsPanel({ client, requestId, canUpload }: AttachmentsPanelProps) {
  const [attachments, setAttachments] = useState<AttachmentMetadata[]>([]);
  const [manifestById, setManifestById] = useState<Record<string, AttachmentManifest>>({});
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadAttachments() {
    setError(null);
    try {
      setAttachments(await client.list(requestId));
    } catch (caughtError) {
      setAttachments([]);
      setError(caughtError instanceof Error ? caughtError.message : "No se pudieron cargar los adjuntos.");
    }
  }

  useEffect(() => {
    void loadAttachments();
  }, [requestId]);

  async function handleUpload(file: File) {
    setError(null);
    setNotice(null);
    try {
      await client.upload(requestId, file);
      setNotice("ZIP cargado correctamente.");
      await loadAttachments();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo cargar el ZIP.");
    }
  }

  async function handleManifest(attachmentId: string) {
    setError(null);
    try {
      const manifest = await client.getManifest(requestId, attachmentId);
      setManifestById((current) => ({ ...current, [attachmentId]: manifest }));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo leer el contenido del ZIP.");
    }
  }

  async function handleDownload(attachmentId: string) {
    setError(null);
    setNotice(null);
    try {
      await client.download(requestId, attachmentId);
      setNotice("Descarga preparada correctamente.");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo descargar el adjunto.");
    }
  }

  return (
    <div className="session-panel">
      <h4>Adjuntos ZIP</h4>
      {canUpload ? <UploadForm onUpload={handleUpload} /> : null}
      {notice ? <p className="success-banner">{notice}</p> : null}
      {error ? <p className="error-banner">{error}</p> : null}

      {attachments.map((attachment) => (
        <div key={attachment.attachment_id}>
          <p>
            {attachment.original_filename} | {attachment.entry_count} archivos
          </p>
          <div className="tab-strip">
            <button className="secondary-button" type="button" onClick={() => handleManifest(attachment.attachment_id)}>
              Ver contenido
            </button>
            <button className="secondary-button" type="button" onClick={() => handleDownload(attachment.attachment_id)}>
              Descargar ZIP
            </button>
          </div>
          {manifestById[attachment.attachment_id]?.entries.map((entry) => (
            <p key={`${attachment.attachment_id}:${entry.path}`}>{entry.path}</p>
          ))}
        </div>
      ))}
    </div>
  );
}
