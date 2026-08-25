import { useEffect, useMemo, useRef, useState } from 'react';
import { AlertCircle, Check, ChevronDown, ChevronUp, Minimize2, Play, RotateCcw } from 'lucide-react';
import useExerciseWorkspace from '../../hooks/useExerciseWorkspace';
import { EVIDENCE_STATUSES, EXERCISE_STATUSES } from '../../api/exerciseModels';
import ExerciseDiagnostics from './ExerciseDiagnostics';
import ExerciseErrorState from './ExerciseErrorState';
import TestEvidence from './TestEvidence';

function getLineNumbers(source) {
  return source.split('\n').map((_, index) => index + 1);
}

function getStatusCopy(status, operation) {
  if (status === EXERCISE_STATUSES.SUCCESS) return 'All expected behaviors verified.';
  if (status === EXERCISE_STATUSES.TEST_FAILURE) return 'The code compiled, but one or more behaviors need another pass.';
  if (status === EXERCISE_STATUSES.COMPILATION_FAILURE) return 'The submitted code could not compile.';
  if (status === EXERCISE_STATUSES.TIMEOUT) return 'Execution exceeded the allowed time.';
  if (status === 'apiFailure') return 'Neuralascent could not execute this workspace.';
  if (status === 'running') return operation === 'check' ? 'Checking the current workspace…' : 'Running the current workspace…';
  return '';
}

function getCompactResult(execution) {
  if (!execution.result) return null;

  const summary = execution.result.summary || {};
  if (execution.stale) return 'Last result is stale · source changed';
  if (execution.status === EXERCISE_STATUSES.SUCCESS) return `✓ ${summary.passed} / ${summary.total} checks passed`;
  if (execution.status === EXERCISE_STATUSES.TEST_FAILURE) return `! ${summary.passed} / ${summary.total} checks passed`;
  if (execution.status === EXERCISE_STATUSES.COMPILATION_FAILURE) return 'Compilation failed · tests not run';
  if (execution.status === EXERCISE_STATUSES.TIMEOUT) return 'Execution timed out · tests not run';
  return null;
}

