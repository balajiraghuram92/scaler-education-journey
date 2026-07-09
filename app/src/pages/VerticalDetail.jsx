import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle2, ChevronRight, LayoutGrid } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, AreaChart, Area } from 'recharts';
import './VerticalDetail.css';

export default function VerticalDetail() {
  const { id } = useParams();
  const [vertical, setVertical] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeModule, setActiveModule] = useState(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/verticals`)
      .then(res => res.json())
      .then(data => {
        const found = data.find(v => v.id === parseInt(id));
        setVertical(found);

        // Default active module to first module for modular tracks
        const isModular = found && (found.layoutMode === "Modular" || (found.tasks && found.tasks.some(t => t.module && t.module !== "General" && t.module !== "Flat")));
        if (found && isModular && found.tasks.length > 0) {
          const firstMod = found.tasks[0].module || "Prerequisite: Agentic AI Core";
          setActiveModule(firstMod);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch vertical:', err);
        setLoading(false);
      });
  }, [id]);

  const toggleTask = async (taskId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/tasks/${taskId}/toggle`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
      });
      const updatedTask = await response.json();

      setVertical(prev => {
        if (!prev) return null;
        return {
          ...prev,
          tasks: prev.tasks.map(t =>
            t.id === taskId ? { ...t, isCompleted: updatedTask.isCompleted } : t
          ),
        };
      });
    } catch (err) {
      console.error('Failed to toggle task:', err);
    }
  };

  if (loading) return <div className="container mt-xl"><p className="text-secondary">Loading...</p></div>;
  if (!vertical) return <div className="container mt-xl"><p className="text-secondary">Vertical not found</p></div>;

  const totalTasks = vertical.tasks.length;
  const completedTasks = vertical.tasks.filter(t => t.isCompleted).length;
  const overallProgress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  const isModular = vertical.layoutMode === "Modular" || (vertical.tasks && vertical.tasks.some(t => t.module && t.module !== "General" && t.module !== "Flat"));
  
  if (isModular) {
    // Group tasks by module
    const modulesMap = {};
    vertical.tasks.forEach(task => {
      const mod = task.module || 'Prerequisite: Agentic AI Core';
      if (!modulesMap[mod]) {
        modulesMap[mod] = [];
      }
      modulesMap[mod].push(task);
    });

    const getModuleBadgeAndTitle = (moduleName) => {
      if (moduleName.startsWith('Prerequisite:')) {
        return {
          badge: 'Prerequisite',
          title: moduleName.replace('Prerequisite:', '').trim()
        };
      }
      const match = moduleName.match(/^(\d+)\.\s*(.+)$/);
      if (match) {
        return {
          badge: `Module ${match[1]}`,
          title: match[2].trim()
        };
      }
      return {
        badge: 'Special',
        title: moduleName
      };
    };

    const modules = Object.keys(modulesMap).map((name, idx) => {
      const tasks = modulesMap[name];
      const total = tasks.length;
      const completed = tasks.filter(t => t.isCompleted).length;
      const progress = total > 0 ? (completed / total) * 100 : 0;
      const { badge, title } = getModuleBadgeAndTitle(name);
      
      // Generate some deterministic mock trend data for the area chart
      const trendData = Array.from({ length: 8 }, (_, i) => ({
        name: i,
        uv: 20 + Math.abs(Math.sin((idx + 1) * i)) * 60 + (progress * 0.2)
      }));

      return { fullName: name, badge, title, tasks, total, completed, progress, trendData };
    });

    const activeModObj = modules.find(m => m.fullName === activeModule);

    // Prepare radar data based on modules
    const radarData = modules.slice(0, 6).map(mod => ({
      subject: mod.title.split(' ')[0], // Take first word for radar chart axis
      A: Math.max(mod.progress, 15), // Ensure at least some visibility
      fullMark: 100
    }));

    return (
      <div className="vertical-detail-wrapper">
        <div className="container mt-md">
          <Link to="/" className="btn btn-secondary mb-lg">
            ← Back to Dashboard
          </Link>

          <div className="fde-dashboard">
            {/* Header */}
            <div className="hero-section text-center mb-xl">
              <span className="hero-badge glow-effect">🚀 IN DEVELOPMENT</span>
              <h1 className="hero-title gradient-text mt-sm">Lab Projects</h1>
              <p className="hero-subtitle text-secondary mt-sm">
                Crafting next-generation applications. A showcase of architectural excellence using <strong style={{color: '#fff'}}>React Frontend</strong> and <strong style={{color: '#fff'}}>.NET Backend</strong>.
              </p>
            </div>

            {/* Top Dashboard Row */}
            <div className="dashboard-top-row">
              {/* Overall Maturity Dials */}
              <div className="glass-panel maturity-panel">
                <h3 className="panel-title mb-lg">Core Architectural Maturity</h3>
                
                <div className="dials-container">
                  <div className="dial-wrapper">
                    <div className="circular-progress-wrapper dial-large">
                      <svg className="circular-progress-svg" viewBox="0 0 100 100">
                        <circle className="circular-progress-bg" cx="50" cy="50" r="42" />
                        <circle
                          className="circular-progress-bar"
                          cx="50"
                          cy="50"
                          r="42"
                          strokeDasharray={2 * Math.PI * 42}
                          strokeDashoffset={2 * Math.PI * 42 * (1 - (overallProgress / 100))}
                        />
                      </svg>
                      <div className="circular-progress-text">
                        {(overallProgress / 20).toFixed(1)}<span className="text-sm">/5</span>
                      </div>
                    </div>
                    <span className="dial-label">Pattern Adherence Score</span>
                  </div>

                  <div className="dial-wrapper">
                    <div className="circular-progress-wrapper dial-small">
                      <svg className="circular-progress-svg" viewBox="0 0 100 100">
                        <circle className="circular-progress-bg" cx="50" cy="50" r="42" />
                        <circle
                          className="circular-progress-bar bar-purple"
                          cx="50"
                          cy="50"
                          r="42"
                          strokeDasharray={2 * Math.PI * 42}
                          strokeDashoffset={2 * Math.PI * 42 * (1 - overallProgress / 100)}
                        />
                      </svg>
                      <div className="circular-progress-text">
                        {Math.round(overallProgress)}%
                      </div>
                    </div>
                    <span className="dial-label">Projected Next Milestone: <br/><strong style={{color:'#fff'}}>12 Days</strong></span>
                  </div>
                </div>
              </div>

              {/* FDE Track Competence Balance (Radar Chart) */}
              <div className="glass-panel radar-panel">
                <h3 className="panel-title mb-md">Codebase Pattern Maturity & Architecture</h3>
                <div className="radar-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                      <PolarGrid stroke="rgba(255,255,255,0.15)" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar name="Competence" dataKey="A" stroke="var(--accent-cyan)" fill="var(--accent-cyan)" fillOpacity={0.3} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Modules Grid */}
            <div className="specializations-section mt-xl">
              <h2 className="section-title mb-lg d-flex align-items-center">
                <LayoutGrid size={24} className="mr-sm text-accent" /> Specializations
              </h2>
              <div className="specializations-grid">
                {modules.map((mod, i) => (
                  <div
                    key={i}
                    className={`glass-panel spec-card ${activeModule === mod.fullName ? 'spec-card--active' : ''}`}
                    onClick={() => setActiveModule(mod.fullName)}
                  >
                    <div className="spec-card-content">
                      <div className="spec-card-header">
                        <span className="spec-badge">{mod.badge}</span>
                        <h4 className="spec-title">{mod.title}</h4>
                      </div>
                      
                      <div className="spec-card-trend mt-sm">
                        <ResponsiveContainer width="100%" height={60}>
                          <AreaChart data={mod.trendData}>
                            <defs>
                              <linearGradient id={`colorUv${i}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={activeModule === mod.fullName ? "var(--accent-purple)" : "var(--accent-cyan)"} stopOpacity={0.6}/>
                                <stop offset="95%" stopColor={activeModule === mod.fullName ? "var(--accent-purple)" : "var(--accent-cyan)"} stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="uv" stroke={activeModule === mod.fullName ? "var(--accent-purple)" : "var(--accent-cyan)"} fillOpacity={1} fill={`url(#colorUv${i})`} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>

                      <div className="spec-card-footer mt-md">
                        <span className="spec-progress-text">
                          {mod.completed}/{mod.total} Modules Done
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Detailed Module View */}
            {activeModObj && (
              <div className="glass-panel module-drawer mt-lg">
                <div className="module-drawer__header">
                  <div>
                    <span className="spec-badge glow-effect">{activeModObj.badge}</span>
                    <h3 className="module-drawer__title mt-sm">{activeModObj.title}</h3>
                  </div>
                  <div className="module-drawer__stats text-right">
                    <span className="text-accent text-lg" style={{ fontWeight: 700 }}>
                      {Math.round(activeModObj.progress)}%
                    </span>
                    <span className="text-secondary d-block" style={{ fontSize: '0.85rem' }}>
                      Skill Depth
                    </span>
                  </div>
                </div>

                <div className="module-drawer__tasks mt-lg">
                  {activeModObj.tasks.map(task => (
                    <div
                      key={task.id}
                      className={`drawer-task-row ${task.isCompleted ? 'drawer-task-row--completed' : ''}`}
                      onClick={() => toggleTask(task.id)}
                    >
                      <div className="drawer-task-row__checkbox">
                        {task.isCompleted && <CheckCircle2 size={16} className="text-accent" />}
                      </div>
                      
                      <div className="drawer-task-row__content">
                        <span className="drawer-task-row__title">{task.title}</span>
                        {/* Skill Depth progress bar */}
                        <div className="skill-depth-container mt-xs">
                          <span className="skill-depth-label">Skill Depth</span>
                          <div className="skill-depth-track">
                            <div className="skill-depth-fill" style={{ width: task.isCompleted ? '100%' : '20%' }}></div>
                          </div>
                        </div>
                      </div>

                      <ChevronRight size={20} className="text-secondary opacity-50" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Fallback UI for other verticals
  return (
    <div className="container mt-md">
      <div className="glass-panel vertical-detail__header text-center">
        <h1 className="gradient-text mb-md vertical-detail__title">
          {vertical.name}
        </h1>
        <p className="text-secondary vertical-detail__description">
          {vertical.description}
        </p>
        {totalTasks > 0 && (
          <div className="vertical-detail__master-progress mx-auto mt-lg">
            <div className="vertical-detail__master-progress-header d-flex justify-content-between mb-sm">
              <span className="vertical-detail__master-progress-label font-weight-bold">Total Progress</span>
              <span className="vertical-detail__master-progress-value text-accent">
                {Math.round(overallProgress)}% ({completedTasks}/{totalTasks})
              </span>
            </div>
            <div className="vertical-detail__master-progress-track">
              <div
                className="vertical-detail__master-progress-fill"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
          </div>
        )}
        <Link to="/" className="btn btn-secondary mt-lg">
          ← Back to Verticals
        </Link>
      </div>

      <section className="mt-xl">
        <h2 className="mb-lg d-flex align-items-center">
          Tasks <span className="text-secondary ml-sm" style={{fontSize: '1.2rem', fontWeight: 500}}>({completedTasks}/{totalTasks} completed)</span>
        </h2>
        <div className="d-flex flex-column gap-md">
          {vertical.tasks.length === 0 ? (
            <p className="text-secondary">No tasks yet</p>
          ) : (
            vertical.tasks.map(task => (
              <div
                key={task.id}
                className={`glass-panel drawer-task-row ${task.isCompleted ? 'drawer-task-row--completed' : ''}`}
                onClick={() => toggleTask(task.id)}
                style={{ padding: '1.2rem' }}
              >
                <div className="drawer-task-row__checkbox">
                  {task.isCompleted && <CheckCircle2 size={18} className="text-accent" />}
                </div>
                <span className="drawer-task-row__title" style={{ fontSize: '1.1rem' }}>{task.title}</span>
                {task.isCompleted && (
                  <span className="text-accent font-weight-bold" style={{ fontSize: '0.85rem', textTransform: 'uppercase' }}>✓ Done</span>
                )}
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
