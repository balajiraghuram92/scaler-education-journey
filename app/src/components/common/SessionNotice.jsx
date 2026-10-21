import { Link, useLocation } from 'react-router-dom';
import { Clock3, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './SessionNotice.css';

export default function SessionNotice() {
  const { sessionNotice, dismissSessionNotice } = useAuth();
  const location = useLocation();

  if (!sessionNotice || location.pathname === '/login') return null;

  return (
    <div className="session-notice" role="status" aria-live="polite">
      <Clock3 size={16} className="session-notice__icon" aria-hidden="true" />
      <div className="session-notice__copy">
        <strong>{sessionNotice.title}</strong>
        <span>{sessionNotice.message}</span>
      </div>
      <Link
        to="/login"
        state={{ from: location }}
        className="session-notice__action"
        onClick={dismissSessionNotice}
      >
        Sign in
      </Link>
      <button
        type="button"
        className="session-notice__dismiss"
        onClick={dismissSessionNotice}
        aria-label="Dismiss session notice"
      >
        <X size={14} />
      </button>
    </div>
  );
}
