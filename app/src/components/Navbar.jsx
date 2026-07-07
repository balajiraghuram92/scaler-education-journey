import { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Hexagon, FolderGit2, BookOpen, ChevronDown, Server, BrainCircuit, Home as HomeIcon, UploadCloud } from 'lucide-react';
import MarkdownIngestModal from './MarkdownIngestModal';
import './Navbar.css';

export default function Navbar() {
  const [verticals, setVerticals] = useState([]);
  const [labId, setLabId] = useState(1);
  const [fdeId, setFdeId] = useState(3);
  const [openDropdown, setOpenDropdown] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const location = useLocation();
  const navRef = useRef(null);

  const fetchVerticals = useCallback(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/verticals`)
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        if (Array.isArray(data)) {
          setVerticals(data);
          const lab = data.find((v) => v.name.toLowerCase().includes('lab'));
          if (lab) setLabId(lab.id);
          const fde = data.find((v) => v.name.toLowerCase().includes('fde'));
          if (fde) setFdeId(fde.id);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchVerticals();
  }, [fetchVerticals]);

  // Listen for global verticals update event
  useEffect(() => {
    const handleUpdate = () => {
      fetchVerticals();
    };
    window.addEventListener('verticalsUpdated', handleUpdate);
    return () => window.removeEventListener('verticalsUpdated', handleUpdate);
  }, [fetchVerticals]);

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

  const handleIngestSuccess = () => {
    fetchVerticals();
    window.dispatchEvent(new CustomEvent('verticalsUpdated'));
  };

  return (
    <>
      <nav ref={navRef} className="ai-navbar">
        <Link to="/profile" className="ai-nav-brand">
          <Hexagon size={28} className="brand-icon" />
          <span className="ai-nav-brand-text">Raghuram Balaji</span>
        </Link>

        <div className="ai-nav-links">
          {/* Home */}
          <Link to="/" className={`ai-nav-link ${location.pathname === '/' ? 'active' : ''}`}>
            <HomeIcon size={16} />
            <span>Home</span>
          </Link>

          {/* Projects Dropdown */}
          <div
            className="ai-nav-dropdown-wrapper"
            onMouseEnter={() => handleMouseEnter('projects')}
            onMouseLeave={handleMouseLeave}
          >
            <button
              type="button"
              onClick={() => toggleDropdown('projects')}
              className={`ai-nav-link ${openDropdown === 'projects' || location.pathname === '/lab-projects' ? 'active' : ''}`}
              aria-expanded={openDropdown === 'projects'}
            >
              <FolderGit2 size={16} />
              <span>Projects</span>
              <ChevronDown size={14} className={`ai-dropdown-chevron ${openDropdown === 'projects' ? 'open' : ''}`} />
            </button>

            {openDropdown === 'projects' && (
              <div className="ai-nav-dropdown-menu">
                <Link
                  to="/lab-projects"
                  className="ai-dropdown-item"
                  onClick={() => setOpenDropdown(null)}
                >
                  <div className="ai-dropdown-item-icon">
                    <Server size={18} />
                  </div>
                  <div>
                    <div className="ai-dropdown-item-title">Lab Projects</div>
                    <div className="ai-dropdown-item-desc">Rebuild, Break, Narrate</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* Lessons Dropdown */}
          <div
            className="ai-nav-dropdown-wrapper"
            onMouseEnter={() => handleMouseEnter('lessons')}
            onMouseLeave={handleMouseLeave}
          >
            <button
              type="button"
              onClick={() => toggleDropdown('lessons')}
              className={`ai-nav-link ${openDropdown === 'lessons' || location.pathname.startsWith(`/vertical/${fdeId}`) ? 'active' : ''}`}
              aria-expanded={openDropdown === 'lessons'}
            >
              <BookOpen size={16} />
              <span>Lessons</span>
              <ChevronDown size={14} className={`ai-dropdown-chevron ${openDropdown === 'lessons' ? 'open' : ''}`} />
            </button>

            {openDropdown === 'lessons' && (
              <div className="ai-nav-dropdown-menu">
                <Link
                  to={`/vertical/${fdeId}`}
                  className="ai-dropdown-item"
                  onClick={() => setOpenDropdown(null)}
                >
                  <div className="ai-dropdown-item-icon">
                    <BrainCircuit size={18} />
                  </div>
                  <div>
                    <div className="ai-dropdown-item-title">FDE Self-Study</div>
                    <div className="ai-dropdown-item-desc">Agentic AI Curriculum Track</div>
                  </div>
                </Link>
                <button
                  type="button"
                  className="ai-dropdown-item"
                  onClick={() => {
                    setOpenDropdown(null);
                    setIsModalOpen(true);
                  }}
                >
                  <div className="ai-dropdown-item-icon">
                    <UploadCloud size={18} />
                  </div>
                  <div>
                    <div className="ai-dropdown-item-title">Add Vertical</div>
                    <div className="ai-dropdown-item-desc">Import from Markdown</div>
                  </div>
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

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