function FileTabs({ files, activeFileId, onSelect, isCompact }) {
  const [isOverflowOpen, setIsOverflowOpen] = useState(false);
  const overflowRef = useRef(null);
  const tabRefs = useRef(new Map());
  const activeFile = files.find((file) => file.id === activeFileId) || files[0];

  useEffect(() => {
    if (!isOverflowOpen) return undefined;
    const handlePointerDown = (event) => {
      if (!overflowRef.current?.contains(event.target)) setIsOverflowOpen(false);
    };
    document.addEventListener('pointerdown', handlePointerDown);
    return () => document.removeEventListener('pointerdown', handlePointerDown);
  }, [isOverflowOpen]);

  if (!activeFile || files.length <= 1) return null;

  const visibleLimit = isCompact ? 0 : files.length <= 4 ? files.length : 3;
  const initialVisibleFiles = isCompact ? [] : files.slice(0, visibleLimit);
  const activeIsVisible = initialVisibleFiles.some((file) => file.id === activeFile.id);
  const visibleFiles = isCompact || activeIsVisible
    ? initialVisibleFiles
    : [...files.slice(0, Math.max(0, visibleLimit - 1)), activeFile];
  const visibleIds = new Set(visibleFiles.map((file) => file.id));
  const overflowFiles = isCompact
    ? files.filter((file) => file.id !== activeFile.id)
    : files.filter((file) => !visibleIds.has(file.id));

  const selectFile = (fileId) => {
    onSelect(fileId);
    setIsOverflowOpen(false);
  };

  const moveTab = (event, direction) => {
    event.preventDefault();
    const currentIndex = files.findIndex((file) => file.id === activeFileId);
    const nextIndex = (currentIndex + direction + files.length) % files.length;
    const nextFile = files[nextIndex];
    onSelect(nextFile.id);
    requestAnimationFrame(() => tabRefs.current.get(nextFile.id)?.focus());
  };

  const moveToBoundary = (event, index) => {
    event.preventDefault();
    const nextFile = files[index];
    onSelect(nextFile.id);
    requestAnimationFrame(() => tabRefs.current.get(nextFile.id)?.focus());
  };

  const handleKeyDown = (event) => {
    if (event.key === 'ArrowLeft') moveTab(event, -1);
    if (event.key === 'ArrowRight') moveTab(event, 1);
    if (event.key === 'Home') moveToBoundary(event, 0);
    if (event.key === 'End') moveToBoundary(event, files.length - 1);
  };

  return (
    <div className={`implementation-exercise__file-tabs${isCompact ? ' is-compact' : ''}`} ref={overflowRef}>
      {isCompact ? (
        <div className="implementation-exercise__compact-file-identity">
          <span className="implementation-exercise__compact-file-name" title={activeFile.path}>{activeFile.displayName}</span>
          <span className="implementation-exercise__compact-file-count">{files.length} files</span>
        </div>
      ) : (
        <div className="implementation-exercise__file-tabs-list" role="tablist" aria-label="Exercise files" onKeyDown={handleKeyDown}>
          {visibleFiles.map((file) => (
            <button
              key={file.id}
              ref={(node) => {
                if (node) tabRefs.current.set(file.id, node);
                else tabRefs.current.delete(file.id);
              }}
              type="button"
              role="tab"
              tabIndex={activeFileId === file.id ? 0 : -1}
              aria-selected={activeFileId === file.id}
              aria-controls={`exercise-file-panel-${file.id}`}
              className={`implementation-exercise__file-tab${activeFileId === file.id ? ' is-active' : ''}`}
              title={file.path}
              onClick={() => selectFile(file.id)}
            >
              {file.displayName}
            </button>
          ))}
        </div>
      )}

      {overflowFiles.length > 0 && (
        <div className="implementation-exercise__file-overflow">
          <button
            type="button"
            className="implementation-exercise__file-overflow-button"
            aria-haspopup="menu"
            aria-expanded={isOverflowOpen}
            onClick={() => setIsOverflowOpen((current) => !current)}
          >
            {isCompact ? 'Files' : 'More'} <span aria-hidden="true">{isCompact ? '▾' : '…'}</span>
          </button>
          {isOverflowOpen && (
            <div className="implementation-exercise__file-overflow-menu" role="menu" aria-label="More exercise files">
              {overflowFiles.map((file) => (
                <button
                  key={file.id}
                  type="button"
                  role="menuitem"
                  className="implementation-exercise__file-overflow-item"
                  title={file.path}
                  onClick={() => selectFile(file.id)}
                >
                  {file.displayName}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ImplementationExercise({ exerciseId, isExpanded, onToggleExpand }) {
  const {
    metadata,
    metadataState,
    workingFiles,
    activeFile,
    activeFileId,
    setActiveFileId,
    updateFile,
    reset,
    execute,
    retryMetadata,
    execution,
    isExecutionActive
  } = useExerciseWorkspace(exerciseId);
  const [evidenceExpanded, setEvidenceExpanded] = useState(true);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState(null);

  useEffect(() => {
    const failed = execution.result?.evidence?.find((item) => item.status === EVIDENCE_STATUSES.FAILED);
    setSelectedEvidenceId(failed?.id || metadata?.evidence?.[0]?.id || null);
    setEvidenceExpanded(true);
  }, [execution.result?.evidence, execution.result?.runId, metadata?.evidence, metadata?.id]);

  const sourceCode = activeFile?.content || '';
  const lineNumbers = useMemo(() => getLineNumbers(sourceCode), [sourceCode]);
  const workspaceId = `exercise-${exerciseId}`;
  const compactResult = getCompactResult(execution);
  const evidence = execution.result?.evidence
    || metadata?.evidence?.map((item) => ({ ...item, status: EVIDENCE_STATUSES.NOT_RUN, durationMilliseconds: 0, message: null }))
    || [];
  const summary = execution.result?.summary || null;
  const isReady = metadataState === 'ready' && Boolean(metadata);
  const canExecute = isReady && !isExecutionActive;

  const handleSourceChange = (event) => {
    if (!activeFile || activeFile.editable === false) return;
    updateFile(activeFile.id, event.target.value);
  };

  const handleEditorKeyDown = (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      if (!isExpanded || !canExecute) return;
      event.preventDefault();
      execute('run');
      return;
    }

    if (event.key !== 'Tab' || !activeFile || activeFile.editable === false) return;
    event.preventDefault();
    const textarea = event.currentTarget;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const nextContent = `${sourceCode.slice(0, start)}    ${sourceCode.slice(end)}`;
    updateFile(activeFile.id, nextContent);
    requestAnimationFrame(() => textarea.setSelectionRange(start + 4, start + 4));
  };

  if (metadataState === 'loading') {
    return (
      <section className="implementation-exercise implementation-exercise--loading" aria-labelledby={`${workspaceId}-title`}>
        <p className="learning-eyebrow">IMPLEMENTATION EXERCISE · JAVA</p>
        <h3 id={`${workspaceId}-title`}>Opening coding workspace…</h3>
        <p>Loading the trusted starter files and exercise checks.</p>
      </section>
    );
  }

  if (!isReady || workingFiles.length === 0) {
    return (
      <section className="implementation-exercise implementation-exercise--unavailable" aria-labelledby={`${workspaceId}-title`}>
        <p className="learning-eyebrow">IMPLEMENTATION EXERCISE · JAVA</p>
        <h3 id={`${workspaceId}-title`}>Coding exercise unavailable</h3>
        <ExerciseErrorState error={execution.error} onRetry={retryMetadata} />
      </section>
    );
  }

  const isReadOnly = activeFile?.editable === false;
  const statusCopy = getStatusCopy(execution.status, execution.operation);

  return (
    <section
      className={`implementation-exercise${isExpanded ? ' is-expanded' : ' is-compact'}`}
      aria-labelledby={`${workspaceId}-title`}
    >
      <header className="implementation-exercise__header">
        <div>
          <p className="learning-eyebrow">IMPLEMENTATION EXERCISE · {metadata.language.toUpperCase()}</p>
          <h3 id={`${workspaceId}-title`}>{metadata.title}</h3>
        </div>
        {isExpanded && (
          <button
            type="button"
            className="learning-text-button implementation-exercise__collapse"
            onClick={onToggleExpand}
            aria-expanded={isExpanded}
            aria-controls={workspaceId}
          >
            <Minimize2 size={14} />
            Collapse exercise <span aria-hidden="true">↑</span>
          </button>
        )}
      </header>

      <div className="implementation-exercise__meta" aria-label="Exercise metadata">
        <span>{metadata.language}</span>
        <span>{metadata.difficulty}</span>
        <span>~{metadata.estimatedMinutes} MIN</span>
      </div>
      {metadata.instructions && <p className="implementation-exercise__description">{metadata.instructions}</p>}
      {!metadata.instructions && <p className="implementation-exercise__description">Edit the starter files, then run the checks to verify the behavior described in this lesson.</p>}

      <div id={workspaceId} className="implementation-exercise__workspace" role="region" aria-label="Coding exercise workspace" aria-busy={isExecutionActive}>
        <FileTabs files={workingFiles} activeFileId={activeFileId} onSelect={setActiveFileId} isCompact={!isExpanded} />

        {(workingFiles.length === 1 || isExpanded || isReadOnly) && (
          <div className="implementation-exercise__toolbar">
            <div className="implementation-exercise__file-identity">
              {workingFiles.length === 1 && (
                <span className="implementation-exercise__file-label" title={activeFile.path}>{activeFile.displayName}</span>
              )}
              {isReadOnly && <span className="implementation-exercise__file-status">Reference · Read only</span>}
            </div>
            {isExpanded && (
              <div className="implementation-exercise__actions">
                <button type="button" className="learning-button learning-button--quiet" onClick={reset} disabled={!canExecute}>
                  <RotateCcw size={13} /> Reset
                </button>
                <button type="button" className="learning-button learning-button--run" aria-label="Run (Ctrl + Enter)" onClick={() => execute('run')} disabled={!canExecute}>
                  <Play size={13} /> {execution.operation === 'run' && isExecutionActive ? 'Running…' : 'Run'}
                  <span className="implementation-exercise__shortcut">Ctrl + Enter</span>
                </button>
                <button type="button" className="learning-button learning-button--check" onClick={() => execute('check')} disabled={!canExecute}>
                  <Check size={13} /> {execution.operation === 'check' && isExecutionActive ? 'Checking…' : 'Check solution'}
                </button>
              </div>
            )}
          </div>
        )}

        <div
          id={`exercise-file-panel-${activeFile.id}`}
          className={`learning-editor${isExpanded ? ' learning-editor--expanded' : ' learning-editor--compact'}${isReadOnly ? ' learning-editor--read-only' : ''}`}
          role="tabpanel"
          aria-label={`${activeFile.displayName} editor`}
        >
          <div className="learning-editor__gutter" aria-hidden="true">
            {lineNumbers.map((line) => <span key={line}>{line}</span>)}
          </div>
          <textarea
            className="learning-editor__textarea"
            value={sourceCode}
            onChange={handleSourceChange}
            onKeyDown={handleEditorKeyDown}
            readOnly={isReadOnly}
            spellCheck={false}
            aria-label={`${activeFile.displayName} source code`}
            aria-readonly={isReadOnly}
          />
        </div>
      </div>

      {isExecutionActive && (
        <div className="implementation-exercise__running" role="status" aria-live="polite">
          <span className="implementation-exercise__status-dot" aria-hidden="true" />
          {statusCopy}
          <span className="implementation-exercise__editing-note">You can keep editing; this run uses the captured snapshot.</span>
        </div>
      )}

      {!isExecutionActive && execution.status === 'apiFailure' && (
        <ExerciseErrorState error={execution.error} onRetry={() => execute(execution.operation || 'run')} />
      )}

      {!isExecutionActive && execution.status !== 'apiFailure' && execution.result && (
        <div className={`implementation-exercise__result implementation-exercise__result--${execution.status}`} role="status" aria-live="polite">
          {execution.status === EXERCISE_STATUSES.SUCCESS ? <Check size={16} aria-hidden="true" /> : <AlertCircle size={16} aria-hidden="true" />}
          <span>{statusCopy}</span>
          {execution.stale && <strong>Result is from an earlier source version.</strong>}
        </div>
      )}

      {isExpanded && !isExecutionActive && execution.status !== 'apiFailure' && (
        <>
          <TestEvidence
            evidence={evidence}
            summary={summary}
            expanded={evidenceExpanded}
            onToggle={() => setEvidenceExpanded((current) => !current)}
            selectedId={selectedEvidenceId}
            onSelect={setSelectedEvidenceId}
            resultStatus={execution.result ? execution.status : 'idle'}
            stale={execution.stale}
          />
          {execution.status === EXERCISE_STATUSES.COMPILATION_FAILURE && (
            <ExerciseDiagnostics title="Compiler diagnostics" content={execution.result?.diagnostics?.compilerOutput} />
          )}
          {execution.status === EXERCISE_STATUSES.TEST_FAILURE && (
            <ExerciseDiagnostics title="Execution output" content={execution.result?.diagnostics?.runtimeOutput} />
          )}
        </>
      )}

      {!isExpanded && compactResult && (
        <p className={`implementation-exercise__compact-result${execution.status === EXERCISE_STATUSES.SUCCESS && !execution.stale ? ' is-passed' : ''}`} role="status" aria-live="polite">
          {compactResult}
        </p>
      )}

      <button
        type="button"
        className="implementation-exercise__disclosure"
        onClick={onToggleExpand}
        aria-expanded={isExpanded}
        aria-controls={workspaceId}
      >
        {isExpanded ? 'Show less' : 'Show full exercise'}
        {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>
    </section>
  );
}
