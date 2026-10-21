import { useCallback, useEffect, useState } from 'react';
import { ArrowRight, BookOpen, Clock3, Compass, Layers3, Route } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { EmptyState, ErrorState, LoadingState } from '../components/common/StateViews';
import ResumeCard from '../components/learning/ResumeCard';
import { pathwayCatalog } from '../content/curriculumCatalog';
import './ChaptersIndex.css';

export default function ChaptersIndex() {
  const [learningPaths, setLearningPaths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLearningPaths = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const paths = await api.v2.getLearningPaths();
      setLearningPaths(Array.isArray(paths) ? paths : []);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLearningPaths();
  }, [fetchLearningPaths]);

  if (loading) return <LoadingState message="Opening curriculum library..." />;
  if (error) return <ErrorState error={error} onRetry={fetchLearningPaths} title="Chapters Temporarily Unavailable" />;

  const activeSlugs = new Set(learningPaths.map((path) => path.slug));
  const plannedPathways = pathwayCatalog.filter((path) => !activeSlugs.has(path.slug));

  return (
    <div className="chapters-index-page">
      <header className="chapters-index-hero">
        <div className="chapters-index-heading">
          <span className="chapters-index-eyebrow">Curriculum library</span>
          <h1 className="chapters-index-title">Learning pathways</h1>
          <p className="chapters-index-description">
            Follow a complete engineering path, or return to the precise lesson that moves your work forward today.
          </p>
        </div>
        <div className="chapters-index-hero-note">
          <Compass size={19} strokeWidth={1.7} />
          <div>
            <span className="chapters-index-hero-note-label">Designed for deliberate progress</span>
            <span className="chapters-index-hero-note-copy">Your completed chapters travel with you across related pathways.</span>
          </div>
        </div>
      </header>

      <ResumeCard />

      <section className="chapters-library-section" aria-labelledby="active-pathways-heading">
        <div className="chapters-section-heading">
          <div>
            <span className="chapters-section-kicker">Ready to explore</span>
            <h2 id="active-pathways-heading">Active pathways</h2>
          </div>
          <div className="chapters-index-count">
            <BookOpen size={15} />
            <span>{learningPaths.length} active</span>
          </div>
        </div>

        {learningPaths.length > 0 ? (
          <div className="chapters-track-grid" aria-label="Active curriculum pathways">
            {learningPaths.map((path) => (
              <Link key={path.id} to={`/chapters/${path.slug}`} className="chapters-track-card">
                <div className="chapters-track-card-topline">
                  <span className="chapters-track-type">{path.pathType || 'Curriculum'}</span>
                  <span className="chapters-track-progress">{path.progressPercentage}%</span>
                </div>

                <h3 className="chapters-track-title">{path.title}</h3>
                <p className="chapters-track-description">{path.description}</p>

                <div className="chapters-track-meta">
                  <span>{path.completedLessons} of {path.totalLessons} lessons completed</span>
                  <span>{path.modules?.length || 0} modules</span>
                </div>

                <div className="chapters-track-progress-bar" aria-hidden="true">
                  <span style={{ width: `${path.progressPercentage}%` }} />
                </div>

                <div className="chapters-track-action">
                  <span>{path.completedLessons > 0 ? 'Continue pathway' : 'Open pathway'}</span>
                  <ArrowRight size={16} />
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState message="The first curriculum pathway is being prepared." />
        )}
      </section>

      <section className="chapters-library-section chapters-planned-section" aria-labelledby="planned-pathways-heading">
        <div className="chapters-section-heading">
          <div>
            <span className="chapters-section-kicker">On the atlas</span>
            <h2 id="planned-pathways-heading">Planned pathways</h2>
          </div>
          <div className="chapters-planned-caption">
            <Layers3 size={15} />
            <span>Focused paths, released as their chapter libraries are ready</span>
          </div>
        </div>

        <div className="chapters-planned-grid" aria-label="Planned curriculum pathways">
          {plannedPathways.map((path) => (
            <article key={path.slug} className={`chapters-planned-card chapters-planned-card--${path.accent}`}>
              <div className="chapters-planned-card-topline">
                <span className="chapters-planned-status"><Clock3 size={13} />{path.label}</span>
                <Route size={17} strokeWidth={1.6} aria-hidden="true" />
              </div>
              <h3>{path.title}</h3>
              <p>{path.description}</p>
              <ul className="chapters-focus-list" aria-label={`${path.title} focus areas`}>
                {path.focusAreas.map((area) => <li key={area}>{area}</li>)}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
