import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import {
  createWorkingFiles,
  getInitialFileId,
  getSourceFingerprint,
  mergeEvidence,
  normalizeExerciseMetadata
} from '../api/exerciseModels';

const EXECUTION_TIMEOUT_MS = 135000;

function createRequestId() {
  return globalThis.crypto?.randomUUID?.()
    || `exercise-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function useExerciseWorkspace(exerciseId) {
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

  const filesRef = useRef([]);
  const metadataControllerRef = useRef(null);
  const executionControllerRef = useRef(null);
  const activeRequestRef = useRef(null);

  useEffect(() => {
    metadataControllerRef.current?.abort();
    executionControllerRef.current?.abort();
    activeRequestRef.current = null;

    const controller = new AbortController();
    metadataControllerRef.current = controller;
    let isCurrent = true;

    setMetadataState('loading');
    setMetadata(null);
    setWorkingFiles([]);
    filesRef.current = [];
    setActiveFileId(null);
    setExecution({ status: 'idle', operation: null, result: null, error: null, stale: false });

    if (!exerciseId) {
      setMetadataState('error');
      return () => {
        isCurrent = false;
        controller.abort();
      };
    }

    api.exercises.getMetadata(exerciseId, { signal: controller.signal })
      .then((response) => {
        if (!isCurrent) return;
        const nextMetadata = normalizeExerciseMetadata(response);
        const nextFiles = createWorkingFiles(nextMetadata);
        setMetadata(nextMetadata);
        setWorkingFiles(nextFiles);
        filesRef.current = nextFiles;
        setActiveFileId(getInitialFileId(nextFiles));
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
  }, [exerciseId, metadataAttempt]);

  useEffect(() => () => {
    metadataControllerRef.current?.abort();
    executionControllerRef.current?.abort();
    activeRequestRef.current = null;
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
  }, []);

  const reset = useCallback(() => {
    if (!metadata || execution.status === 'running') return;
    const nextFiles = createWorkingFiles(metadata);
    setWorkingFiles(nextFiles);
    filesRef.current = nextFiles;
    setActiveFileId(getInitialFileId(nextFiles));
    setExecution({ status: 'idle', operation: null, result: null, error: null, stale: false });
  }, [execution.status, metadata]);

  const retryMetadata = useCallback(() => {
    setMetadataAttempt((current) => current + 1);
  }, []);

  const execute = useCallback(async (operation) => {
    if (
      metadataState !== 'ready'
      || !metadata
      || execution.status === 'running'
      || activeRequestRef.current
      || !['run', 'check'].includes(operation)
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
      const response = await api.exercises[operation](metadata.id, snapshot, {
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
  }, [execution.status, metadata, metadataState]);

  return {
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
    isExecutionActive: execution.status === 'running'
  };
}
