import { useEffect, useState } from "react";

import type { SessionMe } from "../../session-storage";
import {
  CreditRequestsApiClient,
  type CreditRequestQueueItem,
} from "../../services/credit-requests-api";
import { StatusActions } from "./status-actions";

type QueuePageProps = {
  client: CreditRequestsApiClient;
  me: SessionMe;
};


export function QueuePage({ client, me }: QueuePageProps) {
  const [queueStatus, setQueueStatus] = useState("registrada");
  const [items, setItems] = useState<CreditRequestQueueItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [exportPreview, setExportPreview] = useState("");

  async function loadQueue() {
    setError(null);
    try {
      const response = await client.listQueue(queueStatus);
      setItems(response.items);
    } catch (caughtError) {
      setItems([]);
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo cargar la bandeja.");
    }
  }

  useEffect(() => {
    void loadQueue();
  }, []);

  async function handleAction(requestId: string, targetStatus: string) {
    setNotice(null);
    setError(null);
    try {
      const updated = await client.transition(requestId, targetStatus, me.username, `Cambio a ${targetStatus}`);
      setNotice(`Estado actualizado a ${updated.status}`);
      await loadQueue();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo actualizar el estado.");
    }
  }

  async function handleExport() {
    setNotice(null);
    setError(null);
    try {
      const csv = await client.exportQueue(queueStatus);
      setExportPreview(csv);
    } catch (caughtError) {
      setExportPreview("");
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo exportar la bandeja.");
    }
  }

  return (
    <section className="admin-shell">
      <div className="admin-shell-header">
        <div>
          <p className="eyebrow">Solicitudes</p>
          <h2>Bandeja operativa</h2>
        </div>
      </div>

      <label>
        Estado
        <select name="queueStatus" value={queueStatus} onChange={(event) => setQueueStatus(event.target.value)}>
          <option value="registrada">registrada</option>
          <option value="en_revision">en_revision</option>
          <option value="aprobada">aprobada</option>
          <option value="rechazada">rechazada</option>
          <option value="anulada">anulada</option>
        </select>
      </label>
      <div className="tab-strip">
        <button className="secondary-button" type="button" onClick={loadQueue}>
          Cargar bandeja
        </button>
        <button className="secondary-button" type="button" onClick={handleExport}>
          Exportar CSV
        </button>
      </div>

      {notice ? <p className="success-banner">{notice}</p> : null}
      {error ? <p className="error-banner">{error}</p> : null}

      {items.map((item) => (
        <div key={item.request_id} className="session-panel">
          <h3>{item.request_id}</h3>
          <p>{item.customer_name ?? "Sin nombre"}</p>
          <p>{item.status}</p>
          <StatusActions
            actions={item.available_actions}
            onAction={(targetStatus) => handleAction(item.request_id, targetStatus)}
          />
        </div>
      ))}

      {exportPreview ? <pre>{exportPreview}</pre> : null}
    </section>
  );
}
