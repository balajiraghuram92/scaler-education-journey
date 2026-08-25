import { useId } from 'react';

const MAX_DISPLAYED_DIAGNOSTIC_BYTES = 20000;

function limitDiagnostic(text) {
  if (!text || text.length <= MAX_DISPLAYED_DIAGNOSTIC_BYTES) return text || '';
  return `${text.slice(0, MAX_DISPLAYED_DIAGNOSTIC_BYTES)}\n[diagnostic display truncated]`;
}

export default function ExerciseDiagnostics({ title, content }) {
  const titleId = useId();

  if (!content) return null;

  return (
    <section className="exercise-diagnostics" aria-labelledby={titleId}>
      <div className="exercise-diagnostics__header">
        <h4 id={titleId}>{title}</h4>
        <span>LEARNER OUTPUT</span>
      </div>
      <pre className="exercise-diagnostics__content" aria-label={title}>
        {limitDiagnostic(content)}
      </pre>
    </section>
  );
}
