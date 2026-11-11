import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Check, RefreshCw, CheckCircle2 } from 'lucide-react';
import { api } from '../../api/client';
import useLocalizationProject from './useLocalizationProject';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';

export default function LocalizationBidReview() {
  const { jobId } = useParams();
  const parsedJobId = parseInt(jobId, 10);
  const { slug: projectSlug, project, loading: projectLoading, error: projectError } = useLocalizationProject();

  const [bids, setBids] = useState([]);
  const [jobOverview, setJobOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [awardingBidId, setAwardingBidId] = useState(null);
  const [awardedMessage, setAwardedMessage] = useState(null);

  const fetchJobAndBids = useCallback(async () => {
    if (!projectSlug) return;
    setLoading(true);
    setError(null);
    try {
      const bidsData = await api.localization.getBids(parsedJobId);
      setBids(bidsData || []);

      // Get job details from overview
      const overview = await api.localization.getMarketplaceOverview(projectSlug);
      if (Array.isArray(overview)) {
        const found = overview.find((j) => j.id === parsedJobId);
        setJobOverview(found || null);
      }
    } catch (err) {
      setError(err.message || 'Failed to load bids for this job.');
    } finally {
      setLoading(false);
    }
  }, [parsedJobId, projectSlug]);

  useEffect(() => {
    fetchJobAndBids();
  }, [fetchJobAndBids]);

  const handleAwardBid = async (bidId, vendorName) => {
    setAwardingBidId(bidId);
    setAwardedMessage(null);
    try {
      await api.localization.awardBid(parsedJobId, bidId);
      setAwardedMessage(`Job successfully awarded to ${vendorName}!`);
      await fetchJobAndBids();
    } catch (err) {
      alert(`Failed to award bid: ${err.message}`);
    } finally {
      setAwardingBidId(null);
    }
  };

  const getPriceColor = (price, low, high) => {
    if (!low || !high) return 'var(--color-ink, #1F2937)';
    if (price < low) return 'var(--color-sage, #2C5E55)';
    if (price > high) return '#A6772C';
    return 'var(--color-ink, #1F2937)';
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: 'var(--color-parchment, #F8F6F0)',
        padding: '2rem',
        boxSizing: 'border-box'
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Back Link */}
        <div style={{ marginBottom: '1.5rem' }}>
          <Link
            to={projectSlug ? `/lab-projects/localization/marketplace?project=${encodeURIComponent(projectSlug)}` : '/lab-projects/localization/marketplace'}
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
            <ArrowLeft size={16} /> Back to Marketplace
          </Link>
        </div>

        {projectError ? (
          <ErrorState error={{ message: projectError }} title="Unable to Load Project" />
        ) : error ? (
          <ErrorState error={error} onRetry={fetchJobAndBids} title="Unable to Load Bids" />
        ) : (projectLoading || !projectSlug || loading) ? (
          <LoadingState message="Fetching submitted bids..." />
        ) : !jobOverview ? (
          <ErrorState error={{ message: `Marketplace job ${parsedJobId} was not found.` }} onRetry={fetchJobAndBids} title="Job Not Found" />
        ) : (
          <>
            {/* Header */}
            <div style={{ marginBottom: '1.75rem' }}>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-sage, #2C5E55)', fontWeight: '700' }}>
                Bid Evaluation
              </span>
              <h1
                style={{
                  margin: '0.25rem 0 0 0',
                  fontSize: '1.75rem',
                  fontFamily: 'var(--font-serif, "Newsreader", serif)',
                  color: 'var(--color-ink, #1F2937)'
                }}
              >
                Bids for {jobOverview.localeCode}
              </h1>
              <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.9rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                Project: {project ? project.name : '…'} • {jobOverview.stringCount} strings ({jobOverview.wordCount} words) • Suggested Band: {jobOverview.suggestedPriceLow} – {jobOverview.suggestedPriceHigh} Credits
              </p>
            </div>

            {awardedMessage && (
              <div
                style={{
                  padding: '0.85rem 1.25rem',
                  backgroundColor: '#ECFDF5',
                  border: '1px solid #A7F3D0',
                  borderRadius: '6px',
                  color: '#065F46',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  marginBottom: '1.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <CheckCircle2 size={18} />
                <span>{awardedMessage}</span>
              </div>
            )}

            {/* Bids Table */}
            {bids.length === 0 ? (
              <EmptyState message="No bids submitted yet for this job." icon="📝" />
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
                  <th style={{ padding: '0.85rem 1.25rem' }}>VENDOR</th>
                  <th style={{ padding: '0.85rem 1.25rem' }}>LANGUAGES</th>
                  <th style={{ padding: '0.85rem 1.25rem' }}>PROPOSED PRICE</th>
                  <th style={{ padding: '0.85rem 1.25rem' }}>NOTE</th>
                  <th style={{ padding: '0.85rem 1.25rem', width: '80px', textAlign: 'center' }}>AWARD</th>
                </tr>
              </thead>
              <tbody>
                {bids.map((bid) => {
                  const priceColor = getPriceColor(
                    bid.proposedPrice,
                    jobOverview?.suggestedPriceLow,
                    jobOverview?.suggestedPriceHigh
                  );
                  const isAwarded = bid.status === 'Awarded';

                  return (
                    <tr
                      key={bid.id}
                      style={{
                        borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                        backgroundColor: isAwarded ? 'rgba(44, 94, 85, 0.04)' : 'transparent',
                        transition: 'background-color 0.15s ease'
                      }}
                    >
                      {/* VENDOR: Name + ★Rating in single text string */}
                      <td style={{ padding: '0.85rem 1.25rem', fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>
                        {bid.vendorName} ★{bid.vendorRating}
                      </td>

                      <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink-muted, #6B7280)', fontSize: '0.85rem' }}>
                        {bid.vendorLanguages}
                      </td>

                      {/* PROPOSED PRICE */}
                      <td style={{ padding: '0.85rem 1.25rem', fontWeight: '700', color: priceColor }}>
                        {bid.proposedPrice} Credits
                      </td>

                      <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)', fontSize: '0.85rem' }}>
                        {bid.note || '—'}
                      </td>

                      {/* Action: Solid Sage Filled Circle with White Checkmark */}
                      <td style={{ padding: '0.85rem 1.25rem', textAlign: 'center' }}>
                        {isAwarded ? (
                          <span
                            style={{
                              fontSize: '0.75rem',
                              fontWeight: '700',
                              color: 'var(--color-sage, #2C5E55)',
                              textTransform: 'uppercase'
                            }}
                          >
                            Awarded
                          </span>
                        ) : jobOverview.status === 'Open' ? (
                          <button
                            type="button"
                            disabled={awardingBidId === bid.id}
                            onClick={() => handleAwardBid(bid.id, bid.vendorName)}
                            title={`Award Job to ${bid.vendorName}`}
                            style={{
                              width: '32px',
                              height: '32px',
                              borderRadius: '50%',
                              backgroundColor: 'var(--color-sage, #2C5E55)',
                              color: '#FFFFFF',
                              border: 'none',
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              cursor: awardingBidId === bid.id ? 'wait' : 'pointer'
                            }}
                          >
                            {awardingBidId === bid.id ? (
                              <RefreshCw size={13} className="spin" />
                            ) : (
                              <Check size={14} />
                            )}
                          </button>
                        ) : (
                          <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
