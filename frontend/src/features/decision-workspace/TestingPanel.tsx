type TestingPanelProps = {
  tests: string[];
};

export function TestingPanel({ tests }: TestingPanelProps) {
  return (
    <section className="workspace-card">
      <h3>Pruebas AB</h3>
      {tests.map((item) => (
        <p key={item}>{item}</p>
      ))}
    </section>
  );
}
