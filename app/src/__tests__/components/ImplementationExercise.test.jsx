import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../../api/client';
import ImplementationExercise from '../../components/learning/ImplementationExercise';

const metadata = {
  id: 'java-lld-oop3-point-threedpoint',
  lessonSlug: '04-oop-3-polymorphism-interfaces',
  title: 'Point & ThreedPoint — Method Overriding',
  language: 'java',
  difficulty: 'introductory',
  estimatedMinutes: 10,
  instructions: null,
  files: [
    { id: 'point', path: 'src/main/java/Point.java', displayName: 'Point.java', editable: true, starterContent: 'class Point {}' },
    { id: 'threed-point', path: 'src/main/java/ThreedPoint.java', displayName: 'ThreedPoint.java', editable: true, starterContent: 'class ThreedPoint extends Point {}' }
  ],
  evidence: [
    { id: 'point-x', label: 'Point declares protected int x' },
    { id: 'point-y', label: 'Point declares protected int y' }
  ]
};

const solution = {
  exerciseId: metadata.id,
  files: [
    { id: 'point', path: 'src/main/java/Point.java', displayName: 'Point.java', language: 'java', content: 'class Point { int x; }', displayOrder: 0 },
    { id: 'threed-point', path: 'src/main/java/ThreedPoint.java', displayName: 'ThreedPoint.java', language: 'java', content: 'class ThreedPoint extends Point { int z; }', displayOrder: 1 }
  ]
};

function result(status = 'success', overrides = {}) {
  return {
    runId: `run-${status}`,
    exerciseId: metadata.id,
    status,
    passed: status === 'success',
    durationMilliseconds: 42,
    summary: { total: 2, passed: status === 'success' ? 2 : 1, failed: status === 'success' ? 0 : 1, errors: 0, skipped: 0 },
    evidence: [
      { id: 'point-x', label: 'Point declares protected int x', status: status === 'success' ? 'passed' : 'failed', durationMilliseconds: 1, message: status === 'success' ? null : 'Expected protected field.' },
      { id: 'point-y', label: 'Point declares protected int y', status: 'passed', durationMilliseconds: 1, message: null }
    ],
    diagnostics: { compilerOutput: null, runtimeOutput: null },
    ...overrides
  };
}

function deferred() {
  let resolve;
  const promise = new Promise((res) => {
    resolve = res;
  });
  return { promise, resolve };
}

