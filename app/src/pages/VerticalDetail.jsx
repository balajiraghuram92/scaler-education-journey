import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BookOpen, Award, CheckCircle2, ChevronRight, LayoutGrid } from 'lucide-react';

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

    const modules = Object.keys(modulesMap).map(name => {
      const tasks = modulesMap[name];
      const total = tasks.length;
      const completed = tasks.filter(t => t.isCompleted).length;
      const progress = total > 0 ? (completed / total) * 100 : 0;
      const { badge, title } = getModuleBadgeAndTitle(name);
      return { fullName: name, badge, title, tasks, total, completed, progress };
    });

    const activeModObj = modules.find(m => m.fullName === activeModule);

    return (
      <div className="container mt-md">
        <Link to="/" className="btn btn-secondary mb-lg">
          ← Back to Dashboard
        </Link>

        <div className="fde-dashboard">
          {/* Header/Stats Grid */}
          <div className="fde-stats-grid">
            <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <span className="module-card__badge" style={{ fontSize: '0.9rem' }}>Scaler Curriculum</span>
              <h1 className="gradient-text mb-sm" style={{ fontSize: '2.4rem' }}>FDE & Agentic AI Track</h1>
              <p className="text-secondary mb-md">
                Follow along the 8 specializations spanning Python foundations, backend tracing, React streaming UIs, cloud-native deployments, LLM evaluation, and agentic workflows.
              </p>
              <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                <div className="glass-panel" style={{ padding: 'var(--space-sm) var(--space-md)', flex: 1, textAlign: 'center' }}>
                  <h3 className="gradient-text">{completedTasks}</h3>
                  <span className="text-muted" style={{ fontSize: '0.85rem' }}>Completed classes</span>
                </div>
                <div className="glass-panel" style={{ padding: 'var(--space-sm) var(--space-md)', flex: 1, textAlign: 'center' }}>
                  <h3 style={{ color: 'var(--accent-emerald)' }}>{totalTasks - completedTasks}</h3>
                  <span className="text-muted" style={{ fontSize: '0.85rem' }}>Pending classes</span>
                </div>
              </div>
            </div>

            <div className="glass-panel fde-main-progress-card">
              <div className="circular-progress-wrapper">
                <svg className="circular-progress-svg" viewBox="0 0 100 100">
                  <defs>
                    <linearGradient id="cyan-purple-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="var(--accent-cyan)" />
                      <stop offset="100%" stopColor="var(--accent-purple)" />
                    </linearGradient>
                  </defs>
                  <circle className="circular-progress-bg" cx="50" cy="50" r="42" />
                  <circle
                    className="circular-progress-bar"
                    cx="50"
                    cy="50"
                    r="42"
                    strokeDasharray={2 * Math.PI * 42}
                    strokeDashoffset={2 * Math.PI * 42 * (1 - overallProgress / 100)}
                  />
                </svg>
                <div className="circular-progress-text">{Math.round(overallProgress)}%</div>
              </div>
              <h4 className="gradient-text">Overall Syllabus</h4>
              <span className="text-muted" style={{ fontSize: '0.85rem' }}>{completedTasks} / {totalTasks} topics done</span>
            </div>
          </div>

          {/* Modules Grid */}
          <div>
            <h2 className="mb-md" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
              <LayoutGrid size={22} style={{ color: 'var(--accent-cyan)' }} /> Specializations
            </h2>
            <div className="modules-grid">
              {modules.map((mod, i) => (
                <div
                  key={i}
                  className={`module-card ${activeModule === mod.fullName ? 'module-card--active' : ''}`}
                  onClick={() => setActiveModule(mod.fullName)}
                >
                  <div>
                    <div className="module-card__badge">{mod.badge}</div>
                    <div className="module-card__title">{mod.title}</div>
                  </div>
                  <div className="module-card__footer">
                    <span className="module-card__progress-text">
                      {mod.completed}/{mod.total} Done
                    </span>
                    <div className="module-card__mini-ring">
                      <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                        <circle fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" cx="18" cy="18" r="14" />
                        <circle
                          fill="none"
                          stroke={mod.progress === 100 ? 'var(--accent-emerald)' : 'var(--accent-cyan)'}
                          strokeWidth="3"
                          strokeLinecap="round"
                          cx="18"
                          cy="18"
                          r="14"
                          strokeDasharray={2 * Math.PI * 14}
                          strokeDashoffset={2 * Math.PI * 14 * (1 - mod.progress / 100)}
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Module View */}
          {activeModObj && (
            <div className="module-drawer">
              <div className="module-drawer__header">
                <div>
                  <span className="module-card__badge">{activeModObj.badge}</span>
                  <h3 className="module-drawer__title">{activeModObj.title}</h3>
                </div>
                <span className="text-secondary" style={{ fontWeight: 600 }}>
                  {activeModObj.completed} of {activeModObj.total} Completed
                </span>
              </div>

              <div className="module-drawer__progress-bar">
                <div
                  className="module-drawer__progress-fill"
                  style={{ width: `${activeModObj.progress}%` }}
                />
              </div>

              <div className="module-drawer__tasks">
                {activeModObj.tasks.map(task => (
                  <div
                    key={task.id}
                    className={`drawer-task-row ${task.isCompleted ? 'drawer-task-row--completed' : ''}`}
                    onClick={() => toggleTask(task.id)}
                  >
                    <div className="drawer-task-row__checkbox">
                      {task.isCompleted && <CheckCircle2 size={16} style={{ color: '#0a0a0f' }} />}
                    </div>
                    <span className="drawer-task-row__title">{task.title}</span>
                    <ChevronRight size={18} className="opacity-50" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Fallback UI for other verticals (unchanged)
  return (
    <div className="container mt-md">
      <div className="glass-panel vertical-detail__header">
        <h1 className="gradient-text mb-md vertical-detail__title">
          {vertical.name}
        </h1>
        <p className="text-secondary vertical-detail__description">
          {vertical.description}
        </p>
        {totalTasks > 0 && (
          <div className="vertical-detail__master-progress">
            <div className="vertical-detail__master-progress-header">
              <span className="vertical-detail__master-progress-label">Total Progress</span>
              <span className="vertical-detail__master-progress-value">
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
        <Link to="/" className="btn btn-secondary vertical-detail__back-btn mt-md">
          ← Back to Verticals
        </Link>
      </div>

      <section className="mt-xl vertical-detail__tasks-section">
        <h2 className="mb-lg vertical-detail__tasks-title">
          Tasks <span className="text-secondary">({completedTasks}/{totalTasks} completed)</span>
        </h2>
        <div className="vertical-detail__tasks-list">
          {vertical.tasks.length === 0 ? (
            <p className="text-secondary">No tasks yet</p>
          ) : (
            vertical.tasks.map(task => (
              <div
                key={task.id}
                className={`glass-panel vertical-task ${task.isCompleted ? 'vertical-task--completed' : ''}`}
                onClick={() => toggleTask(task.id)}
              >
                <div className="vertical-task__checkmark">
                  {task.isCompleted && (
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="white"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </div>
                <span className="vertical-task__title">{task.title}</span>
                {task.isCompleted && (
                  <span className="vertical-task__badge">✓ Done</span>
                )}
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
