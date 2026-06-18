type ParametersPanelProps = {
  item: string;
  canEdit: boolean;
};

const PARAMETER_TITLES: Record<string, string> = {
  "limites-internos": "Limites internos",
  "limites-globales": "Limites globales",
  "niveles-autonomia": "Niveles de autonomia",
};

export function ParametersPanel({ item, canEdit }: ParametersPanelProps) {
  return (
    <section className="workspace-card">
      <h3>{PARAMETER_TITLES[item] ?? "Parametros"}</h3>
      <p>{canEdit ? "Editable por riesgos" : "Solo lectura para este rol"}</p>
    </section>
  );
}
