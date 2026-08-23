import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '3rem 2rem',
          maxWidth: '680px',
          margin: '3rem auto',
          backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
          border: '1px solid var(--color-border-subtle, #E2DDD5)',
          borderRadius: '8px',
          textAlign: 'center',
          boxShadow: '0 4px 16px rgba(0,0,0,0.04)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#D97706' }}>⚠️</div>
          <h2 style={{ fontFamily: 'var(--font-serif, "Newsreader", serif)', fontSize: '1.75rem', color: 'var(--color-ink, #1F2937)', marginBottom: '0.75rem' }}>
            {this.props.title || 'Something went wrong'}
          </h2>
          <p style={{ color: 'var(--color-ink-muted, #6B7280)', marginBottom: '1.5rem', lineHeight: '1.6' }}>
            {this.state.error?.message || 'An unexpected error occurred while rendering this page component.'}
          </p>
          <button
            onClick={this.handleRetry}
            style={{
              backgroundColor: 'var(--color-sage, #2C5E55)',
              color: '#FFFFFF',
              border: 'none',
              padding: '0.65rem 1.5rem',
              borderRadius: '6px',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '0.95rem'
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
