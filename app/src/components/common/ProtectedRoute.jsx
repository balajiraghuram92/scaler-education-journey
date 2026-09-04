import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, isAuthenticated, isAdmin, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        fontFamily: 'var(--font-sans)',
        color: 'var(--ink-secondary)'
      }}>
        <p>Loading session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin) {
    return (
      <div style={{
        maxWidth: '600px',
        margin: '4rem auto',
        padding: '2rem',
        backgroundColor: 'var(--bg-paper)',
        border: '1px solid var(--rule-border)',
        borderRadius: 'var(--radius-md)',
        textAlign: 'center'
      }}>
        <h2 style={{ fontFamily: 'var(--font-serif)', color: 'var(--accent-terracotta)', marginBottom: '1rem' }}>
          Restricted Access
        </h2>
        <p style={{ color: 'var(--ink-secondary)', marginBottom: '1.5rem' }}>
          Administrator privileges are required to access this resource.
        </p>
        <a
          href="/"
          style={{
            display: 'inline-block',
            padding: '0.6rem 1.2rem',
            backgroundColor: 'var(--accent-sage)',
            color: '#FFFFFF',
            borderRadius: 'var(--radius-sm)',
            textDecoration: 'none',
            fontSize: '0.875rem'
          }}
        >
          Return to Overview
        </a>
      </div>
    );
  }

  return children;
}
