import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import { useOptionalAuth } from '../context/AuthContext';
import {
  createWorkingFiles,
  getInitialFileId,
  getSourceFingerprint,
  mergeEvidence,
  normalizeExerciseMetadata,
  normalizeExerciseSolution
} from '../api/exerciseModels';

const EXECUTION_TIMEOUT_MS = 135000;
const DRAFT_SAVE_DELAY_MS = 1500;

const EMPTY_HISTORY = Object.freeze({
  attemptCount: 0,
  lastAttempt: null,
  bestAttempt: null,
  solved: false,
  restoredDraft: false,
  draftSavedAt: null
});

function applyDraft(files, draftFiles) {
  if (!Array.isArray(draftFiles) || draftFiles.length === 0) return { files, restored: false };
  const byPath = new Map(draftFiles.map((file) => [file.path, file.content]));
  let restored = false;
  const next = files.map((file) => {
    if (file.editable === false || !byPath.has(file.path)) return file;
    restored = true;
    return { ...file, content: byPath.get(file.path) };
  });
  return { files: next, restored };
}

function createRequestId() {
  return globalThis.crypto?.randomUUID?.()
    || `exercise-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function useExerciseWorkspace(exerciseId) {
  const { isAuthenticated } = useOptionalAuth();
  const [history, setHistory] = useState(EMPTY_HISTORY);
  const draftTimerRef = useRef(null);
  const [metadataAttempt, setMetadataAttempt] = useState(0);
  const [metadataState, setMetadataState] = useState('loading');
  const [metadata, setMetadata] = useState(null);
  const [workingFiles, setWorkingFiles] = useState([]);
  const [activeFileId, setActiveFileId] = useState(null);
  const [execution, setExecution] = useState({
    status: 'idle',
    operation: null,
    result: null,
    error: null,
    stale: false
  });
  const [solutionState, setSolutionState] = useState('idle');
  const [solution, setSolution] = useState(null);
  const [solutionError, setSolutionError] = useState(null);

  const filesRef = useRef([]);
  const metadataControllerRef = useRef(null);
  const executionControllerRef = useRef(null);
  const activeRequestRef = useRef(null);
  const solutionControllerRef = useRef(null);
  const solutionRequestRef = useRef(null);

  useEffect(() => {
    metadataControllerRef.current?.abort();
    executionControllerRef.current?.abort();
    solutionControllerRef.current?.abort();
    activeRequestRef.current = null;
    solutionRequestRef.current = null;

    const controller = new AbortController();
    metadataControllerRef.current = controller;
    let isCurrent = true;

    setMetadataState('loading');
    setMetadata(null);
    setWorkingFiles([]);
    filesRef.current = [];
    setActiveFileId(null);
    setExecution({ status: 'idle', operation: null, result: null, error: null, stale: false });
    setSolutionState('idle');
    setSolution(null);
    setSolutionError(null);

    if (!exerciseId) {
      setMetadataState('error');
      return () => {
        isCurrent = false;
        controller.abort();
      };
    }

    setHistory(EMPTY_HISTORY);

    // The learner's saved code is optional: a failure (or being signed out) falls back to the starter.
    const loadSaved = isAuthenticated
      ? api.exercises.getWorkspace(exerciseId, { signal: controller.signal }).catch(() => null)
      : Promise.resolve(null);

    Promise.all([api.exercises.getMetadata(exerciseId, { signal: controller.signal }), loadSaved])
      .then(([response, saved]) => {
        if (!isCurrent) return;
        const nextMetadata = normalizeExerciseMetadata(response);
        const { files: nextFiles, restored } = applyDraft(createWorkingFiles(nextMetadata), saved?.draftFiles);
        setMetadata(nextMetadata);
        setWorkingFiles(nextFiles);
        filesRef.current = nextFiles;
        setActiveFileId(getInitialFileId(nextFiles));
        if (saved) {
          setHistory({
            attemptCount: saved.attemptCount || 0,
            lastAttempt: saved.lastAttempt || null,
            bestAttempt: saved.bestAttempt || null,
            solved: Boolean(saved.solved),
            restoredDraft: restored,
            draftSavedAt: saved.draftUpdatedAt || null
          });
        }
        setMetadataState('ready');
      })
      .catch((error) => {
        if (!isCurrent || controller.signal.aborted) return;
        setMetadataState('error');
        setExecution((current) => ({ ...current, status: 'metadataFailure', error }));
      });

    return () => {
      isCurrent = false;
      controller.abort();
      if (metadataControllerRef.current === controller) metadataControllerRef.current = null;
    };
  }, [exerciseId, metadataAttempt, isAuthenticated]);

  // Autosave the editable files (debounced) so work survives reloads and other devices.
  const scheduleDraftSave = useCallback(() => {
    if (!isAuthenticated || !exerciseId) return;
    clearTimeout(draftTimerRef.current);
    draftTimerRef.current = setTimeout(() => {
      const files = filesRef.current
        .filter((file) => file.editable !== false)
        .map((file) => ({ path: file.path, content: file.content }));
      if (files.length === 0) return;
      api.exercises.saveDraft(exerciseId, files)
        .then(() => setHistory((current) => ({ ...current, draftSavedAt: new Date().toISOString() })))
        .catch(() => {});
    }, DRAFT_SAVE_DELAY_MS);
  }, [exerciseId, isAuthenticated]);

  useEffect(() => () => clearTimeout(draftTimerRef.current), [exerciseId]);

  useEffect(() => () => {
    metadataControllerRef.current?.abort();
    executionControllerRef.current?.abort();
    solutionControllerRef.current?.abort();
    activeRequestRef.current = null;
    solutionRequestRef.current = null;
  }, []);

  const activeFile = workingFiles.find((file) => file.id === activeFileId) || workingFiles[0] || null;

  const updateFile = useCallback((fileId, content) => {
    setWorkingFiles((currentFiles) => {
      const nextFiles = currentFiles.map((file) => (
        file.id === fileId ? { ...file, content } : file
      ));
      filesRef.current = nextFiles;
      return nextFiles;
    });
    setExecution((current) => current.result
      ? { ...current, stale: true }
      : current);
    scheduleDraftSave();
  }, [scheduleDraftSave]);

  const reset = useCallback(() => {
    if (!metadata || execution.status === 'running') return;
    const nextFiles = createWorkingFiles(metadata);
    setWorkingFiles(nextFiles);
    filesRef.current = nextFiles;
    setActiveFileId(getInitialFileId(nextFiles));
    setExecution({ status: 'idle', operation: null, result: null, error: null, stale: false });
    setHistory((current) => ({ ...current, restoredDraft: false }));
    scheduleDraftSave();
  }, [execution.status, metadata, scheduleDraftSave]);

  const retryMetadata = useCallback(() => {
    setMetadataAttempt((current) => current + 1);
  }, []);

  const revealSolution = useCallback(async ({ force = false } = {}) => {
    if (metadataState !== 'ready' || !metadata || solutionRequestRef.current) return;
    if (!force && solutionState === 'ready') return;

    const controller = new AbortController();
    const requestId = createRequestId();
    solutionControllerRef.current = controller;
    solutionRequestRef.current = requestId;
    setSolutionState('loading');
    setSolutionError(null);

    try {
      const response = await api.exercises.getSolution(metadata.id, { signal: controller.signal });
      if (controller.signal.aborted || solutionRequestRef.current !== requestId) return;
      setSolution(normalizeExerciseSolution(response));
      setSolutionState('ready');
    } catch (error) {
      if (solutionRequestRef.current !== requestId || controller.signal.aborted) return;
      setSolution(null);
      setSolutionState('error');
      setSolutionError(error);
    } finally {
      if (solutionRequestRef.current === requestId) {
        solutionRequestRef.current = null;
        solutionControllerRef.current = null;
      }
    }
  }, [metadata, metadataState, solutionState]);

  const retrySolution = useCallback(() => {
    void revealSolution({ force: true });
  }, [revealSolution]);

  const execute = useCallback(async (operation) => {
    if (
      metadataState !== 'ready'
      || !metadata
      || execution.status === 'running'
      || activeRequestRef.current
      || operation !== 'run'
    ) {
      return;
    }

    executionControllerRef.current?.abort();
    const controller = new AbortController();
    const requestId = createRequestId();
    const snapshot = Object.freeze(filesRef.current
      .filter((file) => file.editable !== false)
      .map((file) => Object.freeze({ path: file.path, content: file.content })));
    const snapshotFingerprint = getSourceFingerprint(filesRef.current);

    executionControllerRef.current = controller;
    activeRequestRef.current = requestId;
    setExecution((current) => ({
      ...current,
      status: 'running',
      operation,
      error: null,
      stale: false
    }));

    try {
      const response = await api.exercises.run(metadata.id, snapshot, {
        signal: controller.signal,
        timeoutMs: EXECUTION_TIMEOUT_MS,
        clientRequestId: requestId
      });

      if (controller.signal.aborted || activeRequestRef.current !== requestId) return;

      const result = {
        ...response,
        evidence: mergeEvidence(metadata.evidence, response.evidence)
      };
      const isStale = getSourceFingerprint(filesRef.current) !== snapshotFingerprint;
      if (isAuthenticated) {
        // The server recorded this run (and saved the code); mirror it locally.
        clearTimeout(draftTimerRef.current);
        const attempt = {
          status: response.status,
          testsTotal: response.summary?.total ?? 0,
          testsPassed: response.summary?.passed ?? 0,
          durationMilliseconds: response.durationMilliseconds,
          submittedAt: new Date().toISOString()
        };
        setHistory((current) => {
          const ratio = (a) => (a && a.testsTotal ? a.testsPassed / a.testsTotal : -1);
          const better = !current.bestAttempt
            || (attempt.status === 'success' && current.bestAttempt.status !== 'success')
            || ratio(attempt) > ratio(current.bestAttempt);
          return {
            ...current,
            attemptCount: current.attemptCount + 1,
            lastAttempt: attempt,
            bestAttempt: better ? attempt : current.bestAttempt,
            solved: current.solved || attempt.status === 'success',
            draftSavedAt: attempt.submittedAt
          };
        });
      }
      setExecution({
        status: response.status,
        operation,
        result,
        error: null,
        stale: isStale
      });
    } catch (error) {
      if (activeRequestRef.current !== requestId || controller.signal.aborted) return;
      setExecution((current) => ({
        ...current,
        status: 'apiFailure',
        error,
        operation
      }));
    } finally {
      if (activeRequestRef.current === requestId) {
        activeRequestRef.current = null;
        executionControllerRef.current = null;
      }
    }
  }, [execution.status, metadata, metadataState, isAuthenticated]);

  return {
    history,
    isAuthenticated,
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
    isExecutionActive: execution.status === 'running',
    solution,
    solutionState,
    solutionError,
    revealSolution,
    retrySolution
  };
}
