import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatLastOpened } from '../utils/recentLearningPaths';
import './CompactLearningPathways.css';

function getProgress(path) {
  const progress = Number(path.progressPercentage);
  return Number.isFinite(progress) ? Math.min(100, Math.max(0, progress)) : 0;
}

function hasLessonCount(path) {
  return Number.isFinite(Number(path.completedLessons)) && Number.isFinite(Number(path.totalLessons));
}

export default function CompactLearningPathways({ paths }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const contentId = 'compact-learning-pathways-content';
  const activePaths = Array.isArray(paths) ? paths : [];

  return (
    <section className="compact-learning-pathways" aria-labelledby="compact-learning-pathways-heading">
      <div className="compact-learning-pathways__header">
        <h2 id="compact-learning-pathways-heading">Curriculum Learning Pathways</h2>
        <button
          type="button"
          className="compact-learning-pathways__toggle"
          aria-expanded={isExpanded}
          aria-controls={contentId}
          onClick={() => setIsExpanded((expanded) => !expanded)}
        >
          <span>{activePaths.length} active tracks</span>
          <ChevronDown size={18} aria-hidden="true" />
        </button>
      </div>

      <div
        id={contentId}
        className="compact-learning-pathways__content"
        hidden={!isExpanded}
      >
        <div className="compact-learning-pathways__row" aria-label="Active curriculum pathways">
          {activePaths.map((path, index) => {
            const progress = getProgress(path);
            const isCurrent = index === 0 && Number.isFinite(Number(path.lastOpenedAt)) && Number(path.lastOpenedAt) > 0;

            return (
              <Link
                key={path.id || path.slug}
                to={`/chapters/${path.slug}`}
                className={`compact-learning-pathways__cell${isCurrent ? ' is-current' : ''}`}
                title={path.title}
              >
                <div className="compact-learning-pathways__cell-topline">
                  <span className="compact-learning-pathways__cell-title">{path.title}</span>
                  <span className="compact-learning-pathways__cell-progress">{progress}%</span>
                </div>
                {isCurrent && <span className="compact-learning-pathways__current-label">Current · {formatLastOpened(path.lastOpenedAt)}</span>}
                {hasLessonCount(path) && (
                  <span className="compact-learning-pathways__lesson-count">
                    {path.completedLessons} / {path.totalLessons} lessons
                  </span>
                )}
                <span className="compact-learning-pathways__progress-track" aria-hidden="true">
                  <span style={{ width: `${progress}%` }} />
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}

