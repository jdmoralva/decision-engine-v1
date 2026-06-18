type DataPanelProps = {
  item: string;
};

const DATA_TITLES: Record<string, string> = {
  "importar-dataset": "Importar dataset",
  "configurar-relaciones": "Configurar relaciones",
  "administrar-medidas": "Administrar medidas",
  "administrar-catalogos": "Administrar catalogos",
};

export function DataPanel({ item }: DataPanelProps) {
  return (
    <section className="workspace-card">
      <h3>{DATA_TITLES[item] ?? "Data"}</h3>
      <p>Gobernanza pendiente</p>
    </section>
  );
}
