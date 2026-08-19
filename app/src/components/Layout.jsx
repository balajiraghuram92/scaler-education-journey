import Navbar from './Navbar';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <div className="layout-container">
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <main className="layout-main-content">
        {children}
      </main>
    </div>
  );
}
