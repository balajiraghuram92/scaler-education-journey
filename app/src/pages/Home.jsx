import { useState, useEffect } from 'react';
import VerticalCard from '../components/VerticalCard';
import { Compass } from 'lucide-react';

export default function Home() {
  const [verticals, setVerticals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/verticals')
      .then(res => res.json())
      .then(data => {
        setVerticals(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch verticals:', err);
        setLoading(false);
      });
  }, []);

  const getIconByVertical = (name) => {
    if (name.includes('Lab')) return 'server';
    if (name.includes('Azure')) return 'cloud';
    if (name.includes('FDE')) return 'brain-circuit';
    return 'grid-3x3';
  };

  return (
    <div className="mt-md">
      {/* Compact Dashboard Header */}
      <div
        className="glass-panel mb-xl"
        style={{
          padding: 'var(--space-xl)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-lg)',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.03), rgba(0, 240, 255, 0.05))',
        }}
      >
        <div
          style={{
            padding: 'var(--space-md)',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--accent-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Compass size={32} style={{ color: 'var(--accent-cyan)' }} />
        </div>
        <div>
          <h1 className="gradient-text" style={{ fontSize: '2rem', marginBottom: 'var(--space-xs)' }}>
            Study Tracker Dashboard
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', margin: 0 }}>
            Track progress across Hands-on Labs, Azure Certifications, and FDE Agentic AI Curriculum
          </p>
        </div>
      </div>

      {/* Study Verticals Primary Grid */}
      <section>
        <h2 className="mb-lg" style={{ fontSize: '1.5rem' }}>
          Study Verticals
        </h2>
        {loading ? (
          <p className="text-secondary">Loading verticals...</p>
        ) : (
          <div className="grid grid-3">
            {verticals.map(vertical => (
              <VerticalCard
                key={vertical.id}
                title={vertical.name}
                icon={getIconByVertical(vertical.name)}
                description={vertical.description}
                linkTo={`/vertical/${vertical.id}`}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
