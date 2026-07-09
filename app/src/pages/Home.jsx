import { useState, useEffect, useCallback } from 'react';
import { PieChart, Pie, Cell, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import VerticalCard from '../components/VerticalCard';
import { RefreshCw, Sparkles, Target, Zap } from 'lucide-react';
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

  const totalTasks = verticals.reduce((sum, v) => sum + (v.tasks?.length || 0), 0);
  const totalCompleted = verticals.reduce((sum, v) => sum + (v.tasks?.filter(t => t.isCompleted).length || 0), 0);
  const overallProgress = totalTasks > 0 ? Math.round((totalCompleted / totalTasks) * 100) : 0;

  const radarData = [
    { subject: 'Agent Interaction', A: 90, fullMark: 100 },
    { subject: 'Prompt Engineering', A: 85, fullMark: 100 },
    { subject: 'RAG Systems', A: 60, fullMark: 100 },
    { subject: 'API Integration', A: 70, fullMark: 100 },
    { subject: 'Model Tuning', A: 80, fullMark: 100 },
    { subject: 'Infrastructure', A: 65, fullMark: 100 },
  ];

  const pieData = [
    { name: 'Completed', value: overallProgress },
    { name: 'Remaining', value: 100 - overallProgress },
  ];
  
  const PIE_COLORS = ['#38bdf8', '#1e293b']; 

  return (
    <div className="home-dashboard-dark">
      <div className="glow-orb orb-1"></div>
      <div className="glow-orb orb-2"></div>
      <div className="glow-orb orb-3"></div>

      <div className="dashboard-grid">
        {/* Predictive Study Analytics Hub */}
        <section className="dashboard-glass-panel hub-panel predictive-hub">
          <h2 className="panel-title">
            <Target className="title-icon" size={24} />
            Predictive Study Analytics Hub
          </h2>
          <div className="chart-container-pie">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={85}
                  outerRadius={110}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                  stroke="none"
                  cornerRadius={10}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="pie-center-text">
              <span className="pie-percentage">{overallProgress}%</span>
              <span className="pie-label">Mastery Achieved</span>
            </div>
          </div>
        </section>

        {/* Cross-Competence Spider Dashboard */}
        <section className="dashboard-glass-panel hub-panel spider-hub">
          <h2 className="panel-title">
            <Zap className="title-icon" size={24} />
            Cross-Competence Spider Dashboard
          </h2>
          <div className="chart-container-radar">
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#cbd5e1', fontSize: 13 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Competence"
                  dataKey="A"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  fill="#0ea5e9"
                  fillOpacity={0.4}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0' }} 
                  itemStyle={{ color: '#38bdf8' }} 
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Study Verticals */}
        <section className="dashboard-glass-panel hub-panel verticals-hub">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <Sparkles className="title-icon" size={24} />
                Study Verticals
              </h2>
            </div>
            <button onClick={fetchVerticals} className="neon-refresh-btn">
              <RefreshCw size={16} className={loading ? 'spin' : ''} />
              <span>Refresh Tracks</span>
            </button>
          </div>

          {loading ? (
             <div className="loading-state">
                <RefreshCw size={40} className="spin icon-glow" style={{ margin: '0 auto 1.5rem' }} />
                <p>Syncing neural pathways...</p>
             </div>
          ) : verticals.length === 0 ? (
            <div className="empty-state">
              <Sparkles size={48} className="icon-glow" style={{ margin: '0 auto 1.5rem' }} />
              <h3>No Data Feeds Found</h3>
              <p>Initialize by adding a vertical from the command center.</p>
            </div>
          ) : (
            <div className="verticals-grid">
              {verticals.map(vertical => (
                <div key={vertical.id} className="vertical-card-wrapper">
                  <VerticalCard
                    title={vertical.name}
                    icon={getIconByVertical(vertical.name)}
                    description={vertical.description}
                    linkTo={`/vertical/${vertical.id}`}
                    tasks={vertical.tasks || []}
                  />
                </div>
              ))}
            </div>
          )}
        </section>

        {/* AI Insights */}
        <section className="dashboard-glass-panel hub-panel insights-hub">
           <h2 className="panel-title">
             <Sparkles className="title-icon" size={24} />
             AI Insights
           </h2>
           <div className="insights-content">
             <div className="insight-card">
               <h4>Focus Needed</h4>
               <p>Your design competence is high; prioritize Agent Integration for path balance.</p>
             </div>
             <div className="insight-card">
               <h4>Consistency Forecast</h4>
               <p>Excellent. At current pace, FDE Architect path is projected for completion in 45 days.</p>
             </div>
           </div>
        </section>

      </div>
    </div>
  );
}
