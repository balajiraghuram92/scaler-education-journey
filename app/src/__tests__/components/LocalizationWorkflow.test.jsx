import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LocalizationWorkflow from '../../pages/Localization/LocalizationWorkflow';

const { getProjects, getProject, getProviderHealth, getWorkflow, runWorkflowStep } = vi.hoisted(() => ({
  getProjects: vi.fn(),
  getProject: vi.fn(),
  getProviderHealth: vi.fn(),
  getWorkflow: vi.fn(),
  runWorkflowStep: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: { localization: { getProjects, getProject, getProviderHealth, getWorkflow, runWorkflowStep } }
}));

const project = {
  slug: 'p1',
  name: 'P1',
  sourceLocale: 'en-US',
  tier: null,
  aiEnabled: true,
  locales: []
};

const step = {
  id: 7,
  trigger: 'On Manual Click',
  action: 'Run MT Optimize',
  conditionExpression: null,
  lastRunAt: null,
  lastRunOutcome: null
};

function renderWorkflow() {
  return render(
    <MemoryRouter initialEntries={['/lab-projects/localization/workflow?project=p1']}>
      <LocalizationWorkflow />
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  getProjects.mockResolvedValue([project]);
  getProject.mockResolvedValue(project);
  getProviderHealth.mockResolvedValue([]);
  getWorkflow.mockResolvedValue([step]);
});

describe('LocalizationWorkflow run outcomes', () => {
  it('renders an outcome containing "skipped:" with the warning style', async () => {
    const outcome = '120 strings optimized, 16 skipped: monthly llm cap reached (5000000 of 5000000)';
    runWorkflowStep.mockResolvedValue({ ...step, lastRunAt: '2026-11-12T00:00:00Z', lastRunOutcome: outcome });
    renderWorkflow();

    fireEvent.click(await screen.findByTitle('Run Step'));

    const notice = await screen.findByText(`Run finished with skips: ${outcome}`);
    expect(notice.closest('div')).toHaveStyle('background-color: #FEF3C7');
  });

  it('renders a 409 run as a warning with the server detail', async () => {
    const detail = 'AI assistance is switched off for project P1.';
    runWorkflowStep.mockRejectedValue({ message: detail, status: 409, problemDetails: { detail } });
    renderWorkflow();

    fireEvent.click(await screen.findByTitle('Run Step'));

    const notice = await screen.findByText(detail);
    expect(notice.closest('div')).toHaveStyle('background-color: #FEF3C7');
  });
});
