import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Megaphone, Users, Search, X, Check, ArrowRight, RefreshCw } from 'lucide-react';
import LocalizationShell from './LocalizationShell';
import { api } from '../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';

export default function LocalizationMarketplace() {
  const navigate = useNavigate();
  const [projectSlug] = useState('auroraline-hud-v3');
  const [overview, setOverview] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Post to Marketplace confirmation drawer state
  const [confirmLocaleRow, setConfirmLocaleRow] = useState(null);
  const [isPosting, setIsPosting] = useState(false);

  const fetchOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.localization.getMarketplaceOverview(projectSlug);
      if (Array.isArray(data)) {
        setOverview(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load marketplace overview.');
    } finally {
      setLoading(false);
    }
  }, [projectSlug]);

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  const handleConfirmPost = async () => {
    if (!confirmLocaleRow) return;
    setIsPosting(true);
    try {
      await api.localization.postToMarketplace(projectSlug, confirmLocaleRow.localeCode);
      setConfirmLocaleRow(null);
      await fetchOverview();
    } catch (err) {
      alert(`Error posting to marketplace: ${err.message}`);
    } finally {
      setIsPosting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Open':
      case 'Approved':
        return 'var(--color-sage, #2C5E55)';
      case 'Not Posted':
        return 'var(--color-ink-muted, #6B7280)';
      case 'SubmittedForReview':
        return '#B45309'; // Amber
      case 'Awarded':
      case 'InProgress':
        return 'var(--color-ink, #1F2937)';
      default:
        return 'var(--color-ink, #1F2937)';
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
        return status; // 'Not Posted', 'Open', 'Awarded', 'Approved', 'Closed', 'Draft' are already correctly spaced
    }
  };

  return (
    <LocalizationShell activeTab="marketplace">
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
            Vendor Marketplace & Bidding Overview
          </h2>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
            Post untranslated strings to vetted human translation specialists with automated budget bands.
          </p>
        </div>
      </div>

      {error ? (
        <ErrorState error={error} onRetry={fetchOverview} title="Unable to Load Marketplace" />
      ) : loading ? (
        <LoadingState message="Fetching marketplace statuses across target locales..." />
      ) : overview.length === 0 ? (
        <EmptyState message="No locales found for this project." icon="🏪" />
      ) : (
        <div
          style={{
            backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
            border: '1px solid var(--color-border-subtle, #E2DDD5)',
            borderRadius: '8px',
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
                  backgroundColor: 'rgba(0,0,0,0.02)',
                  fontSize: '0.75rem',
                  letterSpacing: '0.04em',
                  color: 'var(--color-ink-muted, #6B7280)',
                  textTransform: 'uppercase'
                }}
              >
                <th style={{ padding: '0.85rem 1.25rem' }}>LOCALE</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>STRINGS REMAINING</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>STATUS</th>
                <th style={{ padding: '0.85rem 1.25rem' }}>SUGGESTED BAND</th>
                <th style={{ padding: '0.85rem 1.25rem', width: '70px', textAlign: 'center' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {overview.map((row) => {
                const statusColor = getStatusColor(row.status);
                const isBold = row.status === 'Open' || row.status === 'Approved';

                return (
                  <tr
                    key={row.localeCode}
                    style={{
                      borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                      transition: 'background-color 0.15s ease'
                    }}
                  >
                    <td style={{ padding: '0.85rem 1.25rem', fontFamily: 'monospace', fontWeight: '700', color: 'var(--color-ink, #1F2937)' }}>
                      {row.localeCode}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', color: 'var(--color-ink, #1F2937)' }}>
                      {row.stringCount} strings ({row.wordCount} words)
                    </td>
                    <td
                      style={{
                        padding: '0.85rem 1.25rem',
                        color: statusColor,
                        fontWeight: isBold ? '700' : '500'
                      }}
                    >
                      {getStatusLabel(row.status)}
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>
                      {row.suggestedPriceLow} – {row.suggestedPriceHigh} Credits
                    </td>
                    <td style={{ padding: '0.85rem 1.25rem', textAlign: 'center' }}>
                      {row.status === 'Not Posted' && (
                        <button
                          type="button"
                          onClick={() => setConfirmLocaleRow(row)}
                          title="Post to Marketplace"
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'var(--color-sage, #2C5E55)',
                            padding: '4px'
                          }}
                        >
                          <Megaphone size={16} />
                        </button>
                      )}

                      {row.status === 'Open' && row.id && (
                        <button
                          type="button"
                          onClick={() => navigate(`/lab-projects/localization/marketplace/${row.id}/bids`)}
                          title={`Review Bids (${row.bidCount})`}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'var(--color-sage, #2C5E55)',
                            padding: '4px'
                          }}
                        >
                          <Users size={16} />
                        </button>
                      )}

                      {row.status === 'SubmittedForReview' && (
                        <button
                          type="button"
                          onClick={() => navigate(`/lab-projects/localization?locale=${row.localeCode}&jobId=${row.id}`)}
                          title="Review Strings in Strings Tab"
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'var(--color-ink, #1F2937)',
                            padding: '4px'
                          }}
                        >
                          <Search size={16} />
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

      {/* 7.6 Post to Marketplace Confirmation Drawer */}
      {confirmLocaleRow && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            zIndex: 1100,
            display: 'flex',
            justifyContent: 'flex-end'
          }}
          onClick={() => setConfirmLocaleRow(null)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '480px',
              height: '100%',
              backgroundColor: '#FFFFFF',
              boxShadow: '-12px 0 24px rgba(0,0,0,0.12)',
              display: 'flex',
              flexDirection: 'column',
              boxSizing: 'border-box'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Drawer Header */}
            <div
              style={{
                padding: '1.25rem 1.5rem',
                borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                backgroundColor: 'var(--color-parchment-card, #F8F6F0)'
              }}
            >
              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-sage, #2C5E55)', fontWeight: '700' }}>
                  Marketplace Publication
                </span>
                <h3 style={{ margin: '0.25rem 0 0 0', fontSize: '1.15rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
                  Post {confirmLocaleRow.localeCode} to Marketplace
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setConfirmLocaleRow(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--color-ink-muted, #6B7280)',
                  padding: '4px'
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Drawer Body */}
            <div style={{ padding: '1.5rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-ink, #1F2937)', lineHeight: '1.5' }}>
                You are about to publish an open translation job for the <strong>{confirmLocaleRow.localeCode}</strong> target locale.
                Vetted translators proficient in this language pair will be invited to submit bids.
              </p>

              <div
                style={{
                  border: '1px solid var(--color-border-subtle, #E2DDD5)',
                  borderRadius: '6px',
                  backgroundColor: '#FAFAF9',
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                  fontSize: '0.85rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>Remaining Strings:</span>
                  <span style={{ fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>{confirmLocaleRow.stringCount}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>Total Word Count:</span>
                  <span style={{ fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>{confirmLocaleRow.wordCount} words</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>Suggested Price Band:</span>
                  <span style={{ fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
                    {confirmLocaleRow.suggestedPriceLow} – {confirmLocaleRow.suggestedPriceHigh} Credits
                  </span>
                </div>
              </div>
            </div>

            {/* Drawer Footer with one icon-only Post button */}
            <div
              style={{
                padding: '1.25rem 1.5rem',
                borderTop: '1px solid var(--color-border-subtle, #E2DDD5)',
                display: 'flex',
                justifyContent: 'flex-end',
                backgroundColor: 'var(--color-parchment-card, #F8F6F0)'
              }}
            >
              <button
                type="button"
                disabled={isPosting}
                onClick={handleConfirmPost}
                title="Post to Marketplace"
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  border: 'none',
                  backgroundColor: 'var(--color-sage, #2C5E55)',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: isPosting ? 'wait' : 'pointer'
                }}
              >
                {isPosting ? <RefreshCw size={16} className="spin" /> : <Megaphone size={16} />}
              </button>
            </div>
          </div>
        </div>
      )}
    </LocalizationShell>
  );
}
