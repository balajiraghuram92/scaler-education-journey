import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Edit2, Lock, Check, ArrowRight, X, AlertTriangle, CheckCircle, RefreshCw, Flag, ThumbsUp, RotateCcw } from 'lucide-react';
import LocalizationShell from './LocalizationShell';
import { api } from '../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';

const STAGES = ['New', 'Translated', 'Reviewed', 'Approved'];

export default function LocalizationStrings() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialLocale = searchParams.get('locale') || 'de-DE';
  const jobIdParam = searchParams.get('jobId');

  const [projectSlug] = useState('auroraline-hud-v3');
  const [selectedLocale, setSelectedLocale] = useState(initialLocale);
  const [locales, setLocales] = useState([
    { localeCode: 'de-DE', displayName: 'German (Germany)' },
    { localeCode: 'ja-JP', displayName: 'Japanese (Japan)' },
    { localeCode: 'zh-CN', displayName: 'Chinese Simplified (China)' },
    { localeCode: 'fr-FR', displayName: 'French (France)' },
    { localeCode: 'es-ES', displayName: 'Spanish (Spain)' }
  ]);
  const [strings, setStrings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Drawer state
  const [activeStringIndex, setActiveStringIndex] = useState(null);
  const [drawerTargetText, setDrawerTargetText] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // Review submission mode banner
  const [reviewJobId, setReviewJobId] = useState(jobIdParam ? parseInt(jobIdParam, 10) : null);
  const [reviewActionStatus, setReviewActionStatus] = useState(null);

  const fetchStrings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.localization.getStrings(projectSlug, selectedLocale);
      if (Array.isArray(data)) {
        setStrings(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load localization strings.');
    } finally {
      setLoading(false);
    }
  }, [projectSlug, selectedLocale]);

  useEffect(() => {
    fetchStrings();
  }, [fetchStrings]);

  useEffect(() => {
    const loc = searchParams.get('locale');
    if (loc && loc !== selectedLocale) {
      setSelectedLocale(loc);
    }
    const jId = searchParams.get('jobId');
    if (jId) {
      setReviewJobId(parseInt(jId, 10));
    }
  }, [searchParams, selectedLocale]);

  const handleLocaleChange = (e) => {
    const newLocale = e.target.value;
    setSelectedLocale(newLocale);
    setSearchParams({ locale: newLocale, ...(reviewJobId ? { jobId: reviewJobId } : {}) });
  };

  const openDrawer = (index) => {
    setActiveStringIndex(index);
    setDrawerTargetText(strings[index]?.targetText || '');
    setSaveError(null);
  };

  const closeDrawer = () => {
    setActiveStringIndex(null);
    setDrawerTargetText('');
    setSaveError(null);
  };

  const handleSaveAndNext = async () => {
    if (activeStringIndex === null) return;
    const current = strings[activeStringIndex];
    setIsSaving(true);
    setSaveError(null);

    try {
      const updated = await api.localization.updateTranslation(
        projectSlug,
        current.stringId,
        selectedLocale,
        drawerTargetText
      );

      // Update local state row
      const newStrings = [...strings];
      newStrings[activeStringIndex] = updated;
      setStrings(newStrings);

      // Advance to next row
      let nextIndex = -1;
      for (let i = activeStringIndex + 1; i < strings.length; i++) {
        if (!strings[i].targetText || strings[i].stage === 'New') {
          nextIndex = i;
          break;
        }
      }

      if (nextIndex !== -1) {
        setActiveStringIndex(nextIndex);
        setDrawerTargetText(strings[nextIndex]?.targetText || '');
      } else {
        closeDrawer();
      }
    } catch (err) {
      setSaveError(err.message || 'Failed to save translation.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSkip = () => {
    if (activeStringIndex === null) return;
    if (activeStringIndex + 1 < strings.length) {
      const nextIndex = activeStringIndex + 1;
      setActiveStringIndex(nextIndex);
      setDrawerTargetText(strings[nextIndex]?.targetText || '');
    } else {
      closeDrawer();
    }
  };

  const handleApproveSubmission = async () => {
    if (!reviewJobId) return;
    try {
      await api.localization.approveSubmission(reviewJobId);
      setReviewActionStatus('Submission Approved! Translation stages updated to Approved and credits recorded.');
      fetchStrings();
    } catch (err) {
      setReviewActionStatus(`Error: ${err.message}`);
    }
  };

  const handleSendBack = async () => {
    if (!reviewJobId) return;
    try {
      await api.localization.sendBackForRevision(reviewJobId);
      setReviewActionStatus('Job sent back for vendor revision.');
    } catch (err) {
      setReviewActionStatus(`Error: ${err.message}`);
    }
  };

  const hasQpsColumn = strings.some((s) => s.qpsScore !== null && s.qpsScore !== undefined);
  const activeString = activeStringIndex !== null ? strings[activeStringIndex] : null;

  return (
    <LocalizationShell activeTab="strings">
      {/* Locale Selector Bar & Review Toolbar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.25rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <label htmlFor="locale-filter" style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>
            Target Locale:
          </label>
          <select
            id="locale-filter"
            value={selectedLocale}
            onChange={handleLocaleChange}
            style={{
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: '1px solid var(--color-border-subtle, #E2DDD5)',
              backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
              color: 'var(--color-ink, #1F2937)',
              fontSize: '0.85rem',
              fontWeight: '600',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {locales.map((loc) => (
              <option key={loc.localeCode} value={loc.localeCode}>
                {loc.displayName} ({loc.localeCode})
              </option>
            ))}
          </select>
        </div>

        {/* Review Actions if navigated from Marketplace */}
        {reviewJobId && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              backgroundColor: 'rgba(44, 94, 85, 0.06)',
              border: '1px solid var(--color-sage, #2C5E55)',
              padding: '0.4rem 0.85rem',
              borderRadius: '6px'
            }}
          >
            <span style={{ fontSize: '0.8rem', fontWeight: '600', color: 'var(--color-sage, #2C5E55)' }}>
              Vendor Submission Review Mode
            </span>
            <button
              type="button"
              onClick={handleApproveSubmission}
              title="Approve Submission"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '0.3rem 0.65rem',
                backgroundColor: 'var(--color-sage, #2C5E55)',
                color: '#FFF',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              <ThumbsUp size={12} /> Approve
            </button>
            <button
              type="button"
              onClick={handleSendBack}
              title="Send Back for Revision"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '0.3rem 0.65rem',
                backgroundColor: '#FFF',
                color: '#991B1B',
                border: '1px solid #F87171',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              <RotateCcw size={12} /> Send Back
            </button>
          </div>
        )}
      </div>

      {reviewActionStatus && (
        <div
          style={{
            padding: '0.75rem 1rem',
            backgroundColor: '#F0FDF4',
            border: '1px solid #86EFAC',
            borderRadius: '6px',
            color: '#166534',
            fontSize: '0.85rem',
            marginBottom: '1rem'
          }}
        >
          {reviewActionStatus}
        </div>
      )}

      {/* Main Ruled Table */}
      {error ? (
        <ErrorState error={error} onRetry={fetchStrings} title="Unable to Load Strings" />
      ) : loading ? (
        <LoadingState message="Loading localized string records..." />
      ) : strings.length === 0 ? (
        <EmptyState message="No strings found for this locale." icon="🌐" />
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
                <th style={{ padding: '0.85rem 1rem', width: '40px' }}>#</th>
                <th style={{ padding: '0.85rem 1rem', width: '220px' }}>KEY</th>
                <th style={{ padding: '0.85rem 1rem' }}>SOURCE (EN)</th>
                <th style={{ padding: '0.85rem 1rem' }}>TARGET ({selectedLocale.split('-')[0].toUpperCase()})</th>
                {hasQpsColumn && <th style={{ padding: '0.85rem 1rem', width: '80px' }}>QPS</th>}
                <th style={{ padding: '0.85rem 1rem', width: '160px' }}>STAGE</th>
                <th style={{ padding: '0.85rem 1rem', width: '50px', textAlign: 'center' }}></th>
              </tr>
            </thead>
            <tbody>
              {strings.map((str, idx) => {
                const stageIndex = STAGES.indexOf(str.stage);
                const isNeedsReview = str.needsReview;

                return (
                  <tr
                    key={str.stringId}
                    onClick={() => openDrawer(idx)}
                    style={{
                      borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease'
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(44, 94, 85, 0.02)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--color-ink-muted, #6B7280)', fontSize: '0.8rem' }}>
                      {idx + 1}
                    </td>
                    <td style={{ padding: '0.85rem 1rem', fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--color-ink, #1F2937)' }}>
                      {str.key}
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--color-ink, #1F2937)' }}>
                      {str.sourceText}
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: str.targetText ? 'var(--color-ink, #1F2937)' : 'var(--color-ink-muted, #6B7280)', fontStyle: str.targetText ? 'normal' : 'italic' }}>
                      {str.targetText || '—'}
                    </td>

                    {/* QPS Column */}
                    {hasQpsColumn && (
                      <td style={{ padding: '0.85rem 1rem' }}>
                        {str.qpsScore !== null && str.qpsScore !== undefined ? (
                          <span
                            style={{
                              fontWeight: '700',
                              fontSize: '0.85rem',
                              color: str.qpsScore >= 70 ? 'var(--color-sage, #2C5E55)' : '#A6772C'
                            }}
                          >
                            {str.qpsScore}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>—</span>
                        )}
                      </td>
                    )}

                    {/* STAGE Column: Needs Review Flag or Dot Track */}
                    <td style={{ padding: '0.85rem 1rem' }}>
                      {isNeedsReview ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#A6772C', fontWeight: '600', fontSize: '0.8rem' }}>
                          <Flag size={14} />
                          <span>Needs Review</span>
                        </div>
                      ) : (
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            {STAGES.map((s, sIdx) => {
                              const isFilled = stageIndex >= sIdx && stageIndex !== -1;
                              return (
                                <span
                                  key={s}
                                  title={s}
                                  style={{
                                    width: '8px',
                                    height: '8px',
                                    borderRadius: '50%',
                                    backgroundColor: isFilled ? 'var(--color-sage, #2C5E55)' : '#FFFFFF',
                                    border: isFilled ? 'none' : '1.5px solid var(--color-ink-muted, #6B7280)',
                                    display: 'inline-block'
                                  }}
                                />
                              );
                            })}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-muted, #6B7280)', marginTop: '2px' }}>
                            {str.stage}
                          </div>
                        </div>
                      )}
                    </td>

                    {/* Pencil Action Icon */}
                    <td style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          openDrawer(idx);
                        }}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: 'var(--color-ink-muted, #6B7280)',
                          padding: '4px',
                          borderRadius: '4px'
                        }}
                        title="Edit Translation"
                      >
                        <Edit2 size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 7.3 Right-Anchored Edit Drawer */}
      {activeString && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            zIndex: 1100,
            display: 'flex',
            justifyContent: 'flex-end'
          }}
          onClick={closeDrawer}
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
                  String Editor • Locale: {selectedLocale}
                </span>
                <h3
                  style={{
                    margin: '0.25rem 0 0 0',
                    fontSize: '1rem',
                    fontFamily: 'monospace',
                    color: 'var(--color-ink, #1F2937)'
                  }}
                >
                  {activeString.key}
                </h3>
              </div>
              <button
                type="button"
                onClick={closeDrawer}
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
              {saveError && (
                <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#FEF2F2', border: '1px solid #F87171', borderRadius: '6px', color: '#991B1B', fontSize: '0.85rem' }}>
                  {saveError}
                </div>
              )}

              {/* Stage indicator */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)', fontWeight: '600' }}>
                  Current Stage:
                </span>
                <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
                  {activeString.stage}
                </span>
              </div>

              {/* Read-Only Source Text Box */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>
                    Source Text (English)
                  </span>
                  <Lock size={13} color="var(--color-ink-muted, #6B7280)" title="Source text is locked" />
                </div>
                <div
                  style={{
                    padding: '0.85rem 1rem',
                    backgroundColor: 'var(--color-parchment-card, #F8F6F0)',
                    border: '1px solid var(--color-border-subtle, #E2DDD5)',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    color: 'var(--color-ink, #1F2937)',
                    lineHeight: '1.5'
                  }}
                >
                  {activeString.sourceText}
                </div>
              </div>

              {/* Thin Sage Divider */}
              <div style={{ height: '1px', backgroundColor: 'var(--color-sage, #2C5E55)', opacity: 0.3, margin: '0.25rem 0' }} />

              {/* Editable Target Text Box */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                  Target Text ({selectedLocale})
                </span>
                <textarea
                  value={drawerTargetText}
                  onChange={(e) => setDrawerTargetText(e.target.value)}
                  placeholder={`Enter ${selectedLocale} translation...`}
                  style={{
                    flex: 1,
                    minHeight: '130px',
                    padding: '0.85rem 1rem',
                    borderRadius: '6px',
                    border: '1px solid var(--color-border-subtle, #E2DDD5)',
                    fontSize: '0.95rem',
                    fontFamily: 'inherit',
                    color: 'var(--color-ink, #1F2937)',
                    lineHeight: '1.5',
                    outline: 'none',
                    resize: 'none',
                    transition: 'border-color 0.15s ease'
                  }}
                  onFocus={(e) => (e.target.style.border = '2px solid var(--color-sage, #2C5E55)')}
                  onBlur={(e) => (e.target.style.border = '1px solid var(--color-border-subtle, #E2DDD5)')}
                />
              </div>
            </div>

            {/* Drawer Footer with single Save & Next button + Skip button */}
            <div
              style={{
                padding: '1.25rem 1.5rem',
                borderTop: '1px solid var(--color-border-subtle, #E2DDD5)',
                display: 'flex',
                justifyContent: 'flex-end',
                alignItems: 'center',
                gap: '1rem',
                backgroundColor: 'var(--color-parchment-card, #F8F6F0)'
              }}
            >
              {/* Outlined Arrow-Right Skip button */}
              <button
                type="button"
                onClick={handleSkip}
                title="Skip without saving"
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  border: '1px solid var(--color-border-subtle, #E2DDD5)',
                  backgroundColor: '#FFFFFF',
                  color: 'var(--color-ink, #1F2937)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer'
                }}
              >
                <ArrowRight size={18} />
              </button>

              {/* Filled Sage Circle Checkmark button: Save & Next */}
              <button
                type="button"
                disabled={isSaving}
                onClick={handleSaveAndNext}
                title="Save & Next"
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
                  cursor: isSaving ? 'wait' : 'pointer'
                }}
              >
                {isSaving ? <RefreshCw size={16} className="spin" /> : <Check size={18} />}
              </button>
            </div>
          </div>
        </div>
      )}
    </LocalizationShell>
  );
}
