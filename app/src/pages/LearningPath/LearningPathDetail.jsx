import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';
import { markLearningPathOpened } from '../../utils/recentLearningPaths';

export default function LearningPathDetail() {
  const { slug } = useParams();
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPath = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.v2.getLearningPath(slug);
      setPath(data);
      if (data && typeof data.slug === 'string' && data.slug.trim()) {
        markLearningPathOpened(data.slug);
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPath();
  }, [slug]);

  if (loading) return <LoadingState message={`Opening ${slug} pathway...`} />;
  if (error) return <ErrorState error={error} onRetry={fetchPath} title="Failed to Load Pathway" />;
  if (!path) return <EmptyState message="Learning path not found." />;

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      {/* Breadcrumb Header */}
      <div style={{ marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--color-ink-muted, #6B7280)' }}>
        <Link to="/chapters" style={{ color: 'var(--color-sage, #2C5E55)', textDecoration: 'none' }}>Chapters</Link>
        <span style={{ margin: '0 0.5rem' }}>/</span>
        <span style={{ color: 'var(--color-ink, #1F2937)', fontWeight: '500' }}>{path.title}</span>
      </div>

      {/* Hero Card */}
      <div style={{
        backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
        border: '1px solid var(--color-border-subtle, #E2DDD5)',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 20px rgba(0,0,0,0.03)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span style={{
                backgroundColor: 'rgba(44, 94, 85, 0.1)',
                color: 'var(--color-sage, #2C5E55)',
                padding: '0.2rem 0.6rem',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '700',
                textTransform: 'uppercase'
              }}>
                {path.pathType}
              </span>
            </div>
            <h1 style={{
              fontFamily: 'var(--font-serif, "Newsreader", serif)',
              fontSize: '2.25rem',
              color: 'var(--color-ink, #1F2937)',
              margin: '0 0 0.75rem 0'
            }}>
              {path.title}
            </h1>
            <p style={{ color: 'var(--color-ink-muted, #6B7280)', lineHeight: '1.6', maxWidth: '700px', margin: 0 }}>
              {path.description}
            </p>
          </div>

          <div style={{ minWidth: '160px', textAlign: 'right' }}>
            <div style={{ fontSize: '1.75rem', fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
              {path.progressPercentage}%
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
              {path.completedLessons} of {path.totalLessons} lessons completed
            </div>
            <div style={{
              width: '100%',
              height: '6px',
              backgroundColor: '#E5E7EB',
              borderRadius: '3px',
              marginTop: '0.5rem',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${path.progressPercentage}%`,
                height: '100%',
                backgroundColor: 'var(--color-sage, #2C5E55)',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>
        </div>
      </div>

      {/* Modules & Lessons Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {path.modules?.map((module, idx) => {
          const totalCount = module.lessons?.length || 0;
          const completedCount = module.lessons?.filter((lesson) => lesson.isCompleted).length || 0;
          const nextLesson = module.lessons?.find((lesson) => !lesson.isCompleted) || null;

          return (
            <div key={module.id} style={{
              backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
              border: '1px solid var(--color-border-subtle, #E2DDD5)',
              borderRadius: '10px',
              overflow: 'hidden'
            }}>
              <div style={{
                padding: '1.25rem 1.5rem',
                backgroundColor: 'rgba(0,0,0,0.015)',
                borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>
                    Module {idx + 1}
                  </span>
                  <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: 'var(--color-ink, #1F2937)' }}>
                    {module.title}
                  </h3>
                </div>
                <span style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                  {completedCount} of {totalCount} lessons completed
                </span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
                gap: '1rem',
                padding: '1.5rem'
              }}>
                {module.lessons?.map((lesson) => {
                  const isNextUp = nextLesson !== null && lesson.id === nextLesson.id;

                  return (
                    <Link
                      key={lesson.id}
                      to={`/chapter/${path.slug}/${module.slug}/${lesson.slug}`}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem',
                        padding: '1rem',
                        minHeight: '140px',
                        borderRadius: '10px',
                        border: isNextUp ? '2px solid var(--color-sage, #2C5E55)' : '1px solid var(--color-border-subtle, #E2DDD5)',
                        backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
                        color: 'inherit',
                        textDecoration: 'none'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '4px',
                          border: lesson.isCompleted ? 'none' : '2px solid #D1D5DB',
                          backgroundColor: lesson.isCompleted ? 'var(--color-sage, #2C5E55)' : 'transparent',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#FFF',
                          fontSize: '12px',
                          flexShrink: 0
                        }}>
                          {lesson.isCompleted ? '✓' : ''}
                        </div>
                        {isNextUp && (
                          <span style={{
                            fontSize: '0.65rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            color: 'var(--color-sage, #2C5E55)',
                            backgroundColor: 'rgba(44, 94, 85, 0.1)',
                            padding: '0.15rem 0.5rem',
                            borderRadius: '4px'
                          }}>
                            Continue
                          </span>
                        )}
                      </div>

                      <span style={{
                        fontWeight: '600',
                        fontSize: '0.95rem',
                        color: 'var(--color-ink, #1F2937)',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}>
                        {lesson.title}
                      </span>

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', fontSize: '0.7rem', color: 'var(--color-ink-muted, #6B7280)', marginTop: 'auto' }}>
                        <span>⏱ {lesson.estimatedMinutes} min</span>
                        <span>•</span>
                        <span>{lesson.difficulty}</span>
                        {lesson.contentStatus !== 'Published' && (
                          <>
                            <span>•</span>
                            <span style={{ color: '#D97706', fontWeight: '600' }}>{lesson.contentStatus}</span>
                          </>
                        )}
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
