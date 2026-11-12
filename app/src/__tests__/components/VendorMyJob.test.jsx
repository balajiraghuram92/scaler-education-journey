import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import VendorMyJob from '../../pages/Localization/Vendor/VendorMyJob';

const { getRoster, getJobs, getJobStrings, updateJobString, submitJob } = vi.hoisted(() => ({
  getRoster: vi.fn(),
  getJobs: vi.fn(),
  getJobStrings: vi.fn(),
  updateJobString: vi.fn(),
  submitJob: vi.fn()
}));

vi.mock('../../api/client', () => ({
  api: { vendorPortal: { getRoster, getJobs, getJobStrings, updateJobString, submitJob } }
}));

const vendorJob = {
  id: 12,
  clientAlias: 'Client Team Kestrel',
  localeCode: 'de-DE',
  status: 'InProgress',
  stringCount: 5,
  wordCount: 20,
  completedPercent: 40,
  createdAt: '2026-11-01T00:00:00Z',
  submittedAt: null,
  approvedAt: null
};

function stringRow(overrides) {
  return {
    stringId: 1,
    key: 'hud.speed',
    sourceText: 'Speed',
    localeCode: 'de-DE',
    targetText: 'Tempo',
    stage: 'Translated',
    translationSource: 'AI',
    updatedAt: '2026-11-02T00:00:00Z',
    score: null,
    needsReview: false,
    rawMtText: 'raw draft',
    rawMtScore: null,
    ...overrides
  };
}

const strings = [
  stringRow({ stringId: 1, key: 'key.null', score: null, rawMtScore: null }),
  stringRow({ stringId: 2, key: 'key.low', score: 2, rawMtScore: 1 }),
  stringRow({ stringId: 3, key: 'key.mid', score: 3, rawMtScore: 3 }),
  stringRow({ stringId: 4, key: 'key.good', score: 4, rawMtScore: 4 }),
  stringRow({ stringId: 5, key: 'key.best', score: 5, rawMtScore: 5 })
];

function renderJob() {
  return render(
    <MemoryRouter initialEntries={['/lab-projects/localization/vendor/jobs/12']}>
      <Routes>
        <Route path="/lab-projects/localization/vendor/jobs/:jobId" element={<VendorMyJob />} />
      </Routes>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  getRoster.mockResolvedValue([{ id: 1, alias: 'Vendor Team Larch', languages: 'de-DE' }]);
  getJobs.mockResolvedValue([vendorJob]);
  getJobStrings.mockResolvedValue(strings);
});

describe('VendorMyJob score groups', () => {
  it('groups rows by score with the right counts', async () => {
    renderJob();
    const table = await screen.findByRole('table');

    expect(within(table).getByText('Not scored (1)')).toBeInTheDocument();
    expect(within(table).getByText(/1[–-]2 \(1\)/)).toBeInTheDocument();
    expect(within(table).getByText('3 (1)')).toBeInTheDocument();
    expect(within(table).getByText('4 (1)')).toBeInTheDocument();
    expect(within(table).getByText('5 (1)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'All (5)' })).toBeInTheDocument();
  });

  it('places a row with a null score in "not scored"', async () => {
    renderJob();
    const table = await screen.findByRole('table');
    const rowTexts = within(table).getAllByRole('row').map((row) => row.textContent);

    const headerIdx = rowTexts.findIndex((t) => t.includes('Not scored'));
    const rowIdx = rowTexts.findIndex((t) => t.includes('key.null'));
    const nextIdx = rowTexts.findIndex((t) => /1[–-]2/.test(t));

    expect(headerIdx).toBeGreaterThanOrEqual(0);
    expect(rowIdx).toBeGreaterThan(headerIdx);
    expect(rowIdx).toBeLessThan(nextIdx);
  });

  it('filters to one group when a score chip is clicked', async () => {
    renderJob();
    await screen.findByRole('table');

    fireEvent.click(screen.getByRole('button', { name: /Not scored \(1\)/ }));

    const table = screen.getByRole('table');
    expect(within(table).queryByText(/1[–-]2 \(1\)/)).toBeNull();
    expect(within(table).getByText('key.null')).toBeInTheDocument();
    expect(within(table).queryByText('key.low')).toBeNull();
  });

  it('shows the client alias in the header', async () => {
    renderJob();

    expect(await screen.findByText(/Client Team Kestrel/)).toBeInTheDocument();
  });
});
