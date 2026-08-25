import { useId } from 'react';
import { AlertCircle, Check, ChevronDown, ChevronUp, Circle, Minus, X } from 'lucide-react';
import { EVIDENCE_STATUSES, EXERCISE_STATUSES } from '../../api/exerciseModels';

function getEvidenceIcon(status) {
  if (status === EVIDENCE_STATUSES.PASSED) return <Check size={13} />;
  if (status === EVIDENCE_STATUSES.FAILED) return <X size={13} />;
  if (status === EVIDENCE_STATUSES.ERROR) return <AlertCircle size={13} />;
  if (status === EVIDENCE_STATUSES.SKIPPED) return <Minus size={13} />;
  return <Circle size={11} />;
}

function getSummaryText(resultStatus, summary, passed, total) {
  if (resultStatus === EXERCISE_STATUSES.SUCCESS) return `✓ ${passed} / ${total} behaviors verified`;
  if (resultStatus === EXERCISE_STATUSES.COMPILATION_FAILURE) return 'Compilation failed · tests not run';
  if (resultStatus === EXERCISE_STATUSES.TIMEOUT) return 'Timed out · tests not run';
  if (resultStatus === EXERCISE_STATUSES.TEST_FAILURE) return `${passed} / ${total} behaviors verified`;
  if (summary) return summary;
  return `○ 0 / ${total} behaviors verified`;
}

function getDetailCopy(item) {
  if (!item || item.status === EVIDENCE_STATUSES.NOT_RUN) {
    return <p>This behavior has not been evaluated yet.</p>;
  }
  if (item.status === EVIDENCE_STATUSES.PASSED) {
    return <p>This behavior was verified by the exercise test suite.</p>;
  }
  if (item.status === EVIDENCE_STATUSES.SKIPPED) {
    return <p>This behavior was skipped during the captured execution.</p>;
  }
  return <p className="test-evidence__failure-copy">{item.message || 'The exercise reported a problem for this behavior.'}</p>;
}

export default function TestEvidence({
  evidence = [],
  summary,
  expanded,
  onToggle,
  selectedId,
  onSelect,
  resultStatus,
  stale
}) {
  const titleId = useId();
  const total = evidence.length;
  const passed = evidence.filter((item) => item.status === EVIDENCE_STATUSES.PASSED).length;
  const selected = evidence.find((item) => item.id === selectedId) || evidence.find((item) => item.status === EVIDENCE_STATUSES.FAILED) || evidence[0];
  const summaryText = getSummaryText(resultStatus, summary, passed, total);

  return (
    <section className={`test-evidence${expanded ? ' is-expanded' : ''}`} aria-labelledby={titleId}>
      <button type="button" className="test-evidence__summary" onClick={onToggle} aria-expanded={expanded}>
        <span className="test-evidence__summary-title" id={titleId}>TEST EVIDENCE</span>
        <span className={`test-evidence__summary-result ${resultStatus === EXERCISE_STATUSES.SUCCESS ? 'is-passed' : ''}`}>
          {summaryText}
        </span>
        <span className="test-evidence__details-label">Details {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</span>
      </button>

      {stale && <p className="test-evidence__stale">The editor changed after this result. Run again to refresh the evidence.</p>}

      {expanded && (
        <div className="test-evidence__body">
          <ul className="test-evidence__checks" aria-label="Behavior checks">
            {evidence.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={`test-evidence__check${selected?.id === item.id ? ' is-selected' : ''}`}
                  onClick={() => onSelect(item.id)}
                  aria-pressed={selected?.id === item.id}
                >
                  <span className={`test-evidence__check-icon test-evidence__check-icon--${item.status}`} aria-hidden="true">
                    {getEvidenceIcon(item.status)}
                  </span>
                  <span>{item.label}</span>
                  <span className="test-evidence__check-status">{item.status}</span>
                </button>
              </li>
            ))}
          </ul>
          <div className="test-evidence__detail" aria-live="polite">
            {getDetailCopy(selected)}
          </div>
        </div>
      )}
    </section>
  );
}
