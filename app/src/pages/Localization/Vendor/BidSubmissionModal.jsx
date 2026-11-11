import React, { useState, useEffect } from 'react';
import { X, RefreshCw } from 'lucide-react';
import { api } from '../../../api/client';

export default function BidSubmissionModal({ isOpen, onClose, job, vendorId, onSuccess }) {
  const defaultPrice = job
    ? Math.round((job.suggestedPriceLow + job.suggestedPriceHigh) / 2)
    : 0;
  const [proposedPrice, setProposedPrice] = useState(defaultPrice);
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (job) {
      setProposedPrice(defaultPrice);
      setNote('');
      setError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [job?.id]);

  if (!isOpen || !job) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!vendorId) {
      setError('No active vendor selected.');
      return;
    }
    const price = parseFloat(proposedPrice);
    if (!Number.isFinite(price) || price <= 0) {
      setError('Price must be greater than zero.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.vendorPortal.submitBid(vendorId, job.id, price, note);
      if (onSuccess) {
        onSuccess(job.id);
      }
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to submit bid.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.45)',
        zIndex: 1300,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '520px',
          backgroundColor: '#FFFFFF',
          borderRadius: '0px',
          border: '1px solid var(--color-border-subtle, #E2DDD5)',
          boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#FAFAF9'
          }}
        >
          <div>
            <h3 style={{ margin: 0, fontSize: '1.15rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
              Submit Translation Bid
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)' }}>
              Job: {job.localeCode} • {job.stringCount} strings ({job.wordCount} words)
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
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

        {/* Modal Form */}
        <form onSubmit={handleSubmit} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {error && (
            <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#FEF2F2', border: '1px solid #F87171', color: '#991B1B', fontSize: '0.85rem' }}>
              {error}
            </div>
          )}

          {/* Read-only Job Summary */}
          <div
            style={{
              backgroundColor: '#FAFAF9',
              border: '1px solid var(--color-border-subtle, #E2DDD5)',
              padding: '0.85rem 1rem',
              fontSize: '0.85rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.4rem'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>Suggested Price Band:</span>
              <span style={{ fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
                {job.suggestedPriceLow} – {job.suggestedPriceHigh} Credits
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--color-ink-muted, #6B7280)' }}>Target Locale:</span>
              <span style={{ fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>{job.localeCode}</span>
            </div>
          </div>

          {/* YOUR PRICE (CREDITS) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-ink-muted, #6B7280)' }}>
              Your Price (Credits)
            </label>
            <input
              type="number"
              min="10"
              max="5000"
              step="1"
              required
              value={proposedPrice}
              onChange={(e) => setProposedPrice(e.target.value)}
              style={{
                padding: '0.6rem 0.85rem',
                border: '1px solid var(--color-border-subtle, #E2DDD5)',
                borderRadius: '0px',
                fontSize: '1rem',
                color: 'var(--color-ink, #1F2937)',
                outline: 'none'
              }}
            />
          </div>

          {/* NOTE TO PROJECT OWNER */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-ink-muted, #6B7280)' }}>
              Note to Project Owner
            </label>
            <textarea
              rows={3}
              required
              placeholder="Highlight relevant automotive localization experience or turnaround timing..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              style={{
                padding: '0.6rem 0.85rem',
                border: '1px solid var(--color-border-subtle, #E2DDD5)',
                borderRadius: '0px',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
                color: 'var(--color-ink, #1F2937)',
                outline: 'none',
                resize: 'vertical'
              }}
            />
          </div>

          {/* Modal Actions */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '0.6rem 1rem',
                border: '1px solid var(--color-border-subtle, #E2DDD5)',
                borderRadius: '0px',
                backgroundColor: '#FFFFFF',
                color: 'var(--color-ink, #1F2937)',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>

            {/* Solid Sage Rectangular Text-Label Submit Bid Button */}
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: '0.6rem 1.25rem',
                border: 'none',
                borderRadius: '0px',
                backgroundColor: 'var(--color-sage, #2C5E55)',
                color: '#FFFFFF',
                fontSize: '0.85rem',
                fontWeight: '700',
                cursor: submitting ? 'wait' : 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              {submitting ? <RefreshCw size={14} className="spin" /> : null}
              Submit Bid
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
