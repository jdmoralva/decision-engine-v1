import { useEffect, useState } from "react";

import { AuditApiClient, type AuditEventPage } from "../../services/audit-api";
import type { DecisionTraceResponse } from "../../services/runtime-api";


type AuditTimelineProps = {
  client: AuditApiClient;
  productCode: string;
  evaluationId: string | null;
  requestId: string;
};


export function AuditTimeline({ client, productCode, evaluationId, requestId }: AuditTimelineProps) {
  const [audit, setAudit] = useState<AuditEventPage | null>(null);
  const [trace, setTrace] = useState<DecisionTraceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadTimeline() {
      setError(null);
      try {
        const [auditPage, traceResponse] = await Promise.all([
          client.list(requestId, evaluationId),
          evaluationId ? client.getTrace(productCode, evaluationId) : Promise.resolve(null),
        ]);
        if (!isMounted) {
          return;
        }
        setAudit(auditPage);
        setTrace(traceResponse);
      } catch (caughtError) {
        if (!isMounted) {
          return;
        }
        setAudit(null);
        setTrace(null);
        setError(caughtError instanceof Error ? caughtError.message : "No se pudo cargar la auditoria.");
      }
    }

    void loadTimeline();
    return () => {
      isMounted = false;
    };
  }, [client, evaluationId, productCode, requestId]);

  if (error) {
    return <p className="error-banner">{error}</p>;
  }

  if (audit === null) {
    return null;
  }

  return (
    <div className="session-panel">
      <h4>Timeline de auditoria</h4>
      {audit.items.map((item) => (
        <p key={item.event_id}>{item.event_type}</p>
      ))}
      {trace?.nodes_executed.map((node) => (
        <p key={node.node_key}>{node.node_key}</p>
      ))}
    </div>
  );
}
