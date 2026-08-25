export default function ArchitectureFlow({ eyebrow, nodes = [], boundaryLabel, boundaryText }) {
  const request = nodes.find((node) => node.kind === 'input');
  const service = nodes.find((node) => node.kind === 'service');
  const contract = nodes.find((node) => node.kind === 'boundary');
  const adapters = nodes.filter((node) => node.kind === 'adapter');
  const output = nodes.find((node) => node.kind === 'output');

  return (
    <section id="architecture-flow" className="architecture-flow" aria-labelledby="architecture-flow-title">
      <p id="architecture-flow-title" className="learning-eyebrow">{eyebrow}</p>
      <div className="architecture-flow__diagram" role="img" aria-label="Payment request flows through PaymentService and the PaymentAuthorizer interface to provider adapters and an authorization result.">
        <div className="architecture-flow__main-row">
          <div className="architecture-flow__node architecture-flow__node--input">{request?.label}</div>
          <span className="architecture-flow__connector" aria-hidden="true">→</span>
          <div className="architecture-flow__node architecture-flow__node--service">{service?.label}</div>
          <span className="architecture-flow__connector" aria-hidden="true">→</span>
          <div className="architecture-flow__node architecture-flow__node--boundary">{contract?.label}</div>
        </div>
        <div className="architecture-flow__branch-row">
          <span className="architecture-flow__branch-stem" aria-hidden="true" />
          <div className="architecture-flow__adapter-list">
            {adapters.map((adapter) => (
              <div key={adapter.id} className="architecture-flow__adapter-item">
                <span className="architecture-flow__connector architecture-flow__connector--vertical" aria-hidden="true">↓</span>
                <div className="architecture-flow__node architecture-flow__node--adapter">{adapter.label}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="architecture-flow__output-row">
          <span className="architecture-flow__connector" aria-hidden="true">↓</span>
          <div className="architecture-flow__node architecture-flow__node--output">{output?.label}</div>
        </div>
      </div>
      <div className="architecture-flow__boundary-note">
        <span className="architecture-flow__boundary-check" aria-hidden="true">✓</span>
        <p><strong>{boundaryLabel}:</strong> {boundaryText}</p>
      </div>
    </section>
  );
}
