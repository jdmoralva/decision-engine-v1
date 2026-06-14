type ConsultationFormProps = {
  documentType: string;
  documentNumber: string;
  isSubmitting: boolean;
  onDocumentTypeChange: (value: string) => void;
  onDocumentNumberChange: (value: string) => void;
  onSubmit: () => Promise<void>;
};

export function ConsultationForm({
  documentType,
  documentNumber,
  isSubmitting,
  onDocumentTypeChange,
  onDocumentNumberChange,
  onSubmit,
}: ConsultationFormProps) {
  return (
    <div className="login-form">
      <label className="field">
        <span>Tipo de documento</span>
        <input value={documentType} onChange={(event) => onDocumentTypeChange(event.target.value)} />
      </label>
      <label className="field">
        <span>Numero</span>
        <input value={documentNumber} onChange={(event) => onDocumentNumberChange(event.target.value)} />
      </label>
      <button className="primary-button" type="button" disabled={isSubmitting} onClick={() => void onSubmit()}>
        {isSubmitting ? "Consultando..." : "Consultar cliente"}
      </button>
    </div>
  );
}
