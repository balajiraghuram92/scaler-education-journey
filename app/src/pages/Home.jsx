import { useState, useEffect, useCallback } from 'react';
import VerticalCard from '../components/VerticalCard';
import { Compass, Layers, CheckCircle2, Clock, UploadCloud, TrendingUp, Sparkles, RefreshCw } from 'lucide-react';
import './Home.css';

export default function Home() {
  const [verticals, setVerticals] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchVerticals = useCallback(() => {
    setLoading(true);
    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/verticals`)
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
    <div className="home-container">
      <div className="ai-ambient-light light-cyan"></div>
      <div className="ai-ambient-light light-purple"></div>

      {/* Glassmorphic Analytics Banner */}
      <section className="ai-glass-panel">
        {/* Header Title Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="neon-icon-box">
              <Compass size={32} style={{ color: '#0369a1' }} />
            </div>
            <div>
              <h1 className="ai-gradient-text" style={{ fontSize: '2.2rem', margin: 0 }}>
                Interactive AI Dashboard
              </h1>
              <p style={{ color: '#64748b', fontSize: '1.05rem', margin: '0.25rem 0 0' }}>
                Multi-vertical study metrics & dynamic task tracking
              </p>
            </div>
          </div>
        </div>

        {/* Analytics Multi-Metric Display */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
          
          {/* Circular Progress Banner Card */}
          <div className="ai-stat-card">
            <div style={{ position: 'relative', width: '90px', height: '90px', flexShrink: 0 }}>
              <svg width="90" height="90" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                <circle cx="50" cy="50" r={radius} fill="none" stroke="rgba(0, 0, 0, 0.05)" strokeWidth="8" />
                <circle
                  cx="50" cy="50" r={radius} fill="none"
                  stroke="url(#dashboard-cyan-gradient)"
                  strokeWidth="8" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
                />
                <defs>
                  <linearGradient id="dashboard-cyan-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0369a1" />
                    <stop offset="100%" stopColor="#0d9488" />
                  </linearGradient>
                </defs>
              </svg>
              <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 800, fontSize: '1.2rem', color: '#0f172a' }}>
                {overallProgress}%
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: '#0369a1', fontWeight: 700, textTransform: 'uppercase' }}>
                <TrendingUp size={14} />
                <span>Overall Mastery</span>
              </div>
              <div className="ai-stat-value">{totalCompleted} / {totalTasks}</div>
              <div className="ai-stat-label">Completed Curriculum Tasks</div>
            </div>
          </div>

          {/* Stat Counter 1: Active Verticals */}
          <div className="ai-stat-card">
            <div className="neon-icon-box">
              <Layers size={28} style={{ color: '#0369a1' }} />
            </div>
            <div>
              <div className="ai-stat-value">{totalVerticals}</div>
              <div className="ai-stat-label">Active Study Tracks</div>
            </div>
          </div>

          {/* Stat Counter 2: Completed Lessons */}
          <div className="ai-stat-card">
            <div className="neon-icon-box emerald">
              <CheckCircle2 size={28} style={{ color: '#059669' }} />
            </div>
            <div>
              <div className="ai-stat-value">{totalCompleted}</div>
              <div className="ai-stat-label">Completed Lessons</div>
            </div>
          </div>

          {/* Stat Counter 3: Pending Tasks */}
          <div className="ai-stat-card">
            <div className="neon-icon-box purple">
              <Clock size={28} style={{ color: '#4338ca' }} />
            </div>
            <div>
              <div className="ai-stat-value">{pendingTasks}</div>
              <div className="ai-stat-label">Pending Tasks</div>
            </div>
          </div>
        </div>
      </section>

      {/* Study Verticals Primary Grid */}
      <section style={{ marginTop: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 className="ai-gradient-text" style={{ fontSize: '1.8rem', margin: 0 }}>
              Study Verticals
            </h2>
            <p style={{ color: '#64748b', fontSize: '1rem', margin: '0.25rem 0 0' }}>
              Curated architectural tracks & hands-on engineering lab modules
            </p>
          </div>
          <button onClick={fetchVerticals} className="ai-neon-btn">
            <RefreshCw size={16} className={loading ? 'ai-spin' : ''} />
            <span>Refresh Tracks</span>
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
            <RefreshCw size={40} className="ai-spin" style={{ margin: '0 auto', color: '#0369a1', marginBottom: '1rem' }} />
            <p>Syncing neural pathways...</p>
          </div>
        ) : verticals.length === 0 ? (
          <div className="ai-glass-panel" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
            <Sparkles size={48} style={{ color: '#0369a1', margin: '0 auto 1.5rem' }} />
            <h3 style={{ fontSize: '1.5rem', color: '#0f172a', marginBottom: '0.5rem' }}>No Data Feeds Found</h3>
            <p style={{ color: '#64748b', fontSize: '1.1rem' }}>
              Initialize by adding a vertical from the command center dropdown.
            </p>
          </div>
        ) : (
          <div className="ai-grid">
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
    </div>
  );
}
