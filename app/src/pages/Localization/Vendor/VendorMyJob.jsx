import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Edit2, Check, X, RefreshCw, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import VendorPortalShell from './VendorPortalShell';
import useSelectedVendor from './useSelectedVendor';
import { api } from '../../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../../components/common/StateViews';

const READ_ONLY_STATUSES = ['SubmittedForReview', 'Approved', 'Closed'];

export default function VendorMyJob() {
  const { jobId } = useParams();
  const parsedJobId = parseInt(jobId, 10);
  const { vendor, loading: vendorLoading, error: vendorError } = useSelectedVendor();
  const vendorId = vendor?.id;

  const [assignedJob, setAssignedJob] = useState(null);
  const [strings, setStrings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Inline editing state
  const [editingStringId, setEditingStringId] = useState(null);
  const [editingText, setEditingText] = useState('');
  const [savingId, setSavingId] = useState(null);
  const [saveError, setSaveError] = useState(null);

  // Submission state
  const [submitting, setSubmitting] = useState(false);
  const [submitNotice, setSubmitNotice] = useState(null);

  const localeCode = assignedJob?.localeCode || '';
  const isReadOnly = assignedJob ? READ_ONLY_STATUSES.includes(assignedJob.status) : false;

  const fetchJobStrings = useCallback(async () => {
    if (!vendorId) return;
    setLoading(true);
    setError(null);
    try {
      const awarded = await api.vendorPortal.getAwardedJobs(vendorId);
      const found = (awarded || []).find((j) => j.id === parsedJobId);
      setAssignedJob(found || null);
      if (!found) {
        setStrings([]);
        return;
      }
      const data = await api.vendorPortal.getJobStrings(parsedJobId);
      if (Array.isArray(data)) {
        setStrings(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load job strings.');
    } finally {
      setLoading(false);
    }
  }, [vendorId, parsedJobId]);

  useEffect(() => {
    fetchJobStrings();
  }, [fetchJobStrings]);

  const startInlineEdit = (str) => {
    setEditingStringId(str.stringId);
    setEditingText(str.targetText || '');
    setSaveError(null);
  };

  const cancelInlineEdit = () => {
    setEditingStringId(null);
    setEditingText('');
  };

  const saveInlineEdit = async (stringId) => {
    setSavingId(stringId);
    setSaveError(null);
    try {
      const updated = await api.vendorPortal.updateJobString(parsedJobId, stringId, editingText);
      setStrings((prev) => prev.map((s) => (s.stringId === stringId ? updated : s)));
      setEditingStringId(null);
    } catch (err) {
      setSaveError(err.message || 'Failed to save translation.');
    } finally {
      setSavingId(null);
    }
  };

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

  const hasEmptyTargets = strings.some((s) => !s.targetText || s.targetText.trim() === '');

  const handleSubmitForReview = async () => {
    setSubmitting(true);
    setSubmitNotice(null);
    try {
      await api.vendorPortal.submitJob(parsedJobId);
      setSubmitNotice({
        type: 'success',
        message: 'Job submitted for review! The project owner will review your translations shortly.'
      });
      // Reload the job so its new status switches the page to read-only.
      await fetchJobStrings();
    } catch (err) {
      setSubmitNotice({
        type: 'error',
        message: err.message || 'Failed to submit job for review.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <VendorPortalShell>
      {/* Back Link */}
      <div style={{ marginBottom: '1.5rem' }}>
        <Link
          to="/lab-projects/localization/vendor"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.85rem',
            color: 'var(--color-sage, #2C5E55)',
            textDecoration: 'none',
            fontWeight: '600'
          }}
        >
          <ArrowLeft size={16} /> Back to Open Jobs
        </Link>
      </div>

      {/* 8.3 Heading */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h1
          style={{
            margin: '0 0 0.35rem 0',
            fontSize: '1.75rem',
            fontFamily: 'var(--font-serif, "Newsreader", serif)',
            color: 'var(--color-ink, #1F2937)'
          }}
        >
          My Jobs — Auroraline Automotive ({localeCode || '…'})
        </h1>
        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-ink-muted, #6B7280)' }}>
          Awarded job • {strings.length} strings • Deadline not set
        </p>
      </div>

      {submitNotice && (
        <div
          style={{
            padding: '0.85rem 1.25rem',
            borderRadius: '0px',
            fontSize: '0.9rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: submitNotice.type === 'success' ? '#ECFDF5' : '#FEF2F2',
            color: submitNotice.type === 'success' ? '#065F46' : '#991B1B',
            border: `1px solid ${submitNotice.type === 'success' ? '#A7F3D0' : '#FCA5A5'}`
          }}
        >
          {submitNotice.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{submitNotice.message}</span>
        </div>
      )}

      {saveError && (
        <div
          style={{
            padding: '0.85rem 1.25rem',
            borderRadius: '0px',
            fontSize: '0.9rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#FEF2F2',
            color: '#991B1B',
            border: '1px solid #FCA5A5'
          }}
        >
          <AlertCircle size={18} />
          <span>{saveError}</span>
        </div>
      )}

      {assignedJob?.status === 'NeedsRevision' && (
        <p style={{ fontSize: '0.9rem', color: 'var(--color-ink, #1F2937)', margin: '0 0 1.5rem 0' }}>
          The owner sent this job back for revision — please update the translations below and resubmit.
        </p>
      )}

      {/* Strings Table (NO STAGE COLUMN per §8.3) */}
      {vendorError ? (
        <ErrorState error={{ message: vendorError }} title="Unable to Load Vendor Roster" />
      ) : error ? (
        <ErrorState error={error} onRetry={fetchJobStrings} title="Unable to Load Workspace" />
      ) : (vendorLoading || !vendorId || loading) ? (
        <LoadingState message="Loading awarded translation string table..." />
      ) : !assignedJob ? (
        <EmptyState message={`Job ${parsedJobId} is not assigned to ${vendor?.name || 'the selected vendor'}.`} icon="🔒" />
      ) : strings.length === 0 ? (
        <EmptyState message="No strings assigned to this job." icon="📄" />
      ) : (
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid var(--color-border-subtle, #E2DDD5)',
            borderRadius: '0px',
            overflow: 'hidden',
            marginBottom: '2rem'
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
                  backgroundColor: 'rgba(0,0,0,0.02)',
                  fontSize: '0.75rem',
                  letterSpacing: '0.04em',
                  color: 'var(--color-ink-muted, #6B7280)',
                  textTransform: 'uppercase'
                }}
              >
                <th style={{ padding: '0.85rem 1.25rem', width: '50px' }}>#</th>
                <th style={{ padding: '0.85rem 1.25rem', width: '220px' }}>KEY</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>SOURCE (EN)</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>TARGET ({localeCode.split('-')[0].toUpperCase()})</th>
                <th style={{ padding: '0.85rem 1.25rem', width: '80px', textAlign: 'center' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {strings.map((str, idx) => {
                const isEditing = editingStringId === str.stringId;

                return (
                  <tr
                    key={str.stringId}
                    style={{
                      borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                      backgroundColor: isEditing ? 'rgba(44, 94, 85, 0.02)' : 'transparent'
                    }}
                  >
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink-muted, #6B7280)', fontSize: '0.85rem' }}>
                      {idx + 1}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--color-ink, #1F2937)' }}>
                      {str.key}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)' }}>
                      {str.sourceText}
                    </td>

                    {/* TARGET with inline editor */}
                    <td style={{ padding: '0.85rem 1.25rem' }}>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editingText}
                          onChange={(e) => setEditingText(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') saveInlineEdit(str.stringId);
                            if (e.key === 'Escape') cancelInlineEdit();
                          }}
                          autoFocus
                          style={{
                            width: '100%',
                            padding: '0.4rem 0.65rem',
                            border: '2px solid var(--color-sage, #2C5E55)',
                            borderRadius: '0px',
                            fontSize: '0.9rem',
                            color: 'var(--color-ink, #1F2937)',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                        />
                      ) : (
                        <span
                          style={{
                            color: str.targetText ? 'var(--color-ink, #1F2937)' : 'var(--color-ink-muted, #6B7280)',
                            fontStyle: str.targetText ? 'normal' : 'italic'
                          }}
                        >
                          {str.targetText || 'Not translated'}
                        </span>
                      )}
                    </td>

                    {/* Action Column: Inline edit buttons */}
                    <td style={{ padding: '0.85rem 1.25rem', textAlign: 'center' }}>
                      {isReadOnly ? (
                        <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>—</span>
                      ) : isEditing ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
                          <button
                            type="button"
                            disabled={savingId === str.stringId}
                            onClick={() => saveInlineEdit(str.stringId)}
                            title="Save"
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              color: 'var(--color-sage, #2C5E55)',
                              padding: '2px'
                            }}
                          >
                            {savingId === str.stringId ? <RefreshCw size={14} className="spin" /> : <Check size={16} />}
                          </button>
                          <button
                            type="button"
                            onClick={cancelInlineEdit}
                            title="Cancel"
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              color: 'var(--color-ink-muted, #6B7280)',
                              padding: '2px'
                            }}
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => startInlineEdit(str)}
                          title="Edit Translation"
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'var(--color-ink-muted, #6B7280)',
                            padding: '4px'
                          }}
                        >
                          <Edit2 size={14} />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Bottom Action: Solid Sage Rectangular Text-Label "Submit for Review" Button */}
      {assignedJob && (
        <div style={{ display: 'flex', justifyContent: isReadOnly ? 'flex-start' : 'flex-end', alignItems: 'center', gap: '1rem' }}>
          {isReadOnly ? (
            <span style={{ fontSize: '0.9rem', color: 'var(--color-ink, #1F2937)' }}>
              Job status: {getStatusLabel(assignedJob.status)}.
            </span>
          ) : (
            <>
              {hasEmptyTargets && (
                <span style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)', fontStyle: 'italic' }}>
                  All strings must have non-empty translations before submitting.
                </span>
              )}

              <button
                type="button"
                disabled={hasEmptyTargets || submitting}
                onClick={handleSubmitForReview}
                style={{
                  padding: '0.75rem 1.75rem',
                  borderRadius: '0px', // sharp corners
                  border: 'none',
                  backgroundColor: hasEmptyTargets ? 'rgba(44, 94, 85, 0.4)' : 'var(--color-sage, #2C5E55)',
                  color: '#FFFFFF',
                  fontSize: '0.9rem',
                  fontWeight: '700',
                  letterSpacing: '0.02em',
                  cursor: hasEmptyTargets ? 'not-allowed' : submitting ? 'wait' : 'pointer',
                  pointerEvents: hasEmptyTargets ? 'none' : 'auto',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'background-color 0.15s ease'
                }}
              >
                {submitting ? <RefreshCw size={16} className="spin" /> : <Send size={16} />}
                <span>Submit for Review</span>
              </button>
            </>
          )}
        </div>
      )}
    </VendorPortalShell>
  );
}
