import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Clock, CheckCircle, ArrowRight } from 'lucide-react';
import VendorPortalShell from './VendorPortalShell';
import BidSubmissionModal from './BidSubmissionModal';
import useSelectedVendor from './useSelectedVendor';
import { api } from '../../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../../components/common/StateViews';

const SUBMITTED_BIDS_KEY = 'localization-submitted-bids';

function readSubmittedBids() {
  try {
    const raw = sessionStorage.getItem(SUBMITTED_BIDS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return new Set(Array.isArray(parsed) ? parsed : []);
  } catch {
    return new Set();
  }
}

export default function VendorOpenJobs() {
  const navigate = useNavigate();
  const { vendor, loading: vendorLoading, error: vendorError } = useSelectedVendor();
  const vendorId = vendor?.id;
  const [openJobs, setOpenJobs] = useState([]);
  const [awardedJobs, setAwardedJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Bid modal state
  const [activeJobForBid, setActiveJobForBid] = useState(null);

  // Jobs bid on this session, so the user cannot re-bid by accident
  const [submittedBidJobIds, setSubmittedBidJobIds] = useState(readSubmittedBids);

  const markBidSubmitted = (jobId) => {
    setSubmittedBidJobIds((prev) => {
      const next = new Set(prev);
      next.add(jobId);
      try {
        sessionStorage.setItem(SUBMITTED_BIDS_KEY, JSON.stringify([...next]));
      } catch {
        // sessionStorage unavailable; in-memory set still guards this page
      }
      return next;
    });
  };

  const handleBidSuccess = (jobId) => {
    markBidSubmitted(jobId);
    fetchJobs();
  };

  const fetchJobs = useCallback(async () => {
    if (!vendorId) return;
    setLoading(true);
    setError(null);
    try {
      const [open, awarded] = await Promise.all([
        api.vendorPortal.getOpenJobs(vendorId),
        api.vendorPortal.getAwardedJobs(vendorId)
      ]);

      setOpenJobs(open || []);
      setAwardedJobs(awarded || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch vendor jobs.');
    } finally {
      setLoading(false);
    }
  }, [vendorId]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const computeDaysOpen = (postedAt) => {
    if (!postedAt) return 1;
    const diffMs = Date.now() - new Date(postedAt).getTime();
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    return days > 0 ? days : 1;
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
        return status; // 'Not Posted', 'Open', 'Awarded', 'Approved', 'Closed', 'Draft' are already correctly spaced
    }
  };

  return (
    <VendorPortalShell>
      {/* 8.1 Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1
          style={{
            margin: '0 0 0.35rem 0',
            fontSize: '1.85rem',
            fontFamily: 'var(--font-serif, "Newsreader", serif)',
            color: 'var(--color-ink, #1F2937)'
          }}
        >
          Open Jobs
        </h1>
        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-ink-muted, #6B7280)' }}>
          Showing jobs matching language pairs for: <strong>{vendor?.name || 'Selected Vendor'}</strong> ({vendor?.languages || '...'})
        </p>
      </div>

      {vendorError ? (
        <ErrorState error={{ message: vendorError }} title="Unable to Load Vendor Roster" />
      ) : error ? (
        <ErrorState error={error} onRetry={fetchJobs} title="Unable to Load Jobs" />
      ) : (vendorLoading || !vendorId || loading) ? (
        <LoadingState message="Checking open opportunities..." />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
          {/* Active / Awarded Jobs Section */}
          {awardedJobs.length > 0 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                <CheckCircle size={18} color="var(--color-sage, #2C5E55)" />
                <h2 style={{ margin: 0, fontSize: '1.2rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
                  My Awarded Jobs
                </h2>
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
                  gap: '1.25rem'
                }}
              >
                {awardedJobs.map((job) => (
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
                        Auroraline Automotive HUD
                      </h3>
                      <div style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                        {job.stringCount} strings • {job.wordCount} words
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

          {/* Open Bidding Jobs Grid */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
              <Briefcase size={18} color="var(--color-ink, #1F2937)" />
              <h2 style={{ margin: 0, fontSize: '1.2rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
                Available Opportunities ({openJobs.length})
              </h2>
            </div>

            {openJobs.length === 0 ? (
              <EmptyState
                message={`No open jobs currently match the languages for ${vendor?.name || 'this vendor'}.`}
                icon="🔍"
              />
            ) : (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
                  gap: '1.25rem'
                }}
              >
                {openJobs.map((job) => {
                  const daysOpen = computeDaysOpen(job.postedAt);
                  const bidSubmitted = submittedBidJobIds.has(job.id);

                  return (
                    <div
                      key={job.id}
                      style={{
                        border: '1px solid var(--color-border-subtle, #E2DDD5)',
                        borderRadius: '0px', // sharp corners per spec
                        boxShadow: 'none', // no shadow per spec
                        backgroundColor: '#FFFFFF',
                        padding: '1.5rem',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        gap: '1.25rem'
                      }}
                    >
                      <div>
                        {/* Project + Locale Name */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                          <div>
                            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-ink-muted, #6B7280)', fontWeight: '700' }}>
                              Auroraline Automotive HUD
                            </span>
                            <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.15rem', color: 'var(--color-ink, #1F2937)' }}>
                              Target: {job.localeCode}
                            </h3>
                          </div>
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              fontSize: '0.75rem',
                              color: 'var(--color-ink-muted, #6B7280)'
                            }}
                          >
                            <Clock size={12} /> Open {daysOpen} {daysOpen === 1 ? 'day' : 'days'}
                          </span>
                        </div>

                        {/* String & Word Count */}
                        <div style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)', marginBottom: '0.75rem' }}>
                          {job.stringCount} strings • {job.wordCount} words
                        </div>

                        {/* Suggested Band (Bold Sage) */}
                        <div style={{ fontSize: '0.85rem' }}>
                          <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>Suggested Budget: </span>
                          <span style={{ fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
                            {job.suggestedPriceLow} – {job.suggestedPriceHigh} Credits
                          </span>
                        </div>
                      </div>

                      {bidSubmitted && (
                        <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
                          Bid submitted
                        </div>
                      )}

                      {/* Rectangular Sage-Bordered Text-Label Button: Submit a Bid */}
                      <button
                        type="button"
                        disabled={bidSubmitted}
                        onClick={() => setActiveJobForBid(job)}
                        style={{
                          width: '100%',
                          padding: '0.65rem 1rem',
                          borderRadius: '0px', // sharp corners
                          backgroundColor: '#FFFFFF',
                          border: bidSubmitted ? '1px solid var(--color-border-subtle, #E2DDD5)' : '1px solid var(--color-sage, #2C5E55)',
                          color: bidSubmitted ? 'var(--color-ink-muted, #6B7280)' : 'var(--color-sage, #2C5E55)',
                          fontSize: '0.85rem',
                          fontWeight: '700',
                          cursor: bidSubmitted ? 'not-allowed' : 'pointer',
                          textAlign: 'center',
                          transition: 'all 0.15s ease'
                        }}
                        onMouseEnter={(e) => {
                          if (bidSubmitted) return;
                          e.currentTarget.style.backgroundColor = 'var(--color-sage, #2C5E55)';
                          e.currentTarget.style.color = '#FFFFFF';
                        }}
                        onMouseLeave={(e) => {
                          if (bidSubmitted) return;
                          e.currentTarget.style.backgroundColor = '#FFFFFF';
                          e.currentTarget.style.color = 'var(--color-sage, #2C5E55)';
                        }}
                      >
                        Submit a Bid
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 8.2 Bid Submission Modal */}
      <BidSubmissionModal
        isOpen={!!activeJobForBid}
        onClose={() => setActiveJobForBid(null)}
        job={activeJobForBid}
        vendorId={vendorId}
        onSuccess={handleBidSuccess}
      />
    </VendorPortalShell>
  );
}
