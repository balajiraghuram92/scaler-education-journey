import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import CodingAssignment from '../../components/learning/CodingAssignment';

const { getMetadata, getWorkspace, saveDraft, authState } = vi.hoisted(() => ({
  getMetadata: vi.fn(),
  getWorkspace: vi.fn(),
  saveDraft: vi.fn(),
  authState: { isAuthenticated: true }
}));

vi.mock('../../api/client', () => ({
  api: {
    exercises: { getMetadata, getWorkspace, saveDraft, run: vi.fn(), getSolution: vi.fn() },
    me: { setProblemStatus: vi.fn() }
  }
}));

vi.mock('../../context/AuthContext', () => ({
  useOptionalAuth: () => authState
}));

const metadata = {
  id: 'py-09-frequency-count',
  lessonSlug: 'py-09',
  title: 'Frequency Count with a Dictionary',
  language: 'python',
  difficulty: 'warm-up',
  estimatedMinutes: 10,
  instructions: 'Implement `count_frequency`.',
  files: [
    { id: 'count-freq', path: 'config/countFreq.py', displayName: 'countFreq.py', editable: true, starterContent: 'def count_frequency(arr):\n    raise NotImplementedError\n' }
  ],
  evidence: [{ id: 'counts', label: 'Counts every element' }]
};

const problem = {
  id: 7,
  slug: 'py-09-frequency-count',
  title: 'Frequency Count',
  difficulty: 'Warm-up',
  sourceType: 'FROM_MATERIAL',
  problemStatement: 'Count things.',
  runCommand: 'pytest -q',
  exerciseId: 'py-09-frequency-count'
};

function renderCard(overrides = {}) {
  return render(
    <MemoryRouter>
      <CodingAssignment problem={{ ...problem, ...overrides }} index={0} isAuthenticated={authState.isAuthenticated} />
    </MemoryRouter>
  );
}

describe('CodingAssignment live exercise', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    authState.isAuthenticated = true;
    getMetadata.mockResolvedValue(metadata);
  });

  it('hides the browser editor when the assignment has no live exercise', () => {
    renderCard({ exerciseId: null });
    expect(screen.queryByRole('button', { name: /solve in the browser/i })).toBeNull();
    expect(screen.getByText('Run:')).toBeTruthy();
  });

  it('opens the editor and restores the learner\'s saved code and history', async () => {
    getWorkspace.mockResolvedValue({
      exerciseId: problem.exerciseId,
      draftFiles: [{ path: 'config/countFreq.py', content: 'def count_frequency(arr):\n    return {}\n' }],
      draftUpdatedAt: '2026-10-21T10:00:00Z',
      lastAttempt: { status: 'testFailure', testsTotal: 7, testsPassed: 3 },
      bestAttempt: { status: 'testFailure', testsTotal: 7, testsPassed: 5 },
      attemptCount: 4,
      solved: false
    });

    renderCard();
    expect(screen.getByText('Or run locally:')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /solve in the browser/i }));

    await waitFor(() => expect(screen.getByText('Frequency Count with a Dictionary')).toBeTruthy());
    expect(getWorkspace).toHaveBeenCalledWith('py-09-frequency-count', expect.anything());
    expect(screen.getByDisplayValue(/return \{\}/)).toBeTruthy();
    expect(screen.getByText(/Restored your saved code · 4 runs · best 5\/7 checks/)).toBeTruthy();
  });

  it('uses the starter and asks to sign in when signed out', async () => {
    authState.isAuthenticated = false;
    renderCard();
    fireEvent.click(screen.getByRole('button', { name: /solve in the browser/i }));

    await waitFor(() => expect(screen.getByDisplayValue(/raise NotImplementedError/)).toBeTruthy());
    expect(getWorkspace).not.toHaveBeenCalled();
    expect(screen.getByText(/Sign in to save your code/)).toBeTruthy();
  });
});
