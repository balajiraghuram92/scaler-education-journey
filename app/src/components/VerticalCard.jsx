import { Link } from 'react-router-dom';
import { Server, Cloud, BrainCircuit, Grid3x3, ArrowRight, CheckCircle2, Clock, PlayCircle } from 'lucide-react';

export default function VerticalCard({ title, icon: IconName, description, linkTo, tasks = [] }) {
  const iconMap = {
    server: Server,
    cloud: Cloud,
    'brain-circuit': BrainCircuit,
    'grid-3x3': Grid3x3,
  };
  
  const Icon = iconMap[IconName] || Grid3x3;

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.isCompleted).length;
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const getStatusBadge = () => {
    if (totalTasks === 0) return { label: 'Custom Track', color: 'var(--text-muted)', bg: 'rgba(255, 255, 255, 0.05)', icon: Clock };
    if (progress === 100) return { label: 'Completed', color: 'var(--accent-emerald)', bg: 'rgba(0, 255, 157, 0.1)', icon: CheckCircle2 };
    if (progress > 0) return { label: 'In Progress', color: 'var(--accent-cyan)', bg: 'rgba(0, 240, 255, 0.1)', icon: PlayCircle };
    return { label: 'Ready to Start', color: 'var(--accent-purple)', bg: 'rgba(123, 47, 247, 0.15)', icon: Clock };
  };

  const badge = getStatusBadge();
  const BadgeIcon = badge.icon;

  return (
    <article className="glass-panel vertical-card" style={{ position: 'relative', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Top Header Row with Icon and Badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-md)' }}>
        <div className="glow-effect vertical-card__icon">
          <Icon size={28} />
        </div>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '0.25rem 0.6rem',
            borderRadius: 'var(--radius-full)',
            background: badge.bg,
            border: `1px solid ${badge.color}40`,
            color: badge.color,
            fontSize: '0.75rem',
            fontWeight: '600'
          }}
        >
          <BadgeIcon size={12} />
          <span>{badge.label}</span>
        </div>
      </div>

      {/* Title & Description */}
      <h3 className="vertical-card__title" style={{ fontSize: '1.25rem', marginBottom: 'var(--space-xs)' }}>
        {title}
      </h3>
      <p className="vertical-card__description" style={{ flex: 1, marginBottom: 'var(--space-md)' }}>
        {description}
      </p>

      {/* Enhanced Progress Bar & Stat Details */}
      <div className="vertical-card__progress" style={{ marginBottom: 'var(--space-lg)' }}>
        <div className="vertical-card__progress-header">
          <span className="vertical-card__progress-label">
            {completedTasks} / {totalTasks} Lessons
          </span>
          <span className="vertical-card__progress-value">{progress}%</span>
        </div>
        <div className="vertical-card__progress-track" style={{ height: '8px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: 'var(--radius-full)' }}>
          <div
            className="vertical-card__progress-fill"
            style={{
              width: `${progress}%`,
              background: progress === 100 
                ? 'var(--accent-emerald)' 
                : 'linear-gradient(90deg, var(--accent-cyan), var(--accent-purple))',
              borderRadius: 'var(--radius-full)'
            }}
          />
        </div>
      </div>

      {/* Navigation Button */}
      <Link to={linkTo} className="btn btn-secondary vertical-card__btn" style={{ width: '100%', justifyContent: 'center' }}>
        <span>View Track Details</span>
        <ArrowRight size={16} />
      </Link>
    </article>
  );
}
