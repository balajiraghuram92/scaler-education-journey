import { Link, useLocation } from 'react-router-dom';
import { User } from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const location = useLocation();

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

          {/* Center: Navigation Links */}
          <div className="navbar-section navbar-center">
            <Link
              to="/"
              className={`navbar-nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Knowledge Atlas
            </Link>
            <span className="navbar-nav-divider">·</span>
            <Link
              to="/reading-map"
              className={`navbar-nav-link ${location.pathname === '/reading-map' || location.pathname === '/lab-projects' ? 'active' : ''}`}
            >
              Reading Map
            </Link>
            <span className="navbar-nav-divider">·</span>
            <Link
              to="/chapter/structured-concurrency"
              className={`navbar-nav-link ${location.pathname.startsWith('/chapter') || location.pathname === '/learning' ? 'active' : ''}`}
            >
              Concept Chapters
            </Link>
          </div>

          {/* Right: Author Profile */}
          <div className="navbar-section navbar-right">
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
