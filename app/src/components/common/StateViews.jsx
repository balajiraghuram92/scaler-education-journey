import React from 'react';

export function LoadingState({ message = 'Consulting the Knowledge Atlas...' }) {
  return (
    <div style={{
      padding: '4rem 2rem',
      textAlign: 'center',
      color: 'var(--color-ink-muted, #6B7280)',
      fontFamily: 'var(--font-sans, "Plus Jakarta Sans", sans-serif)'
    }}>
      <div style={{
        display: 'inline-block',
        width: '36px',
        height: '36px',
        border: '3px solid var(--color-border-subtle, #E2DDD5)',
        borderTopColor: 'var(--color-sage, #2C5E55)',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '1rem'
      }} />
      <p style={{ fontSize: '1rem', fontStyle: 'italic' }}>{message}</p>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export function ErrorState({ error, onRetry, title = 'Unable to Load Content' }) {
  const is401 = error?.status === 401;
  const is503 = error?.status === 503;

  if (is401) {
    return <UnauthorizedState onRetry={onRetry} />;
  }

  if (is503) {
    return <UnavailableState error={error} onRetry={onRetry} />;
  }

  return (
    <div style={{
      padding: '3rem 2rem',
      maxWidth: '600px',
      margin: '2rem auto',
      backgroundColor: '#FEF2F2',
      border: '1px solid #FECACA',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <h3 style={{ color: '#991B1B', marginBottom: '0.5rem', fontFamily: 'var(--font-serif, "Newsreader", serif)' }}>
        {title}
      </h3>
      <p style={{ color: '#7F1D1D', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
        {error?.message || 'A network error or database communication failure occurred.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            backgroundColor: '#DC2626',
            color: '#FFFFFF',
            border: 'none',
            padding: '0.5rem 1.25rem',
            borderRadius: '6px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Retry Connection
        </button>
      )}
    </div>
  );
}

export function UnauthorizedState({ onRetry }) {
  return (
    <div style={{
      padding: '3rem 2rem',
      maxWidth: '600px',
      margin: '2rem auto',
      backgroundColor: '#FFFBEB',
      border: '1px solid #FDE68A',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔒</div>
      <h3 style={{ color: '#92400E', marginBottom: '0.5rem', fontFamily: 'var(--font-serif, "Newsreader", serif)' }}>
        Authentication Required
      </h3>
      <p style={{ color: '#B45309', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
        Invalid or missing API key. Please check your client configuration.
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            backgroundColor: '#D97706',
            color: '#FFFFFF',
            border: 'none',
            padding: '0.5rem 1.25rem',
            borderRadius: '6px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Retry Request
        </button>
      )}
    </div>
  );
}

export function UnavailableState({ error, onRetry }) {
  return (
    <div style={{
      padding: '3rem 2rem',
      maxWidth: '600px',
      margin: '2rem auto',
      backgroundColor: '#F3F4F6',
      border: '1px solid #E5E7EB',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🛠️</div>
      <h3 style={{ color: '#374151', marginBottom: '0.5rem', fontFamily: 'var(--font-serif, "Newsreader", serif)' }}>
        Service Temporarily Unavailable
      </h3>
      <p style={{ color: '#4B5563', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
        {error?.message || 'Database schema migrations or maintenance are underway. Please try again shortly.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            backgroundColor: 'var(--color-sage, #2C5E55)',
            color: '#FFFFFF',
            border: 'none',
            padding: '0.5rem 1.25rem',
            borderRadius: '6px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Check Service Status
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message = 'No entries found in this path.', icon = '📖' }) {
  return (
    <div style={{
      padding: '3rem 2rem',
      textAlign: 'center',
      color: 'var(--color-ink-muted, #6B7280)',
      border: '1px dashed var(--color-border-subtle, #E2DDD5)',
      borderRadius: '8px',
      margin: '1.5rem 0'
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
      <p>{message}</p>
    </div>
  );
}

export function DevFixturesBanner() {
  return (
    <div style={{
      backgroundColor: '#FEF3C7',
      borderBottom: '1px solid #F59E0B',
      color: '#92400E',
      padding: '0.4rem 1rem',
      fontSize: '0.8rem',
      fontWeight: '600',
      textAlign: 'center'
    }}>
      ⚠️ DEVELOPMENT FIXTURE MODE ACTIVE — Rendering local fixtures for offline debugging.
    </div>
  );
}
