import { useState } from "react";

import { RuntimeApiClient, type ConsultationResponse } from "../../services/runtime-api";
import { ConsultationForm } from "./consultation-form";

type ConsultationPageProps = {
  client: RuntimeApiClient;
  onConsultationChange: (result: ConsultationResponse | null) => void;
};

export function ConsultationPage({ client, onConsultationChange }: ConsultationPageProps) {
  const [documentType, setDocumentType] = useState("DNI");
  const [documentNumber, setDocumentNumber] = useState("12345678");
  const [result, setResult] = useState<ConsultationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit() {
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await client.consult("PLD", {
        document_type: documentType,
        document_number: documentNumber,
      });
      setResult(response);
      onConsultationChange(response);
    } catch (caughtError) {
      setResult(null);
      onConsultationChange(null);
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo consultar el cliente.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="admin-shell">
      <div className="admin-shell-header">
        <div>
          <p className="eyebrow">Runtime PLD</p>
          <h2>Consulta</h2>
        </div>
      </div>

      <ConsultationForm
        documentType={documentType}
        documentNumber={documentNumber}
        isSubmitting={isSubmitting}
        onDocumentTypeChange={setDocumentType}
        onDocumentNumberChange={setDocumentNumber}
        onSubmit={handleSubmit}
      />

      {error ? <p className="error-banner">{error}</p> : null}
      {result ? (
        <div className="session-panel">
          <h3>Resultado de consulta</h3>
          <p>{result.customer.full_name}</p>
          <p>{result.customer.customer_type}</p>
          {result.campaigns.map((campaign) => (
            <p key={campaign.campaign_code}>{campaign.campaign_code}</p>
          ))}
        </div>
      ) : null}
    </section>
  );
}
