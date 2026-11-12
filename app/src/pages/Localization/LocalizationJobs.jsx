import React, { useState, useEffect, useCallback } from 'react';
import LocalizationShell from './LocalizationShell';
import useLocalizationProject from './useLocalizationProject';
import { api } from '../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';

function formatDate(value) {
  if (!value) return null;
  const time = new Date(value).getTime();
  if (Number.isNaN(time)) return value;
  return new Date(value).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

export default function LocalizationJobs() {
  const { slug: projectSlug, loading: projectLoading, error: projectError } = useLocalizationProject();
  const [jobs, setJobs] = useState([]);
  const [agreement, setAgreement] = useState(null);
  const [hasAgreement, setHasAgreement] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rowErrors, setRowErrors] = useState({});
  const [actingLocale, setActingLocale] = useState(null);

  const fetchJobs = useCallback(async () => {
    if (!projectSlug) return;
    setLoading(true);
    setError(null);
    setRowErrors({});
    try {
      const agreementPromise = api.localization.getAgreement(projectSlug).then(
        (data) => ({ found: true, data }),
        (err) => {
          if (err && err.status === 404) return { found: false, data: null };
          throw err;
        }
      );
      const [jobsData, agreementResult] = await Promise.all([
        api.localization.getJobs(projectSlug),
        agreementPromise
      ]);
      if (Array.isArray(jobsData)) {
        setJobs(jobsData);
      }
      setHasAgreement(agreementResult.found);
      setAgreement(agreementResult.data);
    } catch (err) {
      setError(err.message || 'Failed to load translation jobs.');
    } finally {
      setLoading(false);
    }
  }, [projectSlug]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const runRowAction = async (row, action) => {
    setActingLocale(row.localeCode);
    setRowErrors((prev) => ({ ...prev, [row.localeCode]: null }));
    try {
      let updated;
      if (action === 'create') {
        updated = await api.localization.createJob(projectSlug, row.localeCode);
      } else if (action === 'approve') {
        updated = await api.localization.approveJob(row.id);
      } else {
        updated = await api.localization.sendBackJob(row.id);
      }
      if (updated && updated.localeCode) {
        setJobs((prev) => prev.map((j) => (j.localeCode === updated.localeCode ? updated : j)));
      } else {
        await fetchJobs();
      }
    } catch (err) {
      const detail = err.status === 409
        ? (err.problemDetails?.detail || err.message)
        : (err.message || 'Action failed.');
      setRowErrors((prev) => ({ ...prev, [row.localeCode]: detail }));
    } finally {
      setActingLocale(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved':
        return 'var(--color-sage, #2C5E55)';
      case 'NotCreated':
        return 'var(--color-ink-muted, #6B7280)';
      case 'NeedsRevision':
        return '#A6772C';
      default:
        return 'var(--color-ink, #1F2937)';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'NotCreated':
        return 'Not created';
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

  const renderAction = (row) => {
    const busy = actingLocale === row.localeCode;
    if (row.status === 'NotCreated') {
      if (!row.vendorTeamAlias) {
        return (
          <span style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)', fontStyle: 'italic' }}>
            No team assigned
          </span>
        );
      }
      return (
        <button
          type="button"
          disabled={busy}
          onClick={() => runRowAction(row, 'create')}
          style={{
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: 'var(--color-sage, #2C5E55)',
            color: '#FFFFFF',
            fontSize: '0.8rem',
            fontWeight: '700',
            cursor: busy ? 'wait' : 'pointer'
          }}
        >
          Create job
        </button>
      );
    }
    if (row.status === 'SubmittedForReview') {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            type="button"
            disabled={busy}
            onClick={() => runRowAction(row, 'approve')}
            style={{
              padding: '0.4rem 0.8rem',
              borderRadius: '4px',
              border: 'none',
              backgroundColor: 'var(--color-sage, #2C5E55)',
              color: '#FFFFFF',
              fontSize: '0.8rem',
              fontWeight: '700',
              cursor: busy ? 'wait' : 'pointer'
            }}
          >
            Approve
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => runRowAction(row, 'send-back')}
            style={{
              padding: '0.4rem 0.8rem',
              borderRadius: '4px',
              backgroundColor: '#FFFFFF',
              color: '#991B1B',
              border: '1px solid #F87171',
              fontSize: '0.8rem',
              fontWeight: '700',
              cursor: busy ? 'wait' : 'pointer'
            }}
          >
            Send back
          </button>
        </div>
      );
    }
    return <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>—</span>;
  };

  const validFrom = agreement ? formatDate(agreement.validFrom) : null;
  const validTo = agreement ? formatDate(agreement.validTo) : null;

  return (
    <LocalizationShell activeTab="jobs">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.25rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
          Translation Jobs
        </h2>
        <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
          One job per locale, handled by the vendor team named in the project service agreement.
        </p>
        {agreement && (
          <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: 'var(--color-ink, #1F2937)', fontWeight: '600' }}>
            {agreement.tier} • {agreement.membersPerTeam} members per team • Valid {validFrom || '—'} – {validTo || 'ongoing'}
          </p>
        )}
      </div>

      {projectError ? (
        <ErrorState error={{ message: projectError }} title="Unable to Load Project" />
      ) : error ? (
        <ErrorState error={error} onRetry={fetchJobs} title="Unable to Load Jobs" />
      ) : (projectLoading || !projectSlug || loading) ? (
        <LoadingState message="Fetching translation jobs across target locales..." />
      ) : !hasAgreement ? (
        <EmptyState message="This project has no service agreement yet. Operations assigns one." icon="📋" />
      ) : jobs.length === 0 ? (
        <EmptyState message="No locales found for this project." icon="🌐" />
      ) : (
        <div
          style={{
            backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
            border: '1px solid var(--color-border-subtle, #E2DDD5)',
            overflow: 'hidden'
          }}
        >
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              textAlign: 'left',
              fontSize: '0.9rem'
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                  fontSize: '0.75rem',
                  letterSpacing: '0.04em',
                  color: 'var(--color-ink-muted, #6B7280)',
                  textTransform: 'uppercase'
                }}
              >
                <th style={{ padding: '0.85rem 1.25rem' }}>LOCALE</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>VENDOR TEAM</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>TEAM SIZE</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>STRINGS</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>WORDS</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>PROGRESS</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>STATUS</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((row) => {
                const rowError = rowErrors[row.localeCode];
                return (
                  <tr
                    key={row.localeCode}
                    style={{ borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)' }}
                  >
                    <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'monospace', fontWeight: '700', color: 'var(--color-ink, #1F2937)' }}>
                      {row.localeCode}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)' }}>
                      {row.vendorTeamAlias || '—'}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)' }}>
                      {row.memberCount ?? '—'}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)' }}>
                      {row.stringCount}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)' }}>
                      {row.wordCount}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '90px', height: '8px', backgroundColor: '#F3F4F6', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${row.completedPercent || 0}%`, height: '100%', backgroundColor: 'var(--color-sage, #2C5E55)' }} />
                        </div>
                        <span style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                          {row.completedPercent || 0}%
                        </span>
                      </div>
                    </td>
                    <td
                      style={{
                        padding: '0.85rem 1.25rem',
                        color: getStatusColor(row.status),
                        fontWeight: row.status === 'Approved' ? '700' : '500'
                      }}
                    >
                      {getStatusLabel(row.status)}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem' }}>
                      {renderAction(row)}
                      {rowError && (
                        <div style={{ marginTop: '0.4rem', fontSize: '0.8rem', color: '#991B1B' }}>
                          {rowError}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </LocalizationShell>
  );
}
