import { useEffect, useMemo, useRef, useState } from 'react';
import { Check, Maximize2, Minimize2, Play, RotateCcw } from 'lucide-react';
import TestEvidence from './TestEvidence';

function getLineNumbers(source) {
  return source.split('\n').map((_, index) => index + 1);
}

export default function ImplementationExercise({ exercise, isExpanded, onToggleExpand }) {
  const [sourceCode, setSourceCode] = useState(exercise.starterCode);
  const [runState, setRunState] = useState('idle');
  const [resultStatus, setResultStatus] = useState('failed');
  const [evidenceExpanded, setEvidenceExpanded] = useState(true);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState('extension');
  const demoTimerRef = useRef(null);
  const lineNumbers = useMemo(() => getLineNumbers(sourceCode), [sourceCode]);

  const executeDemo = (mode) => {
    if (runState === 'running') return;
    setRunState('running');
    demoTimerRef.current = window.setTimeout(() => {
      setResultStatus(mode === 'check' ? 'passed' : 'failed');
      setSelectedEvidenceId(mode === 'check' ? exercise.evidence[0]?.id : 'extension');
      setEvidenceExpanded(true);
      setRunState('completed');
    }, 320);
  };

  const handleEditorKeyDown = (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      executeDemo('run');
    }
  };

  const handleReset = () => {
    if (demoTimerRef.current) window.clearTimeout(demoTimerRef.current);
    setSourceCode(exercise.starterCode);
    setRunState('idle');
    setResultStatus('failed');
    setSelectedEvidenceId('extension');
    setEvidenceExpanded(true);
  };

  useEffect(() => () => {
    if (demoTimerRef.current) window.clearTimeout(demoTimerRef.current);
  }, []);

  return (
    <section className={`implementation-exercise${isExpanded ? ' is-expanded' : ''}`} aria-labelledby="implementation-exercise-title">
      <header className="implementation-exercise__header">
        <div>
          <p className="learning-eyebrow">{exercise.eyebrow}</p>
          <h3 id="implementation-exercise-title">{exercise.title}</h3>
        </div>
        <button type="button" className="learning-text-button implementation-exercise__expand" onClick={onToggleExpand}>
          {isExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          {isExpanded ? 'Collapse' : 'Expand'}
          <span aria-hidden="true">{isExpanded ? '↙' : '↗'}</span>
        </button>
      </header>

      <div className="implementation-exercise__meta" aria-label="Exercise metadata">
        <span>{exercise.language}</span>
        <span>{exercise.difficulty}</span>
        <span>~{exercise.estimatedMinutes} MIN</span>
      </div>
      <p className="implementation-exercise__description">{exercise.description}</p>

      <div className="implementation-exercise__toolbar">
        <span className="implementation-exercise__file-label">{exercise.editableFile}</span>
        <div className="implementation-exercise__actions">
          <button type="button" className="learning-button learning-button--quiet" onClick={handleReset}>
            <RotateCcw size={13} /> Reset
          </button>
          <button type="button" className="learning-button learning-button--run" onClick={() => executeDemo('run')} disabled={runState === 'running'}>
            <Play size={13} /> {runState === 'running' ? 'Running…' : 'Run'}
            <span className="implementation-exercise__shortcut">Ctrl + Enter</span>
          </button>
          <button type="button" className="learning-button learning-button--check" onClick={() => executeDemo('check')} disabled={runState === 'running'}>
            <Check size={13} /> Check solution
          </button>
        </div>
      </div>

      <div className="learning-editor" aria-label={`${exercise.editableFile} editor`}>
        <div className="learning-editor__gutter" aria-hidden="true">
          {lineNumbers.map((line) => <span key={line}>{line}</span>)}
        </div>
        <textarea
          className="learning-editor__textarea"
          value={sourceCode}
          onChange={(event) => setSourceCode(event.target.value)}
          onKeyDown={handleEditorKeyDown}
          spellCheck={false}
          aria-label={`${exercise.editableFile} source code`}
        />
      </div>

      {runState === 'running' && <div className="implementation-exercise__running" role="status" aria-live="polite">Running checks…</div>}

      {runState !== 'running' && (
        <TestEvidence
          evidence={exercise.evidence}
          expanded={evidenceExpanded}
          onToggle={() => setEvidenceExpanded((current) => !current)}
          selectedId={selectedEvidenceId}
          onSelect={setSelectedEvidenceId}
          resultStatus={resultStatus}
        />
      )}
    </section>
  );
}
