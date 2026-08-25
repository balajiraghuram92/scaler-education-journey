import { Check, ChevronDown, ChevronUp, X } from 'lucide-react';

export default function TestEvidence({ evidence = [], expanded, onToggle, selectedId, onSelect, resultStatus }) {
  const total = evidence.length;
  const passed = resultStatus === 'passed'
    ? total
    : evidence.filter((item) => item.status === 'passed').length;
  const selected = evidence.find((item) => item.id === selectedId) || evidence.find((item) => item.status === 'failed') || evidence[0];
  const selectedStatus = resultStatus === 'passed' ? 'passed' : selected?.status;

  return (
    <section className={`test-evidence${expanded ? ' is-expanded' : ''}`} aria-labelledby="test-evidence-title">
      <button type="button" className="test-evidence__summary" onClick={onToggle} aria-expanded={expanded}>
        <span className="test-evidence__summary-title" id="test-evidence-title">TEST EVIDENCE</span>
        <span className={`test-evidence__summary-result ${resultStatus === 'passed' ? 'is-passed' : 'is-failed'}`}>
          {resultStatus === 'passed' ? '✓' : '✕'} {passed} / {total} behaviors verified
        </span>
        <span className="test-evidence__details-label">{expanded ? 'Details' : 'Details'} {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</span>
      </button>

      {expanded && (
        <div className="test-evidence__body">
          <div className="test-evidence__checks" role="list" aria-label="Behavior checks">
            {evidence.map((item) => (
              <button
                type="button"
                role="listitem"
                key={item.id}
                className={`test-evidence__check${selected?.id === item.id ? ' is-selected' : ''}${resultStatus !== 'passed' && item.status === 'failed' ? ' is-failed' : ''}`}
                onClick={() => onSelect(item.id)}
              >
                <span className="test-evidence__check-icon" aria-hidden="true">
                  {resultStatus === 'passed' || item.status === 'passed' ? <Check size={13} /> : <X size={13} />}
                </span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
          <div className="test-evidence__detail" aria-live="polite">
            {selectedStatus === 'failed' ? (
              <>
                <p className="test-evidence__failure-copy">{selected.message}</p>
                <p className="test-evidence__source">{selected.source}</p>
                <div className="test-evidence__hint">
                  <p className="test-evidence__hint-label">Architectural Hint</p>
                  <p>{selected.hint}</p>
                  <code>{selected.prompt}</code>
                </div>
              </>
            ) : (
              <div className="test-evidence__passed-copy">
                <p>All expected behaviors verified.</p>
                <p>Select a behavior to review the evidence captured by the exercise.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
