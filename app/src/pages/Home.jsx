import { useState, useEffect, useCallback } from 'react';
import VerticalCard from '../components/VerticalCard';
import MarkdownIngestModal from '../components/MarkdownIngestModal';
import { Compass, Layers, CheckCircle2, Clock, UploadCloud, TrendingUp, Sparkles, RefreshCw } from 'lucide-react';

export default function Home() {
  const [verticals, setVerticals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchVerticals = useCallback(() => {
    setLoading(true);
    fetch('/api/verticals')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setVerticals(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch verticals:', err);
        setLoading(false);
      });
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

  const getIconByVertical = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes('lab')) return 'server';
    if (lower.includes('azure') || lower.includes('cert')) return 'cloud';
    if (lower.includes('fde') || lower.includes('ai')) return 'brain-circuit';
    return 'grid-3x3';
  };

  // Aggregated Analytics
  const totalVerticals = verticals.length;
  const totalTasks = verticals.reduce((sum, v) => sum + (v.tasks?.length || 0), 0);
  const totalCompleted = verticals.reduce((sum, v) => sum + (v.tasks?.filter(t => t.isCompleted).length || 0), 0);
  const pendingTasks = totalTasks - totalCompleted;
  const overallProgress = totalTasks > 0 ? Math.round((totalCompleted / totalTasks) * 100) : 0;

  // Circular ring calculations
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (overallProgress / 100) * circumference;

  return (
    <div className="mt-md" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Glassmorphic Analytics Banner */}
      <section
        className="glass-panel"
        style={{
          padding: 'var(--space-xl)',
          background: 'linear-gradient(135deg, rgba(26, 26, 46, 0.7), rgba(18, 18, 26, 0.9))',
          border: '1px solid var(--border-accent)',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header Title Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-md)', marginBottom: 'var(--space-xl)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
            <div
              style={{
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-glow-cyan)'
              }}
            >
              <Compass size={32} style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <div>
              <h1 className="gradient-text" style={{ fontSize: '2.2rem', margin: 0 }}>
                Interactive SPA Dashboard
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', margin: 0 }}>
                Multi-vertical study metrics & dynamic curriculum ingestion platform
              </p>
            </div>
          </div>

          <button
            type="button"
            className="btn btn-primary glow-effect"
            onClick={() => setIsModalOpen(true)}
            style={{ display: 'inline-flex', gap: 'var(--space-xs)' }}
          >
            <UploadCloud size={20} />
            <span>Ingest Markdown Curriculum</span>
          </button>
        </div>

        {/* Analytics Multi-Metric Display */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--space-lg)',
            alignItems: 'center'
          }}
        >
          {/* Circular Progress Banner Card */}
          <div
            style={{
              padding: 'var(--space-lg)',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-lg)'
            }}
          >
            <div style={{ position: 'relative', width: '90px', height: '90px', flexShrink: 0 }}>
              <svg width="90" height="90" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                <circle
                  cx="50"
                  cy="50"
                  r={radius}
                  fill="none"
                  stroke="rgba(255, 255, 255, 0.05)"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r={radius}
                  fill="none"
                  stroke="url(#dashboard-cyan-gradient)"
                  strokeWidth="8"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
                />
                <defs>
                  <linearGradient id="dashboard-cyan-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="var(--accent-cyan)" />
                    <stop offset="100%" stopColor="var(--accent-purple)" />
                  </linearGradient>
                </defs>
              </svg>
              <div
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  fontWeight: 800,
                  fontSize: '1.2rem',
                  color: 'var(--text-primary)'
                }}
              >
                {overallProgress}%
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 700, textTransform: 'uppercase' }}>
                <TrendingUp size={14} />
                <span>Overall Mastery</span>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', margin: '2px 0' }}>
                {totalCompleted} / {totalTasks}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Completed Curriculum Tasks
              </div>
            </div>
          </div>

          {/* Stat Counter 1: Active Verticals */}
          <div
            style={{
              padding: 'var(--space-lg)',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-md)'
            }}
          >
            <div
              style={{
                width: '50px',
                height: '50px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(0, 240, 255, 0.08)',
                border: '1px solid var(--border-accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
            >
              <Layers size={24} style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                {totalVerticals}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Active Study Tracks
              </div>
            </div>
          </div>

          {/* Stat Counter 2: Completed Lessons */}
          <div
            style={{
              padding: 'var(--space-lg)',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-md)'
            }}
          >
            <div
              style={{
                width: '50px',
                height: '50px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(0, 255, 157, 0.08)',
                border: '1px solid rgba(0, 255, 157, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
            >
              <CheckCircle2 size={24} style={{ color: 'var(--accent-emerald)' }} />
            </div>
            <div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                {totalCompleted}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Completed Lessons
              </div>
            </div>
          </div>

          {/* Stat Counter 3: Pending Tasks */}
          <div
            style={{
              padding: 'var(--space-lg)',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-md)'
            }}
          >
            <div
              style={{
                width: '50px',
                height: '50px',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(123, 47, 247, 0.1)',
                border: '1px solid rgba(123, 47, 247, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
            >
              <Clock size={24} style={{ color: 'var(--accent-purple)' }} />
            </div>
            <div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                {pendingTasks}
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Pending Tasks
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Study Verticals Primary Grid */}
      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
          <div>
            <h2 className="gradient-text" style={{ fontSize: '1.6rem', margin: 0 }}>
              Study Verticals
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', margin: 0 }}>
              Curated architectural tracks & hands-on engineering lab modules
            </p>
          </div>
          <button
            onClick={fetchVerticals}
            className="btn btn-secondary"
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Refresh Tracks</span>
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-3xl)', color: 'var(--text-muted)' }}>
            Loading study verticals...
          </div>
        ) : verticals.length === 0 ? (
          <div className="glass-panel text-center" style={{ padding: 'var(--space-3xl)' }}>
            <Sparkles size={40} style={{ color: 'var(--accent-cyan)', marginBottom: 'var(--space-md)' }} />
            <h3>No Verticals Found</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)' }}>
              Get started by ingesting a Markdown curriculum or creating a vertical!
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="btn btn-primary"
            >
              <UploadCloud size={18} />
              Ingest First Curriculum
            </button>
          </div>
        ) : (
          <div className="grid grid-3">
            {verticals.map(vertical => (
              <VerticalCard
                key={vertical.id}
                title={vertical.name}
                icon={getIconByVertical(vertical.name)}
                description={vertical.description}
                linkTo={`/vertical/${vertical.id}`}
                tasks={vertical.tasks || []}
              />
            ))}
          </div>
        )}
      </section>

      {/* Markdown Ingest Modal */}
      <MarkdownIngestModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchVerticals}
        verticals={verticals}
      />
    </div>
  );
}
