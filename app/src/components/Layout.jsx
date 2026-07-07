import Navbar from './Navbar';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <div className="layout-container">
      {/* Ambient Background Orbs */}
      <div className="ai-bg-orb ai-bg-orb--cyan" />
      <div className="ai-bg-orb ai-bg-orb--purple" />
      <div className="ai-bg-orb ai-bg-orb--emerald" />

      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <main className="container mt-xl layout-main-content" style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </main>
    </div>
  );
}
