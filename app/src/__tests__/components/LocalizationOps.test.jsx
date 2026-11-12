import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LocalizationOps from '../../pages/Localization/LocalizationOps';

const { getProjects, getUsage, getUsageEvents, getRates, getControls, updateControls, getTeams, getAgreement } = vi.hoisted(() => ({
  getProjects: vi.fn(),
  getUsage: vi.fn(),
  getUsageEvents: vi.fn(),
  getRates: vi.fn(),
  getControls: vi.fn(),
  updateControls: vi.fn(),
  getTeams: vi.fn(),
  getAgreement: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: {
    localization: { getProjects },
    localizationOps: { getUsage, getUsageEvents, getRates, getControls, updateControls, getTeams, getAgreement }
  }
}));

const emptyUsage = {
  month: '2026-11',
  projectSlug: null,
  meters: [],
  byOperation: [],
  byLocale: [],
  byDay: [],
  ratesMissing: [],
  caps: []
};

const controls = {
  projectSlug: 'p1',
  aiEnabled: true,
  caps: [
    { kind: 'machine-translation', monthlyLimit: 2000000, used: 23895 },
    { kind: 'llm', monthlyLimit: 5000000, used: 75102 }
  ]
};

function renderOps() {
  return render(
    <MemoryRouter initialEntries={['/lab-projects/localization/ops']}>
      <LocalizationOps />
    </MemoryRouter>
  );
}

async function selectProject() {
  fireEvent.change(await screen.findByLabelText('Project'), { target: { value: 'p1' } });
  await screen.findByText('23,895 / 2,000,000');
}

beforeEach(() => {
  vi.clearAllMocks();
  getProjects.mockResolvedValue([{ slug: 'p1', name: 'P1', locales: [{ localeCode: 'de-DE', displayName: 'German' }] }]);
  getUsage.mockResolvedValue(emptyUsage);
  getUsageEvents.mockResolvedValue([]);
  getRates.mockResolvedValue([]);
  getTeams.mockResolvedValue([]);
  getAgreement.mockResolvedValue({ tier: 'Gold', clientAlias: 'Client Team Kestrel', validFrom: '2026-01-01T00:00:00Z', validTo: null, teams: [] });
  getControls.mockResolvedValue(controls);
  updateControls.mockImplementation(async (slug) => ({ projectSlug: slug, aiEnabled: true, caps: [] }));
});

describe('LocalizationOps', () => {
  it('shows caps bars with used and limit numbers', async () => {
    renderOps();
    await selectProject();

    expect(screen.getByText('75,102 / 5,000,000')).toBeInTheDocument();
  });

  it('sends null for a cleared limit and omits untouched fields', async () => {
    renderOps();
    await selectProject();

    fireEvent.change(await screen.findByLabelText('Machine translation cap (characters)'), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: 'Save controls' }));

    expect(await screen.findByText('Controls saved.')).toBeInTheDocument();
    expect(updateControls).toHaveBeenCalledWith('p1', { machineTranslationMonthlyLimit: null });
  });

  it('shows the access message when any call returns 403', async () => {
    getUsage.mockRejectedValue({ message: 'Access denied', status: 403 });
    renderOps();

    expect(await screen.findByText('Operations access requires an administrator account.')).toBeInTheDocument();
  });
});
