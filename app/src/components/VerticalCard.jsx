import { Link } from 'react-router-dom';
import { Server, Cloud, BrainCircuit, Grid3x3 } from 'lucide-react';

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
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  return (
    <article className="glass-panel vertical-card">
      {/* Icon */}
      <div className="glow-effect vertical-card__icon">
        <Icon size={28} />
      </div>

      {/* Title */}
      <h3 className="vertical-card__title">{title}</h3>

      {/* Description */}
      <p className="vertical-card__description">{description}</p>

      {/* Progress Bar */}
      {totalTasks > 0 && (
        <div className="vertical-card__progress">
          <div className="vertical-card__progress-header">
            <span className="vertical-card__progress-label">Progress</span>
            <span className="vertical-card__progress-value">{Math.round(progress)}%</span>
          </div>
          <div className="vertical-card__progress-track">
            <div
              className="vertical-card__progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Button */}
      <Link to={linkTo} className="btn btn-secondary vertical-card__btn">
        View Details
      </Link>
    </article>
  );
}
