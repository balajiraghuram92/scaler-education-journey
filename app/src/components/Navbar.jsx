import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Hexagon, FolderGit2, BookOpen, ChevronDown, Server, BrainCircuit, Home as HomeIcon } from 'lucide-react';

export default function Navbar() {
  const [labId, setLabId] = useState(1);
  const [fdeId, setFdeId] = useState(3);
  const [openDropdown, setOpenDropdown] = useState(null);
  const location = useLocation();
  const navRef = useRef(null);

  useEffect(() => {
    fetch('/api/verticals')
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        if (Array.isArray(data)) {
          const lab = data.find((v) => v.name.toLowerCase().includes('lab'));
          if (lab) setLabId(lab.id);
          const fde = data.find((v) => v.name.toLowerCase().includes('fde'));
          if (fde) setFdeId(fde.id);
        }
      })
      .catch(() => {});
  }, []);

  // Close dropdown on route change
  useEffect(() => {
    setOpenDropdown(null);
  }, [location]);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (navRef.current && !navRef.current.contains(event.target)) {
        setOpenDropdown(null);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMouseEnter = (name) => {
    setOpenDropdown(name);
  };

  const handleMouseLeave = () => {
    setOpenDropdown(null);
  };

  const toggleDropdown = (name) => {
    setOpenDropdown((prev) => (prev === name ? null : name));
  };

  return (
    <nav
      ref={navRef}
      className="glass-panel"
      style={{
        position: 'sticky',
        top: '1rem',
        margin: '0 auto var(--space-lg)',
        maxWidth: '1200px',
        zIndex: 1000,
        overflow: 'visible',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-md)',
        }}
      >
        {/* Top Left Brand Link to Profile */}
        <Link
          to="/profile"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-sm)',
            textDecoration: 'none',
          }}
        >
          <Hexagon size={28} style={{ color: 'var(--accent-cyan)' }} />
          <span className="gradient-text" style={{ fontSize: '1.25rem' }}>
            Raghuram Balaji
          </span>
        </Link>

        {/* Navigation Links */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-md)',
          }}
        >
          {/* Home */}
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
            <HomeIcon size={16} />
            <span>Home</span>
          </Link>

          {/* Projects Dropdown */}
          <div
            className="nav-dropdown-wrapper"
            onMouseEnter={() => handleMouseEnter('projects')}
            onMouseLeave={handleMouseLeave}
            style={{ position: 'relative' }}
          >
            <button
              type="button"
              onClick={() => toggleDropdown('projects')}
              className={`nav-dropdown-btn ${openDropdown === 'projects' || location.pathname.startsWith('/vertical/1') ? 'active' : ''}`}
              aria-expanded={openDropdown === 'projects'}
            >
              <FolderGit2 size={16} />
              <span>Projects</span>
              <ChevronDown
                size={14}
                className={`dropdown-chevron ${openDropdown === 'projects' ? 'open' : ''}`}
              />
            </button>

            {openDropdown === 'projects' && (
              <div className="nav-dropdown-menu">
                <Link
                  to={`/vertical/${labId}`}
                  className="nav-dropdown-item"
                  onClick={() => setOpenDropdown(null)}
                >
                  <div className="dropdown-item-icon">
                    <Server size={18} />
                  </div>
                  <div>
                    <div className="dropdown-item-title">Lab Projects</div>
                    <div className="dropdown-item-desc">Rebuild, Break, Narrate</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* Lessons Dropdown */}
          <div
            className="nav-dropdown-wrapper"
            onMouseEnter={() => handleMouseEnter('lessons')}
            onMouseLeave={handleMouseLeave}
            style={{ position: 'relative' }}
          >
            <button
              type="button"
              onClick={() => toggleDropdown('lessons')}
              className={`nav-dropdown-btn ${openDropdown === 'lessons' || location.pathname.startsWith('/vertical/3') ? 'active' : ''}`}
              aria-expanded={openDropdown === 'lessons'}
            >
              <BookOpen size={16} />
              <span>Lessons</span>
              <ChevronDown
                size={14}
                className={`dropdown-chevron ${openDropdown === 'lessons' ? 'open' : ''}`}
              />
            </button>

            {openDropdown === 'lessons' && (
              <div className="nav-dropdown-menu">
                <Link
                  to={`/vertical/${fdeId}`}
                  className="nav-dropdown-item"
                  onClick={() => setOpenDropdown(null)}
                >
                  <div className="dropdown-item-icon">
                    <BrainCircuit size={18} />
                  </div>
                  <div>
                    <div className="dropdown-item-title">FDE Self-Study</div>
                    <div className="dropdown-item-desc">Agentic AI Curriculum Track</div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

