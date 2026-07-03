import { Link } from 'react-router-dom';
import { Hexagon } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="glass-panel" style={{
      position: 'sticky',
      top: '1rem',
      margin: '0 auto var(--space-lg)',
      maxWidth: '1200px',
      zIndex: 100,
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-md)',
      }}>
        {/* Brand */}
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)',
          textDecoration: 'none',
        }}>
          <Hexagon size={28} style={{ color: 'var(--accent-cyan)' }} />
          <span className="gradient-text" style={{ fontSize: '1.25rem' }}>
            Raghuram Balaji
          </span>
        </Link>

        {/* Navigation Links */}
        <div style={{
          display: 'flex',
          gap: 'var(--space-lg)',
          flexWrap: 'wrap',
        }}>
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/projects" className="nav-link">Projects</Link>
          <Link to="/certifications" className="nav-link">Certifications</Link>
          <Link to="/fde-study" className="nav-link">FDE Study</Link>
        </div>
      </div>
    </nav>
  );
}
