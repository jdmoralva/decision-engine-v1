import { useEffect, useState } from "react";

import { AttachmentsPanel } from "../attachments/AttachmentsPanel";
import { AuditTimeline } from "../attachments/AuditTimeline";
import type { SessionMe } from "../../session-storage";
import { AttachmentsApiClient } from "../../services/attachments-api";
import { AuditApiClient } from "../../services/audit-api";
import {
  CreditRequestsApiClient,
  type CreditRequestDetail,
} from "../../services/credit-requests-api";
import type { ConsultationResponse, EvaluationResponse } from "../../services/runtime-api";

type CreditRequestPageProps = {
  client: CreditRequestsApiClient;
  attachmentsClient: AttachmentsApiClient | null;
  auditClient: AuditApiClient | null;
  me: SessionMe;
  consultation: ConsultationResponse | null;
  evaluation: EvaluationResponse | null;
};


export function CreditRequestPage({
  client,
  attachmentsClient,
  auditClient,
  me,
  consultation,
  evaluation,
}: CreditRequestPageProps) {
  const [evaluationId, setEvaluationId] = useState(evaluation?.evaluation_id ?? "");
  const [requestedAmount, setRequestedAmount] = useState("9800");
  const [comment, setComment] = useState("Solicitud inicial");
  const [detail, setDetail] = useState<CreditRequestDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (evaluation?.evaluation_id) {
      setEvaluationId(evaluation.evaluation_id);
    }
    const offeredAmount = evaluation?.product_result?.offered_amount;
    if (typeof offeredAmount === "number") {
      setRequestedAmount(String(offeredAmount));
    }
  }, [evaluation]);

  async function handleSubmit() {
    setIsSubmitting(true);
    setError(null);
    try {
      const created = await client.create({
        product_code: "PLD",
        evaluation_id: evaluationId,
        document: consultation?.document ?? { document_type: "DNI", document_number: "12345678" },
        campaign_code: consultation?.campaigns[0]?.campaign_code ?? "PLD_48M",
        requested_amount: Number(requestedAmount),
        comment,
        created_by: { username: me.username },
      });
      const fetchedDetail = await client.getDetail(created.request_id);
      setDetail(fetchedDetail);
    } catch (caughtError) {
      setDetail(null);
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo registrar la solicitud.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const canManageAttachments = me.roles.some((role) => ["analista", "evaluador", "admin"].includes(role));
  const canReadAudit = me.roles.some((role) =>
    ["evaluador", "auditor", "admin", "admin_negocio", "admin_riesgos", "plataforma"].includes(role),
  );

  return (
    <section className="admin-shell">
      <div className="admin-shell-header">
        <div>
          <p className="eyebrow">Solicitudes</p>
          <h2>Registro</h2>
        </div>
      </div>

      <div className="session-grid">
        <label>
          Evaluacion
          <input name="evaluationId" value={evaluationId} onChange={(event) => setEvaluationId(event.target.value)} />
        </label>
        <label>
          Monto solicitado
          <input
            name="requestedAmount"
            value={requestedAmount}
            onChange={(event) => setRequestedAmount(event.target.value)}
          />
        </label>
      </div>
      <label>
        Comentario
        <textarea name="comment" value={comment} onChange={(event) => setComment(event.target.value)} />
      </label>
      <button className="secondary-button" type="button" disabled={isSubmitting} onClick={handleSubmit}>
        {isSubmitting ? "Registrando..." : "Registrar solicitud"}
      </button>

      {error ? <p className="error-banner">{error}</p> : null}

      {detail ? (
        <div className="session-panel">
          <h3>Detalle de la solicitud</h3>
          <p>{detail.request_id}</p>
          <p>{detail.customer_name ?? "Sin nombre"}</p>
          <p>{detail.status}</p>
          <h4>Historial de estados</h4>
          {detail.status_history.map((item) => (
            <p key={`${item.status}-${item.changed_at}`}>
              {item.status} | {item.changed_by.username}
            </p>
          ))}

          {attachmentsClient ? (
            <AttachmentsPanel
              client={attachmentsClient}
              requestId={detail.request_id}
              canUpload={canManageAttachments}
            />
          ) : null}

          {auditClient && canReadAudit ? (
            <AuditTimeline
              client={auditClient}
              productCode={detail.product_code}
              evaluationId={detail.evaluation_id ?? null}
              requestId={detail.request_id}
            />
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
