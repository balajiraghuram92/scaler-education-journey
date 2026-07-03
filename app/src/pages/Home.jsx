import { useState, useEffect } from 'react';
import { User, GitBranch, Award } from 'lucide-react';
import { Link } from 'react-router-dom';
import VerticalCard from '../components/VerticalCard';

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
      {/* Hero Container */}
      <div className="glass-panel" style={{
        padding: 'var(--space-3xl)',
        textAlign: 'center',
        maxWidth: '900px',
        margin: '0 auto',
      }}>
        {/* Avatar Placeholder */}
        <div className="glow-effect" style={{
          width: '140px',
          height: '140px',
          borderRadius: '50%',
          margin: '0 auto var(--space-xl)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--bg-tertiary)',
          border: '2px solid var(--accent-cyan)',
        }}>
          <User size={56} style={{ color: 'var(--accent-cyan)' }} />
        </div>

        {/* Name */}
        <h1 className="gradient-text" style={{ marginBottom: 'var(--space-sm)' }}>
          Raghuram Balaji
        </h1>

        {/* Subtitle */}
        <h3 className="mb-md" style={{ color: 'var(--accent-cyan)' }}>
          AI Architect Candidate
        </h3>

        {/* Professional Summary */}
        <p style={{
          fontSize: '1.1rem',
          lineHeight: '1.8',
          color: 'var(--text-secondary)',
          maxWidth: '750px',
          margin: '0 auto var(--space-xl)',
        }}>
          I've spent seven years doing root-cause analysis on the runtime under Unity—the operational excellence half of this role is my day job. In 2018 I built ML-based automation before it was fashionable: a video pipeline feeding a CNN for defect detection inside a supply-chain automation platform. This year I rebuilt my two most relevant systems with the 2026 AI layer—structured LLM ticket triage with guardrails, an eval pipeline, human-in-the-loop review, and hybrid local/cloud model routing.
        </p>

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          gap: 'var(--space-lg)',
          justifyContent: 'center',
          flexWrap: 'wrap',
        }}>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
            style={{ display: 'inline-flex' }}
          >
            <GitBranch size={18} />
            View GitHub
          </a>

          <Link
            to="/certifications"
            className="btn btn-primary"
            style={{ display: 'inline-flex' }}
          >
            <Award size={18} />
            View Certifications
          </Link>
        </div>
      </div>

      {/* Study Verticals Grid */}
      <section className="mt-xl">
        <h2 className="mb-lg">Study Verticals</h2>
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
