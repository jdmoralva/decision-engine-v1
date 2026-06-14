type EvaluationFormProps = {
  campaignCode: string;
  reportedDebt: string;
  isSubmitting: boolean;
  onCampaignCodeChange: (value: string) => void;
  onReportedDebtChange: (value: string) => void;
  onSubmit: () => Promise<void>;
};

export function EvaluationForm({
  campaignCode,
  reportedDebt,
  isSubmitting,
  onCampaignCodeChange,
  onReportedDebtChange,
  onSubmit,
}: EvaluationFormProps) {
  return (
    <div className="login-form">
      <label className="field">
        <span>Campana</span>
        <input value={campaignCode} onChange={(event) => onCampaignCodeChange(event.target.value)} />
      </label>
      <label className="field">
        <span>Deuda reportada</span>
        <input value={reportedDebt} onChange={(event) => onReportedDebtChange(event.target.value)} />
      </label>
      <button className="primary-button" type="button" disabled={isSubmitting} onClick={() => void onSubmit()}>
        {isSubmitting ? "Evaluando..." : "Evaluar oferta"}
      </button>
    </div>
  );
}
