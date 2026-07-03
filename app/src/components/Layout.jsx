import Navbar from './Navbar';

export default function Layout({ children }) {
  return (
    <div style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
      {/* Ambient Background Orbs */}
      <div className="bg-orb bg-orb--cyan" />
      <div className="bg-orb bg-orb--purple" />
      <div className="bg-orb bg-orb--emerald" />

      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <main className="container mt-xl" style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </main>
    </div>
  );
}