describe('ImplementationExercise', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(api.exercises, 'getMetadata').mockResolvedValue(metadata);
    vi.spyOn(api.exercises, 'run').mockResolvedValue(result());
    vi.spyOn(api.exercises, 'getSolution').mockResolvedValue(solution);
  });

  it('starts with a persistent collapsed reference solution control', async () => {
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    await screen.findByLabelText('Point.java source code');

    const referencePanel = screen.getByRole('region', { name: 'Reference solution' });
    const solutionToggle = screen.getByRole('button', { name: 'View solution' });
    expect(referencePanel).toBeInTheDocument();
    expect(solutionToggle).toHaveAttribute('aria-expanded', 'false');
    expect(solutionToggle).toHaveAttribute('aria-controls', `exercise-${metadata.id}-reference-solution-content`);
    expect(screen.queryByRole('button', { name: /Check solution/i })).not.toBeInTheDocument();
    expect(within(referencePanel).queryByLabelText('Point.java source code')).not.toBeInTheDocument();
  });

  it('loads API-provided starter files and keeps edits when switching tabs', async () => {
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    const pointEditor = await screen.findByLabelText('Point.java source code');

    expect(pointEditor).toHaveValue('class Point {}');
    fireEvent.change(pointEditor, { target: { value: 'edited point' } });
    fireEvent.click(screen.getByRole('tab', { name: 'ThreedPoint.java' }));
    const threedPointEditor = screen.getByLabelText('ThreedPoint.java source code');
    fireEvent.change(threedPointEditor, { target: { value: 'edited three' } });
    fireEvent.click(screen.getByRole('tab', { name: 'Point.java' }));

    expect(screen.getByLabelText('Point.java source code')).toHaveValue('edited point');
    fireEvent.click(screen.getByRole('tab', { name: 'ThreedPoint.java' }));
    expect(screen.getByLabelText('ThreedPoint.java source code')).toHaveValue('edited three');
  });

  it('keeps the editor editable while Run uses an immutable snapshot', async () => {
    const pending = deferred();
    api.exercises.run.mockReturnValue(pending.promise);
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    const pointEditor = await screen.findByLabelText('Point.java source code');
    fireEvent.change(pointEditor, { target: { value: 'captured point' } });
    fireEvent.click(screen.getByRole('button', { name: 'Run (Ctrl + Enter)' }));

    await waitFor(() => expect(screen.getByRole('button', { name: 'Run (Ctrl + Enter)' })).toBeDisabled());
    expect(screen.getByRole('button', { name: /View solution/ })).toBeDisabled();
    expect(screen.getByRole('button', { name: /Reset/ })).toBeDisabled();
    expect(pointEditor).not.toHaveAttribute('readonly');

    fireEvent.change(pointEditor, { target: { value: 'newer point' } });
    expect(api.exercises.run).toHaveBeenCalledWith(
      metadata.id,
      [
        { path: 'src/main/java/Point.java', content: 'captured point' },
        { path: 'src/main/java/ThreedPoint.java', content: 'class ThreedPoint extends Point {}' }
      ],
      expect.objectContaining({ clientRequestId: expect.any(String), signal: expect.any(AbortSignal) })
    );

    pending.resolve(result());
    await waitFor(() => expect(screen.getByText(/earlier source version/)).toBeInTheDocument());
  });

  it('reveals a read-only multi-file reference solution without changing student code', async () => {
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    const pointEditor = await screen.findByLabelText('Point.java source code');
    fireEvent.change(pointEditor, { target: { value: 'student implementation' } });
    fireEvent.click(screen.getByRole('button', { name: /View solution/ }));

    await waitFor(() => expect(api.exercises.getSolution).toHaveBeenCalledTimes(1));
    const referencePanel = screen.getByRole('region', { name: 'Reference solution' });
    const studentWorkspace = screen.getByRole('region', { name: 'Coding exercise workspace' });
    await waitFor(() => expect(within(referencePanel).getByLabelText('Point.java source code')).toHaveAttribute('readonly'));
    expect(api.exercises.run).not.toHaveBeenCalled();
    expect(within(studentWorkspace).getByLabelText('Point.java source code')).toHaveValue('student implementation');
    expect(within(referencePanel).getByLabelText('Point.java source code')).toHaveValue('class Point { int x; }');
    expect(within(referencePanel).getByRole('tab', { name: 'ThreedPoint.java' })).toHaveAttribute('aria-selected', 'false');
    fireEvent.click(within(referencePanel).getByRole('tab', { name: 'ThreedPoint.java' }));
    await waitFor(() => expect(within(screen.getByRole('region', { name: 'Reference solution' })).getByLabelText('ThreedPoint.java source code')).toHaveValue('class ThreedPoint extends Point { int z; }'));

    const solutionToggle = screen.getByRole('button', { name: 'Hide solution' });
    fireEvent.click(solutionToggle);
    expect(solutionToggle).toHaveAttribute('aria-expanded', 'false');
    expect(within(referencePanel).queryByLabelText('Point.java source code')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'View solution' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'View solution' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Hide solution' })).toHaveAttribute('aria-expanded', 'true'));
    expect(api.exercises.getSolution).toHaveBeenCalledTimes(1);
  });

  it('renders a missing reference solution state and preserves the student editor', async () => {
    api.exercises.getSolution.mockRejectedValue({ status: 404 });
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    const pointEditor = await screen.findByLabelText('Point.java source code');
    fireEvent.change(pointEditor, { target: { value: 'student implementation' } });
    fireEvent.click(screen.getByRole('button', { name: /View solution/ }));

    await waitFor(() => expect(screen.getByText('This exercise does not have a reference solution yet.')).toBeInTheDocument());
    expect(screen.getByLabelText('Point.java source code')).toHaveValue('student implementation');
  });

  it('renders compilation diagnostics and keeps evidence not run', async () => {
    api.exercises.run.mockResolvedValue(result('compilationFailure', {
      evidence: [],
      diagnostics: { compilerOutput: '[ERROR] Point.java:[4,1] illegal start of expression', runtimeOutput: null }
    }));
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    await screen.findByLabelText('Point.java source code');
    fireEvent.click(screen.getByRole('button', { name: /^Run/ }));

    await waitFor(() => expect(screen.getByText('Compiler diagnostics')).toBeInTheDocument());
    expect(screen.getByText(/illegal start of expression/)).toBeInTheDocument();
    expect(screen.getAllByText('notRun').length).toBeGreaterThan(0);
  });

  it('renders timeout as a learner timeout, not a test failure', async () => {
    api.exercises.run.mockResolvedValue(result('timeout', { evidence: [] }));
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    await screen.findByLabelText('Point.java source code');
    fireEvent.click(screen.getByRole('button', { name: /^Run/ }));

    await waitFor(() => expect(screen.getByText('Execution exceeded the allowed time.')).toBeInTheDocument());
    expect(screen.getByText('Timed out · tests not run')).toBeInTheDocument();
  });

  it('renders sanitized infrastructure failure states', async () => {
    api.exercises.run.mockRejectedValue({ status: 503, message: 'docker://internal/socket' });
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    await screen.findByLabelText('Point.java source code');
    fireEvent.click(screen.getByRole('button', { name: /^Run/ }));

    await waitFor(() => expect(screen.getByText('Neuralascent could not execute your code')).toBeInTheDocument());
    expect(screen.queryByText(/docker|socket|internal/i)).not.toBeInTheDocument();
  });

  it('only triggers Run from Ctrl/Cmd+Enter when expanded and ready', async () => {
    const onToggleExpand = vi.fn();
    const { rerender } = render(<ImplementationExercise exerciseId={metadata.id} isExpanded={false} onToggleExpand={onToggleExpand} />);
    const collapsedEditor = await screen.findByLabelText('Point.java source code');
    fireEvent.keyDown(collapsedEditor, { key: 'Enter', ctrlKey: true });
    expect(api.exercises.run).not.toHaveBeenCalled();

    rerender(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={onToggleExpand} />);
    fireEvent.keyDown(screen.getByLabelText('Point.java source code'), { key: 'Enter', ctrlKey: true });
    await waitFor(() => expect(api.exercises.run).toHaveBeenCalledTimes(1));
  });

  it('supports ArrowLeft and ArrowRight file-tab navigation', async () => {
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    await screen.findByRole('tab', { name: 'Point.java' });
    const pointTab = screen.getByRole('tab', { name: 'Point.java' });
    fireEvent.keyDown(pointTab, { key: 'ArrowRight' });
    await waitFor(() => expect(screen.getByRole('tab', { name: 'ThreedPoint.java' })).toHaveAttribute('aria-selected', 'true'));

    const threedPointTab = screen.getByRole('tab', { name: 'ThreedPoint.java' });
    fireEvent.keyDown(threedPointTab, { key: 'ArrowLeft' });
    await waitFor(() => expect(pointTab).toHaveAttribute('aria-selected', 'true'));
  });

  it('uses Home and End to select and focus the boundary file tabs', async () => {
    render(<ImplementationExercise exerciseId={metadata.id} isExpanded onToggleExpand={vi.fn()} />);
    const pointTab = await screen.findByRole('tab', { name: 'Point.java' });
    const threedPointTab = screen.getByRole('tab', { name: 'ThreedPoint.java' });

    threedPointTab.focus();
    fireEvent.keyDown(threedPointTab, { key: 'Home' });
    await waitFor(() => {
      expect(pointTab).toHaveAttribute('aria-selected', 'true');
      expect(document.activeElement).toBe(pointTab);
    });

    pointTab.focus();
    fireEvent.keyDown(pointTab, { key: 'End' });
    await waitFor(() => {
      expect(threedPointTab).toHaveAttribute('aria-selected', 'true');
      expect(document.activeElement).toBe(threedPointTab);
    });
  });
});
