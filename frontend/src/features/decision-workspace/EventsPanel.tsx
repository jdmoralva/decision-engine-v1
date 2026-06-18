type EventsPanelProps = {
  events: string[];
};

export function EventsPanel({ events }: EventsPanelProps) {
  return (
    <section className="workspace-card">
      <h3>Ultimos eventos</h3>
      {events.map((item) => (
        <p key={item}>{item}</p>
      ))}
    </section>
  );
}
