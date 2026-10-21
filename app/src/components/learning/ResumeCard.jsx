import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookmarkCheck } from 'lucide-react';
import { api } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { timeAgo } from '../../utils/timeAgo';
import './ResumeCard.css';

function lessonHref(lesson) {
  const hash = lesson.lastSectionId ? `#${encodeURIComponent(lesson.lastSectionId)}` : '';
  return `/chapter/${lesson.fullSlug}${hash}`;
}

/**
 * "Continue where you left off" card, shown only to signed-in learners who have a
 * resume point. If the last lesson is finished, it also offers the next lesson.
 */
export default function ResumeCard() {
  const { isAuthenticated } = useAuth();
  const [resume, setResume] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setResume(null);
      return undefined;
    }

    let cancelled = false;
    api.me.resume()
      .then((data) => {
        if (!cancelled) setResume(data || null);
      })
      .catch(() => {
        if (!cancelled) setResume(null);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  const lastLesson = resume?.lastLesson;
  if (!isAuthenticated || !lastLesson?.fullSlug) return null;

  const nextLesson = resume?.nextLesson;
  const lastIsCompleted = lastLesson.status === 'Completed';
  const showNext = lastIsCompleted && nextLesson?.fullSlug;

  return (
    <section className="resume-card" aria-labelledby="resume-card-title">
      <div className="resume-card__main">
        <span className="resume-card__kicker">
          <BookmarkCheck size={14} aria-hidden="true" /> Continue where you left off
        </span>
        <h2 id="resume-card-title" className="resume-card__title">{lastLesson.title}</h2>
        <p className="resume-card__meta">
          <span>{lastLesson.courseTitle}</span>
          <span aria-hidden="true">›</span>
          <span>{lastLesson.moduleTitle}</span>
          {lastLesson.lastOpenedAt && (
            <>
              <span aria-hidden="true">·</span>
              <span>Opened {timeAgo(lastLesson.lastOpenedAt)}</span>
            </>
          )}
          {lastIsCompleted && <span className="resume-card__done">Completed</span>}
        </p>
        {!lastIsCompleted && lastLesson.scrollPercent > 0 && (
          <div className="resume-card__progress" aria-label={`${lastLesson.scrollPercent}% read`}>
            <span style={{ width: `${Math.min(100, lastLesson.scrollPercent)}%` }} />
          </div>
        )}
      </div>

      <div className="resume-card__actions">
        <Link to={lessonHref(lastLesson)} className={showNext ? 'resume-card__btn resume-card__btn--quiet' : 'resume-card__btn'}>
          {lastIsCompleted ? 'Review chapter' : 'Resume reading'} <ArrowRight size={15} />
        </Link>
        {showNext && (
          <Link to={`/chapter/${nextLesson.fullSlug}`} className="resume-card__btn">
            Next: {nextLesson.title} <ArrowRight size={15} />
          </Link>
        )}
      </div>
    </section>
  );
}
