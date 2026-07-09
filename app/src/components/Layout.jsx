import Navbar from './Navbar';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <div className="layout-container">
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <main className="container mt-xl layout-main-content" style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </main>
    </div>
  );
}
