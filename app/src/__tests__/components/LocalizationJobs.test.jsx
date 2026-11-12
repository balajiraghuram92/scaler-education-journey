import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LocalizationJobs from '../../pages/Localization/LocalizationJobs';

const { getProjects, getProject, getProviderHealth, getJobs, getAgreement, createJob, approveJob, sendBackJob } = vi.hoisted(() => ({
  getProjects: vi.fn(),
  getProject: vi.fn(),
  getProviderHealth: vi.fn(),
  getJobs: vi.fn(),
  getAgreement: vi.fn(),
  createJob: vi.fn(),
  approveJob: vi.fn(),
  sendBackJob: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: {
    localization: { getProjects, getProject, getProviderHealth, getJobs, getAgreement, createJob, approveJob, sendBackJob }
  }
}));

const project = {
  slug: 'auroraline-hud-v3',
  name: 'Auroraline Automotive — HUD Strings',
  sourceLocale: 'en-US',
  tier: 'Gold',
  aiEnabled: true,
  locales: [
    { id: 1, localeCode: 'de-DE', displayName: 'German (Germany)' },
    { id: 2, localeCode: 'fr-FR', displayName: 'French (France)' }
  ]
};

const agreement = {
  tier: 'Gold',
  membersPerTeam: 6,
  validFrom: '2026-01-01T00:00:00Z',
  validTo: null,
  teams: [{ localeCode: 'de-DE', vendorTeamAlias: 'Vendor Team Larch', memberCount: 6 }]
};

function jobRow(overrides) {
  return {
    id: null,
    projectId: 1,
    localeCode: 'de-DE',
    status: 'NotCreated',
    stringCount: 136,
    wordCount: 540,
    completedPercent: 0,
    vendorTeamAlias: 'Vendor Team Larch',
    memberCount: 6,
    createdAt: null,
    submittedAt: null,
    approvedAt: null,
    ...overrides
  };
}

function renderJobs() {
  return render(
    <MemoryRouter initialEntries={['/lab-projects/localization/jobs?project=auroraline-hud-v3']}>
      <LocalizationJobs />
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  getProjects.mockResolvedValue([project]);
  getProject.mockResolvedValue(project);
  getProviderHealth.mockResolvedValue([]);
  getAgreement.mockResolvedValue(agreement);
});

describe('LocalizationJobs', () => {
  it('shows "Create job" when a team is assigned and "No team assigned" when it is not', async () => {
    getJobs.mockResolvedValue([
      jobRow({ localeCode: 'de-DE' }),
      jobRow({ localeCode: 'fr-FR', vendorTeamAlias: null, memberCount: null })
    ]);
    renderJobs();

    expect(await screen.findByRole('button', { name: 'Create job' })).toBeInTheDocument();
    expect(screen.getByText('No team assigned')).toBeInTheDocument();
  });

  it('shows both review buttons for a SubmittedForReview row', async () => {
    getJobs.mockResolvedValue([
      jobRow({ localeCode: 'de-DE', id: 12, status: 'SubmittedForReview', completedPercent: 100 })
    ]);
    renderJobs();

    expect(await screen.findByRole('button', { name: 'Approve' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send back' })).toBeInTheDocument();
  });

  it('shows the server detail inline on the row when create returns 409', async () => {
    getJobs.mockResolvedValue([jobRow({ localeCode: 'de-DE' })]);
    createJob.mockRejectedValue({
      message: 'A job for locale de-DE already exists.',
      status: 409,
      problemDetails: { Detail: 'A job for locale de-DE already exists.' }
    });
    renderJobs();

    fireEvent.click(await screen.findByRole('button', { name: 'Create job' }));

    expect(await screen.findByText('A job for locale de-DE already exists.')).toBeInTheDocument();
    expect(createJob).toHaveBeenCalledWith('auroraline-hud-v3', 'de-DE');
  });
});
