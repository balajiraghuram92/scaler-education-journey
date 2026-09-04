import { Link } from 'react-router-dom';
import { User, LogOut, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth();

  return (
    <>
      <header className="editorial-navbar-wrapper">
        <nav className="editorial-navbar" aria-label="Main Navigation">
          {/* Left: Brand Logo + Brand Name */}
          <div className="navbar-section navbar-left">
            <Link to="/" className="navbar-brand-pill">
              <img src="/favicon.svg" alt="Neuralascent Logo" className="navbar-brand-logo" />
              <span className="brand-pill-text">Neuralascent</span>
            </Link>
          </div>

          {/* Right: Auth Controls & Author Profile */}
          <div className="navbar-section navbar-right">
            {isAdmin && (
              <Link to="/admin/users" className="navbar-auth-pill admin-pill" title="Admin User Management">
                <Shield size={13} />
                <span>Admin</span>
              </Link>
            )}

            {user ? (
              <div className="navbar-user-menu">
                <span className="navbar-user-display" title={user.email}>
                  {user.displayName || user.email.split('@')[0]}
                </span>
                <button
                  type="button"
                  onClick={logout}
                  className="navbar-logout-btn"
                  title="Sign Out"
                >
                  <LogOut size={14} />
                </button>
              </div>
            ) : (
              <Link to="/login" className="navbar-auth-pill signin-pill">
                Sign In
              </Link>
            )}

            <div className="navbar-divider" />

            <Link to="/profile" className="navbar-author-profile" title="View Profile & Certifications">
              <span className="author-name">By Raghuram Balaji</span>
              <div className="author-avatar-wrapper">
                <img
                  src="/raghuram-profile.jpg"
                  alt="Raghuram Balaji"
                  className="author-avatar-img"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    if (e.currentTarget.nextSibling) {
                      e.currentTarget.nextSibling.style.display = 'flex';
                    }
                  }}
                />
                <div className="author-avatar-fallback">
                  <User size={16} />
                </div>
              </div>
            </Link>
          </div>
        </nav>
      </header>
    </>
  );
}
