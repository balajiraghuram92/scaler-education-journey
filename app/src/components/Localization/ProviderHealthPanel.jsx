import React, { useState } from 'react';
import { X, Activity, AlertTriangle, CheckCircle, RefreshCw, Zap, ShieldAlert } from 'lucide-react';
import { api } from '../../api/client';

export default function ProviderHealthPanel({ isOpen, onClose, healthData, onRefresh }) {
  const [toggling, setToggling] = useState(null);
  const [actionError, setActionError] = useState(null);

  if (!isOpen) return null;

  const handleToggle = async (provider, currentState) => {
    setToggling(provider);
    setActionError(null);
    try {
      if (currentState.toLowerCase() === 'open') {
        await api.localization.resolveOutage(provider);
      } else {
        await api.localization.simulateOutage(provider);
      }
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      setActionError(err.message || 'Failed to update provider circuit state.');
    } finally {
      setToggling(null);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        zIndex: 1200,
        display: 'flex',
        justifyContent: 'flex-end',
        transition: 'opacity 0.2s ease-in-out'
      }}
      onClick={onClose}
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
          overflowY: 'auto'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Panel Header */}
        <div
          style={{
            padding: '1.5rem',
            borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            backgroundColor: 'var(--color-parchment-card, #F8F6F0)'
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="var(--color-sage, #2C5E55)" />
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
                Provider Health & Resilience
              </h3>
            </div>
            <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
              Real-time latency percentiles, error telemetry, and circuit breaker simulation.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-ink-muted, #6B7280)',
              padding: '4px',
              borderRadius: '4px'
            }}
            title="Close Panel"
          >
            <X size={18} />
          </button>
        </div>

        {/* Panel Content */}
        <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1 }}>
          {actionError && (
            <div style={{ padding: '0.75rem 1rem', backgroundColor: '#FEF2F2', border: '1px solid #F87171', borderRadius: '6px', color: '#991B1B', fontSize: '0.85rem' }}>
              {actionError}
            </div>
          )}

          {!healthData || healthData.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-ink-muted, #6B7280)', fontSize: '0.9rem' }}>
              No provider telemetry available.
            </div>
          ) : (
            healthData.map((p) => {
              const isOpen = p.circuitState?.toLowerCase() === 'open';
              const isHalfOpen = p.circuitState?.toLowerCase() === 'halfopen';
              const badgeColor = isOpen ? '#DC2626' : isHalfOpen ? '#A6772C' : 'var(--color-sage, #2C5E55)';
              const badgeBg = isOpen ? 'rgba(220, 38, 38, 0.08)' : isHalfOpen ? 'rgba(166, 119, 44, 0.08)' : 'rgba(44, 94, 85, 0.08)';

              return (
                <div
                  key={p.id || p.provider}
                  style={{
                    border: '1px solid var(--color-border-subtle, #E2DDD5)',
                    borderRadius: '8px',
                    padding: '1.25rem',
                    backgroundColor: '#FAFAF9',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--color-ink, #1F2937)' }}>
                        {p.provider === 'GoogleMT' ? 'Google Cloud Translation (v2)' : 'Azure OpenAI (GPT-4o Mini)'}
                      </div>
                      <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--color-ink-muted, #6B7280)' }}>
                        {p.provider}
                      </span>
                    </div>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '0.25rem 0.6rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: '700',
                        color: badgeColor,
                        backgroundColor: badgeBg,
                        border: `1px solid ${badgeColor}33`
                      }}
                    >
                      {isOpen ? <AlertTriangle size={13} /> : <CheckCircle size={13} />}
                      Circuit: {p.circuitState}
                    </span>
                  </div>

                  {/* Metrics Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
                    <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border-subtle, #E2DDD5)', borderRadius: '6px', padding: '0.6rem' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>P50 Latency</div>
                      <div style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--color-ink, #1F2937)', marginTop: '2px' }}>
                        {p.p50LatencyMs} <span style={{ fontSize: '0.75rem', fontWeight: '400' }}>ms</span>
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border-subtle, #E2DDD5)', borderRadius: '6px', padding: '0.6rem' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>P99 Latency</div>
                      <div style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--color-ink, #1F2937)', marginTop: '2px' }}>
                        {p.p99LatencyMs} <span style={{ fontSize: '0.75rem', fontWeight: '400' }}>ms</span>
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#FFFFFF', border: '1px solid var(--color-border-subtle, #E2DDD5)', borderRadius: '6px', padding: '0.6rem' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>Error Rate</div>
                      <div style={{ fontWeight: '700', fontSize: '1rem', color: isOpen ? '#DC2626' : 'var(--color-ink, #1F2937)', marginTop: '2px' }}>
                        {p.errorRatePercent}%
                      </div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '0.25rem' }}>
                    <button
                      type="button"
                      disabled={toggling === p.provider}
                      onClick={() => handleToggle(p.provider, p.circuitState)}
                      title={isOpen ? "Resolve simulated outage and close circuit" : "Simulate downstream service outage and trip circuit"}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '0.45rem 0.85rem',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: '600',
                        cursor: toggling === p.provider ? 'wait' : 'pointer',
                        border: isOpen ? '1px solid var(--color-sage, #2C5E55)' : '1px solid #DC2626',
                        backgroundColor: isOpen ? 'var(--color-sage, #2C5E55)' : '#FFFFFF',
                        color: isOpen ? '#FFFFFF' : '#DC2626',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      {toggling === p.provider ? (
                        <RefreshCw size={14} className="spin" />
                      ) : isOpen ? (
                        <CheckCircle size={14} />
                      ) : (
                        <ShieldAlert size={14} />
                      )}
                      {isOpen ? 'Resolve Outage' : 'Simulate Outage'}
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Panel Footer */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid var(--color-border-subtle, #E2DDD5)',
            fontSize: '0.75rem',
            color: 'var(--color-ink-muted, #6B7280)',
            backgroundColor: 'var(--color-parchment-card, #F8F6F0)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <span>Fallback Strategy: Dynamic Mock / Stored Translation</span>
          <button
            type="button"
            onClick={onRefresh}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-sage, #2C5E55)',
              fontSize: '0.75rem',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
      </div>
    </div>
  );
}
