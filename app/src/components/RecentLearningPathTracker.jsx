import { useEffect, useRef, useState } from 'react';
import { ArrowRight, ChevronDown, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatLastOpened } from '../utils/recentLearningPaths';
import './RecentLearningPathTracker.css';

const CLOSE_DELAY_MS = 220;

function getProgress(path) {
  const progress = Number(path.progressPercentage);
  return Number.isFinite(progress) ? Math.min(100, Math.max(0, progress)) : 0;
}

function hasLessonCount(path) {
  return Number.isFinite(Number(path.completedLessons)) && Number.isFinite(Number(path.totalLessons));
}

export default function RecentLearningPathTracker({ paths }) {
  const [isOpen, setIsOpen] = useState(false);
  const trackerRef = useRef(null);
  const triggerRef = useRef(null);
  const closeTimeoutRef = useRef(null);
  const suppressFocusRevealRef = useRef(false);
  const pointerTriggeredOpenRef = useRef(false);
  const drawerId = 'recent-learning-path-tracker-drawer';
  const activePaths = Array.isArray(paths) ? paths : [];

  const clearCloseTimeout = () => {
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
  };

  const revealDrawer = () => {
    clearCloseTimeout();
    if (suppressFocusRevealRef.current) {
      suppressFocusRevealRef.current = false;
      return;
    }
    setIsOpen(true);
  };

  const scheduleClose = () => {
    clearCloseTimeout();
    closeTimeoutRef.current = window.setTimeout(() => {
      closeTimeoutRef.current = null;
      if (trackerRef.current?.contains(document.activeElement)) return;
      pointerTriggeredOpenRef.current = false;
      setIsOpen(false);
    }, CLOSE_DELAY_MS);
  };

  const closeDrawer = (restoreFocus = false) => {
    clearCloseTimeout();
    pointerTriggeredOpenRef.current = false;
    suppressFocusRevealRef.current = restoreFocus;
    setIsOpen(false);
    if (restoreFocus) {
      if (document.activeElement === triggerRef.current) {
        suppressFocusRevealRef.current = false;
      } else {
        triggerRef.current?.focus();
      }
    }
  };

  useEffect(() => () => {
    if (closeTimeoutRef.current) window.clearTimeout(closeTimeoutRef.current);
  }, []);

  const handleFocusCapture = () => {
    revealDrawer();
  };

  const handlePointerEnter = () => {
    if (!isOpen) pointerTriggeredOpenRef.current = true;
    revealDrawer();
  };

  const handleBlurCapture = (event) => {
    if (!event.currentTarget.contains(event.relatedTarget)) scheduleClose();
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeDrawer(true);
    }
  };

  return (
    <aside
      ref={trackerRef}
      className={`recent-learning-path-tracker${isOpen ? ' is-open' : ''}`}
      aria-label="Recent learning paths"
      onFocusCapture={handleFocusCapture}
      onBlurCapture={handleBlurCapture}
      onKeyDown={handleKeyDown}
    >
      <div
        className="recent-learning-path-tracker__proximity"
        aria-hidden="true"
        onPointerEnter={handlePointerEnter}
        onPointerLeave={scheduleClose}
      />

      <div
        className="recent-learning-path-tracker__shell"
        onPointerEnter={handlePointerEnter}
        onPointerLeave={scheduleClose}
      >
        <button
          ref={triggerRef}
          type="button"
          className="recent-learning-path-tracker__trigger"
          aria-expanded={isOpen}
          aria-controls={drawerId}
          onClick={() => {
            clearCloseTimeout();
            if (pointerTriggeredOpenRef.current) {
              pointerTriggeredOpenRef.current = false;
              setIsOpen(true);
              return;
            }
            setIsOpen((open) => !open);
          }}
        >
          <span className="recent-learning-path-tracker__trigger-label">Recent paths</span>
          <span className="recent-learning-path-tracker__segments" aria-hidden="true">
            {activePaths.map((path, index) => (
              <span
                key={path.id || path.slug}
                className={`recent-learning-path-tracker__segment${index === 0 && Number.isFinite(Number(path.lastOpenedAt)) ? ' is-current' : ''}`}
                title={path.title}
              >
                <span style={{ width: `${getProgress(path)}%` }} />
              </span>
            ))}
          </span>
          <span className="recent-learning-path-tracker__count">{activePaths.length}</span>
          <ChevronDown size={15} aria-hidden="true" />
        </button>

        <section
          id={drawerId}
          className={`recent-learning-path-tracker__drawer${isOpen ? ' is-open' : ''}`}
          aria-hidden={!isOpen}
          aria-labelledby="recent-learning-path-tracker-title"
        >
          <div className="recent-learning-path-tracker__drawer-header">
            <span id="recent-learning-path-tracker-title">Recent learning paths</span>
            <button
              type="button"
              className="recent-learning-path-tracker__close"
              aria-label="Close recent learning paths"
              tabIndex={isOpen ? 0 : -1}
              onClick={() => closeDrawer(true)}
            >
              <X size={16} aria-hidden="true" />
            </button>
          </div>

          <div className="recent-learning-path-tracker__items">
            {activePaths.map((path, index) => {
              const progress = getProgress(path);
              const isCurrent = index === 0 && Number.isFinite(Number(path.lastOpenedAt)) && Number(path.lastOpenedAt) > 0;

              return (
                <Link
                  key={path.id || path.slug}
                  to={`/chapters/${path.slug}`}
                  className={`recent-learning-path-tracker__item${isCurrent ? ' is-current' : ''}`}
                  tabIndex={isOpen ? 0 : -1}
                  title={path.title}
                >
                  <div className="recent-learning-path-tracker__item-title-row">
                    <h3>{path.title}</h3>
                    {isCurrent && <span className="recent-learning-path-tracker__current-label">Current</span>}
                  </div>
                  <div className="recent-learning-path-tracker__item-meta">
                    <span>{formatLastOpened(path.lastOpenedAt)}</span>
                    <strong>{progress}%</strong>
                  </div>
                  <div
                    className="recent-learning-path-tracker__progress"
                    role="progressbar"
                    aria-label={`${path.title} progress`}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={progress}
                  >
                    <span style={{ width: `${progress}%` }} />
                  </div>
                  <div className="recent-learning-path-tracker__item-footer">
                    {hasLessonCount(path) ? (
                      <span>{path.completedLessons} / {path.totalLessons} lessons</span>
                    ) : <span>Progress from live pathway</span>}
                    {isCurrent && <span className="recent-learning-path-tracker__resume">Resume <ArrowRight size={13} aria-hidden="true" /></span>}
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

      </div>
    </aside>
  );
}
