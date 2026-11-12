import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, ArrowRight } from 'lucide-react';
import VendorPortalShell from './VendorPortalShell';
import useSelectedVendor from './useSelectedVendor';
import { api } from '../../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../../components/common/StateViews';

export default function VendorJobs() {
  const navigate = useNavigate();
  const { vendor, loading: vendorLoading, error: vendorError } = useSelectedVendor();
  const vendorId = vendor?.id;
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJobs = useCallback(async () => {
    if (!vendorId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.vendorPortal.getJobs(vendorId);
      setJobs(data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch vendor jobs.');
    } finally {
      setLoading(false);
    }
  }, [vendorId]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const getStatusLabel = (status) => {
    switch (status) {
      case 'SubmittedForReview':
        return 'Submitted for Review';
      case 'InProgress':
        return 'In Progress';
      case 'NeedsRevision':
        return 'Needs Revision';
      default:
        return status;
    }
  };

  return (
    <VendorPortalShell>
      <div style={{ marginBottom: '2rem' }}>
        <h1
          style={{
            margin: '0 0 0.35rem 0',
            fontSize: '1.85rem',
            fontFamily: 'var(--font-serif, "Newsreader", serif)',
            color: 'var(--color-ink, #1F2937)'
          }}
        >
          My Jobs
        </h1>
        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-ink-muted, #6B7280)' }}>
          Showing jobs assigned to: <strong>{vendor?.alias || 'Selected Team'}</strong> ({vendor?.languages || '...'})
        </p>
      </div>

      {vendorError ? (
        <ErrorState error={{ message: vendorError }} title="Unable to Load Vendor Roster" />
      ) : error ? (
        <ErrorState error={error} onRetry={fetchJobs} title="Unable to Load Jobs" />
      ) : (vendorLoading || !vendorId || loading) ? (
        <LoadingState message="Checking assigned jobs..." />
      ) : jobs.length === 0 ? (
        <EmptyState
          message={`No jobs are currently assigned to ${vendor?.alias || 'this team'}.`}
          icon="💼"
        />
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
            <Briefcase size={18} color="var(--color-ink, #1F2937)" />
            <h2 style={{ margin: 0, fontSize: '1.2rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
              Assigned Jobs ({jobs.length})
            </h2>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
              gap: '1.25rem'
            }}
          >
            {jobs.map((job) => (
              <div
                key={job.id}
                style={{
                  border: '1px solid var(--color-sage, #2C5E55)',
                  borderRadius: '0px',
                  backgroundColor: '#FFFFFF',
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '1rem'
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-sage, #2C5E55)' }}>
                      Status: {getStatusLabel(job.status)}
                    </span>
                    <span style={{ fontSize: '0.85rem', fontFamily: 'monospace', fontWeight: '700', color: 'var(--color-ink, #1F2937)' }}>
                      {job.localeCode}
                    </span>
                  </div>
                  <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.1rem', color: 'var(--color-ink, #1F2937)' }}>
                    {job.clientAlias}
                  </h3>
                  <div style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)', marginBottom: '0.75rem' }}>
                    {job.stringCount} strings • {job.wordCount} words
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ flex: 1, height: '8px', backgroundColor: '#F3F4F6', borderRadius: '0px', overflow: 'hidden' }}>
                      <div style={{ width: `${job.completedPercent || 0}%`, height: '100%', backgroundColor: 'var(--color-sage, #2C5E55)' }} />
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                      {job.completedPercent || 0}%
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => navigate(`/lab-projects/localization/vendor/jobs/${job.id}`)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    padding: '0.6rem 1rem',
                    borderRadius: '0px',
                    backgroundColor: 'var(--color-sage, #2C5E55)',
                    color: '#FFFFFF',
                    border: 'none',
                    fontSize: '0.85rem',
                    fontWeight: '700',
                    cursor: 'pointer'
                  }}
                >
                  <span>Open Workspace</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </VendorPortalShell>
  );
}
