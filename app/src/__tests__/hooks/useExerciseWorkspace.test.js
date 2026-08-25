import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../../api/client';
import useExerciseWorkspace from '../../hooks/useExerciseWorkspace';

const metadata = {
  id: 'java-lld-oop3-point-threedpoint',
  lessonSlug: '04-oop-3-polymorphism-interfaces',
  title: 'Point & ThreedPoint — Method Overriding',
  language: 'java',
  difficulty: 'introductory',
  estimatedMinutes: 10,
  instructions: null,
  files: [
    {
      id: 'point',
      path: 'src/main/java/Point.java',
      displayName: 'Point.java',
      editable: true,
      starterContent: 'class Point {}'
    },
    {
      id: 'threed-point',
      path: 'src/main/java/ThreedPoint.java',
      displayName: 'ThreedPoint.java',
      editable: true,
      starterContent: 'class ThreedPoint extends Point {}'
    }
  ],
  evidence: [
    { id: 'point-x', label: 'Point declares protected int x' },
    { id: 'point-y', label: 'Point declares protected int y' }
  ]
};

function executionResponse(status = 'success') {
  return {
    runId: 'run-1',
    exerciseId: metadata.id,
    status,
    passed: status === 'success',
    durationMilliseconds: 42,
    summary: { total: 2, passed: status === 'success' ? 2 : 1, failed: status === 'success' ? 0 : 1, errors: 0, skipped: 0 },
    evidence: [
      { id: 'point-x', label: 'Point declares protected int x', status: status === 'success' ? 'passed' : 'failed', durationMilliseconds: 1, message: status === 'success' ? null : 'Expected protected field.' },
      { id: 'point-y', label: 'Point declares protected int y', status: 'passed', durationMilliseconds: 1, message: null }
    ],
    diagnostics: { compilerOutput: null, runtimeOutput: null }
  };
}

describe('useExerciseWorkspace', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(api.exercises, 'getMetadata').mockResolvedValue(metadata);
    vi.spyOn(api.exercises, 'run').mockResolvedValue(executionResponse());
    vi.spyOn(api.exercises, 'check').mockResolvedValue(executionResponse('testFailure'));
  });

  it('initializes starter files and preserves independent edits across files', async () => {
    const { result } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));

    expect(result.current.workingFiles.map((file) => file.content)).toEqual([
      'class Point {}',
      'class ThreedPoint extends Point {}'
    ]);

    act(() => {
      result.current.updateFile('point', 'edited point');
      result.current.setActiveFileId('threed-point');
      result.current.updateFile('threed-point', 'edited three');
    });

    expect(result.current.workingFiles.map((file) => file.content)).toEqual([
      'edited point',
      'edited three'
    ]);
    expect(result.current.activeFileId).toBe('threed-point');

    act(() => result.current.reset());

    expect(result.current.workingFiles.map((file) => file.content)).toEqual([
      'class Point {}',
      'class ThreedPoint extends Point {}'
    ]);
    expect(result.current.execution.status).toBe('idle');
  });

  it('submits an immutable snapshot and marks a result stale when source changes', async () => {
    let resolveRun;
    let submittedFiles;
    api.exercises.run.mockImplementation((_exerciseId, files) => {
      submittedFiles = files;
      return new Promise((resolve) => {
        resolveRun = resolve;
      });
    });

    const { result } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));

    act(() => result.current.updateFile('point', 'snapshot point'));
    act(() => { void result.current.execute('run'); });
    await waitFor(() => expect(result.current.isExecutionActive).toBe(true));

    act(() => result.current.updateFile('point', 'newer point while running'));

    expect(submittedFiles).toEqual([
      { path: 'src/main/java/Point.java', content: 'snapshot point' },
      { path: 'src/main/java/ThreedPoint.java', content: 'class ThreedPoint extends Point {}' }
    ]);

    await act(async () => {
      resolveRun(executionResponse());
    });
    await waitFor(() => expect(result.current.execution.status).toBe('success'));
    expect(result.current.execution.stale).toBe(true);
  });

  it('marks a completed result stale when source changes afterward', async () => {
    const { result } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));

    await act(async () => result.current.execute('run'));
    await waitFor(() => expect(result.current.execution.status).toBe('success'));
    expect(result.current.execution.stale).toBe(false);

    act(() => result.current.updateFile('point', 'changed after result'));

    expect(result.current.execution.stale).toBe(true);
  });

  it('keeps Check separate and blocks duplicate execution while running', async () => {
    let resolveRun;
    api.exercises.run.mockImplementation(() => new Promise((resolve) => {
      resolveRun = resolve;
    }));

    const { result } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));

    act(() => {
      result.current.execute('run');
      result.current.execute('check');
    });
    await waitFor(() => expect(result.current.isExecutionActive).toBe(true));
    expect(api.exercises.run).toHaveBeenCalledTimes(1);
    expect(api.exercises.check).not.toHaveBeenCalled();

    await act(async () => resolveRun(executionResponse()));
    await waitFor(() => expect(result.current.isExecutionActive).toBe(false));

    await act(async () => result.current.execute('check'));
    await waitFor(() => expect(result.current.execution.operation).toBe('check'));
    expect(api.exercises.check).toHaveBeenCalledTimes(1);
  });

  it.each(['success', 'testFailure', 'compilationFailure', 'timeout'])('accepts learner result status %s', async (status) => {
    api.exercises.run.mockResolvedValue(executionResponse(status));
    const { result } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));

    await act(async () => result.current.execute('run'));
    await waitFor(() => expect(result.current.execution.status).toBe(status));
  });

  it.each([429, 503, 0])('maps API/network failure %s to apiFailure', async (status) => {
    api.exercises.run.mockRejectedValue({ status });
    const { result } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));

    await act(async () => result.current.execute('run'));
    await waitFor(() => expect(result.current.execution.status).toBe('apiFailure'));
  });

  it('aborts execution on unmount', async () => {
    let requestOptions;
    api.exercises.run.mockImplementation((_exerciseId, _files, options) => {
      requestOptions = options;
      return new Promise(() => {});
    });

    const { result, unmount } = renderHook(() => useExerciseWorkspace(metadata.id));
    await waitFor(() => expect(result.current.metadataState).toBe('ready'));
    act(() => { void result.current.execute('run'); });
    await waitFor(() => expect(result.current.isExecutionActive).toBe(true));

    unmount();

    expect(requestOptions.signal.aborted).toBe(true);
  });
});
