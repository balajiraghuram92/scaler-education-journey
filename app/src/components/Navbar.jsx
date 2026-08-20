import { useState, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Globe, Plus, User } from 'lucide-react';
import MarkdownIngestModal from './MarkdownIngestModal';
import './Navbar.css';

export default function Navbar() {
  const [verticals, setVerticals] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const location = useLocation();

  const fetchVerticals = useCallback(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/verticals`, {
      headers: {
        'x-api-key': import.meta.env.VITE_API_KEY || ''
      }
    })
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        if (Array.isArray(data)) {
          setVerticals(data);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchVerticals();
  }, [fetchVerticals]);

  useEffect(() => {
    const handleUpdate = () => {
      fetchVerticals();
    };
    window.addEventListener('verticalsUpdated', handleUpdate);
    return () => window.removeEventListener('verticalsUpdated', handleUpdate);
  }, [fetchVerticals]);

  const handleIngestSuccess = () => {
    fetchVerticals();
    window.dispatchEvent(new CustomEvent('verticalsUpdated'));
  };

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

          {/* Right: Author Profile & Ingest Action */}
          <div className="navbar-section navbar-right">
            <button
              type="button"
              className="navbar-action-btn"
              onClick={() => setIsModalOpen(true)}
              title="Import Curriculum Markdown"
            >
              <Plus size={15} />
              <span>Import</span>
            </button>

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

      {/* Markdown Ingest Modal */}
      <MarkdownIngestModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleIngestSuccess}
        verticals={verticals}
      />
    </>
  );
}
