import { useEffect, useMemo, useRef, useState } from 'react';
import { Check, ChevronDown, ChevronUp, Minimize2, Play, RotateCcw } from 'lucide-react';
import TestEvidence from './TestEvidence';

function normalizeExerciseFiles(exercise) {
  if (Array.isArray(exercise.files)) return exercise.files;
  if (exercise.starterCode) {
    return [{
      id: 'exercise-source',
      name: exercise.editableFile || 'Main.java',
      path: exercise.editableFile || 'Main.java',
      editable: true,
      role: 'editable',
      content: exercise.starterCode
    }];
  }
  return [];
}

function cloneFiles(files) {
  return files.map((file) => ({ ...file }));
}

function getEntryFileId(files, entryFileId) {
  if (entryFileId && files.some((file) => file.id === entryFileId)) return entryFileId;
  return files.find((file) => file.editable !== false)?.id || files[0]?.id || null;
}

function getLineNumbers(source) {
  return source.split('\n').map((_, index) => index + 1);
}

function serializeWorkingFiles(files) {
  return files.map((file) => ({
    id: file.id,
    path: file.path || file.name,
    name: file.name,
    editable: file.editable !== false,
    content: file.content
  }));
}

function FileTabs({ files, activeFileId, onSelect }) {
  if (files.length <= 1) return null;

  const handleKeyDown = (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const currentIndex = files.findIndex((file) => file.id === activeFileId);
    const direction = event.key === 'ArrowRight' ? 1 : -1;
    const nextIndex = (currentIndex + direction + files.length) % files.length;
    onSelect(files[nextIndex].id);
  };

  return (
    <div className="implementation-exercise__file-tabs" role="tablist" aria-label="Exercise files" onKeyDown={handleKeyDown}>
      {files.map((file) => (
        <button
          key={file.id}
          type="button"
          role="tab"
          aria-selected={activeFileId === file.id}
          aria-controls={`exercise-file-panel-${file.id}`}
          className={`implementation-exercise__file-tab${activeFileId === file.id ? ' is-active' : ''}`}
          title={file.path || file.name}
          onClick={() => onSelect(file.id)}
        >
          {file.name}
        </button>
      ))}
    </div>
  );
}

