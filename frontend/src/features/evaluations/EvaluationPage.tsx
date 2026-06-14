import { useEffect, useState } from "react";

import { type SessionMe } from "../../session-storage";
import {
  RuntimeApiClient,
  type ConsultationResponse,
  type DecisionTraceResponse,
  type EvaluationResponse,
} from "../../services/runtime-api";
import { EvaluationForm } from "./evaluation-form";
import { TracePanel } from "./trace-panel";

type EvaluationPageProps = {
  client: RuntimeApiClient;
  me: SessionMe;
  consultation: ConsultationResponse | null;
  onEvaluationChange?: (result: EvaluationResponse | null) => void;
};

export function EvaluationPage({ client, me, consultation, onEvaluationChange }: EvaluationPageProps) {
  const [campaignCode, setCampaignCode] = useState("PLD_48M");
  const [reportedDebt, setReportedDebt] = useState("400");
  const [result, setResult] = useState<EvaluationResponse | null>(null);
  const [trace, setTrace] = useState<DecisionTraceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const campaign = consultation?.campaigns[0]?.campaign_code;
    if (campaign) {
      setCampaignCode(campaign);
    }
  }, [consultation]);

  async function handleSubmit() {
    setIsSubmitting(true);
    setError(null);
    try {
      const evaluation = await client.evaluate("PLD", {
        product_code: "PLD",
        workflow_code: "standard",
        document: consultation?.document ?? { document_type: "DNI", document_number: "12345678" },
        requested_by: { username: me.username },
        product_context: {
          campaign_code: campaignCode,
          customer_type: consultation?.customer.customer_type ?? "CLIENTE",
          profile_code: consultation?.customer.profile_code ?? "PERFIL 1",
          sunedu_flag: consultation?.customer.sunedu_flag ?? "CON SUNEDU",
          employment_status: consultation?.customer.employment_status ?? "DEP",
          validated_income: consultation?.customer.validated_income ?? 2500,
          initial_offered_amount: consultation?.campaigns[0]?.offered_amount ?? 12000,
          existing_consumption_balance: 300,
          campaign_rate: consultation?.campaigns[0]?.rate ?? 18.5,
          campaign_term_months: consultation?.campaigns[0]?.term_months ?? 48,
        },
        external_inputs: [
          {
            source_type: "user_input",
            source_key: "form:pld",
            field_name: "reported_debt",
            field_value: reportedDebt,
          },
        ],
      });
      const fetchedTrace = await client.getTrace("PLD", evaluation.evaluation_id);
      setResult(evaluation);
      setTrace(fetchedTrace);
      onEvaluationChange?.(evaluation);
    } catch (caughtError) {
      setResult(null);
      setTrace(null);
      onEvaluationChange?.(null);
      setError(caughtError instanceof Error ? caughtError.message : "No se pudo ejecutar la evaluacion.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="admin-shell">
      <div className="admin-shell-header">
        <div>
          <p className="eyebrow">Runtime PLD</p>
          <h2>Evaluacion</h2>
        </div>
      </div>

      <EvaluationForm
        campaignCode={campaignCode}
        reportedDebt={reportedDebt}
        isSubmitting={isSubmitting}
        onCampaignCodeChange={setCampaignCode}
        onReportedDebtChange={setReportedDebt}
        onSubmit={handleSubmit}
      />

      {error ? <p className="error-banner">{error}</p> : null}
      {result ? (
        <div className="session-panel">
          <h3>Resultado de evaluacion</h3>
          <p>{String(result.product_result?.offered_amount ?? "")}</p>
          <p>{String(result.product_result?.installment_amount ?? "")}</p>
        </div>
      ) : null}
      <TracePanel trace={trace} />
    </section>
  );
}