export default function ImplementationExercise({ exercise, isExpanded, onToggleExpand }) {
  const exerciseFiles = useMemo(() => normalizeExerciseFiles(exercise), [exercise]);
  const [workingFiles, setWorkingFiles] = useState(() => cloneFiles(exerciseFiles));
  const [activeFileId, setActiveFileId] = useState(() => getEntryFileId(exerciseFiles, exercise.entryFileId));
  const [runState, setRunState] = useState('idle');
  const [resultStatus, setResultStatus] = useState('failed');
  const [evidenceExpanded, setEvidenceExpanded] = useState(true);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState(() => exercise.evidence?.find((item) => item.status === 'failed')?.id || exercise.evidence?.[0]?.id);
  const demoTimerRef = useRef(null);
  const lastRunPayloadRef = useRef(null);

  const activeFile = workingFiles.find((file) => file.id === activeFileId) || workingFiles[0];
  const sourceCode = activeFile?.content || '';
  const lineNumbers = useMemo(() => getLineNumbers(sourceCode), [sourceCode]);
  const isReadOnly = activeFile ? activeFile.editable === false : true;
  const workspaceId = `exercise-${exercise.id}`;

  useEffect(() => {
    return () => {
      if (demoTimerRef.current) window.clearTimeout(demoTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!exercise.id) return;
    if (demoTimerRef.current) window.clearTimeout(demoTimerRef.current);
    setWorkingFiles(cloneFiles(exerciseFiles));
    setActiveFileId(getEntryFileId(exerciseFiles, exercise.entryFileId));
    setRunState('idle');
    setResultStatus('failed');
    setEvidenceExpanded(true);
    setSelectedEvidenceId(exercise.evidence?.find((item) => item.status === 'failed')?.id || exercise.evidence?.[0]?.id);
  }, [exercise.id, exercise.entryFileId, exercise.evidence, exerciseFiles]);

  const handleFileSelect = (fileId) => {
    setActiveFileId(fileId);
  };

  const handleSourceChange = (event) => {
    if (!activeFile || isReadOnly) return;
    const nextContent = event.target.value;
    setWorkingFiles((currentFiles) => currentFiles.map((file) => (
      file.id === activeFile.id ? { ...file, content: nextContent } : file
    )));
  };

  const executeDemo = (mode) => {
    if (runState === 'running' || workingFiles.length === 0) return;

    // Keep execution at workspace scope even while the local behavior is simulated.
    lastRunPayloadRef.current = {
      exerciseId: exercise.id,
      files: serializeWorkingFiles(workingFiles)
    };

    if (!isExpanded) onToggleExpand();
    setRunState('running');
    demoTimerRef.current = window.setTimeout(() => {
      setResultStatus(mode === 'check' ? 'passed' : 'failed');
      setSelectedEvidenceId(mode === 'check' ? exercise.evidence?.[0]?.id : exercise.evidence?.find((item) => item.status === 'failed')?.id);
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
    setWorkingFiles(cloneFiles(exerciseFiles));
    setActiveFileId((currentId) => getEntryFileId(exerciseFiles, currentId));
    setRunState('idle');
    setResultStatus('failed');
    setSelectedEvidenceId(exercise.evidence?.find((item) => item.status === 'failed')?.id || exercise.evidence?.[0]?.id);
    setEvidenceExpanded(true);
  };

  if (workingFiles.length === 0) {
    return (
      <section className="implementation-exercise implementation-exercise--unavailable" aria-labelledby={`${workspaceId}-title`}>
        <p className="learning-eyebrow">{exercise.eyebrow}</p>
        <h3 id={`${workspaceId}-title`}>{exercise.title}</h3>
        <p>Exercise source unavailable.</p>
      </section>
    );
  }

  const compactResult = runState === 'completed' && (
    <p className={`implementation-exercise__compact-result${resultStatus === 'passed' ? ' is-passed' : ''}`} role="status" aria-live="polite">
      {resultStatus === 'passed' ? '✓' : '✕'} {resultStatus === 'passed' ? '5 / 5' : '4 / 5'} behaviors verified
    </p>
  );

  return (
    <section
      className={`implementation-exercise${isExpanded ? ' is-expanded' : ' is-compact'}`}
      aria-labelledby={`${workspaceId}-title`}
    >
      <header className="implementation-exercise__header">
        <div>
          <p className="learning-eyebrow">{exercise.eyebrow}</p>
          <h3 id={`${workspaceId}-title`}>{exercise.title}</h3>
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
        <span>{exercise.language}</span>
        <span>{exercise.difficulty}</span>
        <span>~{exercise.estimatedMinutes} MIN</span>
      </div>
      <p className="implementation-exercise__description">{exercise.description}</p>

      <div id={workspaceId} className="implementation-exercise__workspace" role="region" aria-label="Coding exercise workspace">
        <FileTabs files={workingFiles} activeFileId={activeFileId} onSelect={handleFileSelect} />

        <div className="implementation-exercise__toolbar">
          <div className="implementation-exercise__file-identity">
            {workingFiles.length === 1 ? (
              <span className="implementation-exercise__file-label" title={activeFile.path || activeFile.name}>{activeFile.name}</span>
            ) : (
              <span className="implementation-exercise__file-label" title={activeFile.path || activeFile.name}>{activeFile.name}</span>
            )}
            {isReadOnly && <span className="implementation-exercise__file-status">Reference · Read only</span>}
          </div>
          {isExpanded && (
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
          )}
        </div>

        <div
          id={`exercise-file-panel-${activeFile.id}`}
          className={`learning-editor${isExpanded ? ' learning-editor--expanded' : ' learning-editor--compact'}${isReadOnly ? ' learning-editor--read-only' : ''}`}
          role="tabpanel"
          aria-label={`${activeFile.name} editor`}
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
            aria-label={`${activeFile.name} source code`}
            aria-readonly={isReadOnly}
          />
        </div>
      </div>

      {runState === 'running' && <div className="implementation-exercise__running" role="status" aria-live="polite">Running workspace checks…</div>}

      {isExpanded && runState !== 'running' && (
        <TestEvidence
          evidence={exercise.evidence}
          expanded={evidenceExpanded}
          onToggle={() => setEvidenceExpanded((current) => !current)}
          selectedId={selectedEvidenceId}
          onSelect={setSelectedEvidenceId}
          resultStatus={resultStatus}
        />
      )}

      {!isExpanded && compactResult}

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
