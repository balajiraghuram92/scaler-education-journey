import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Layers, Terminal, Sparkles } from 'lucide-react';
import KnowledgeAtlasGraph, { DEFAULT_DOMAINS, DEFAULT_CONCEPTS, DEFAULT_CONNECTIONS } from '../components/KnowledgeAtlasGraph';
import { api } from '../api/client';
import { ErrorState, LoadingState, DevFixturesBanner } from '../components/common/StateViews';
import './Home.css';

function normalizePrerequisite(prerequisite) {
  if (typeof prerequisite === 'string') {
    return { name: prerequisite };
  }

  if (prerequisite && typeof prerequisite === 'object') {
    return {
      name: prerequisite.name || prerequisite.title || prerequisite.prerequisiteTitle || 'Prerequisite',
      status: prerequisite.status
    };
  }

  return { name: 'Prerequisite' };
}

function normalizeLessonLabel(lesson, fallback) {
  if (typeof lesson === 'string') {
    return lesson;
  }

  if (lesson && typeof lesson === 'object') {
    return lesson.lessonTitle || lesson.targetTitle || lesson.title ||
      lesson.lessonSlug || lesson.targetSlug || fallback;
  }

  return fallback;
}

export default function Home() {
  const [atlasData, setAtlasData] = useState({
    domains: [],
    concepts: [],
    connections: []
  });
  const [learningPaths, setLearningPaths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDevFixture, setIsDevFixture] = useState(false);

  const fetchAtlasData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsDevFixture(false);
    try {
      // 1. Fetch Knowledge Atlas Graph from v2 API
      const data = await api.v2.getKnowledgeAtlas();
      if (data && Array.isArray(data.domains) && data.domains.length > 0) {
        const mappedDomains = data.domains.map(d => ({
          id: d.slug || d.id,
          label: d.name
        }));
        const mappedConcepts = data.concepts.map(c => ({
          id: c.slug || c.id,
          title: c.title,
          subLabel: c.subLabel || c.title,
          connectedDomains: c.domainIds || [],
          prerequisites: (c.prerequisites || []).map(normalizePrerequisite),
          relatedLessons: (c.outgoingRelations || [])
            .map(relation => normalizeLessonLabel(relation, 'Related Concept')),
          nextLessons: (c.nextLessons || [])
            .map(lesson => normalizeLessonLabel(lesson, 'Next Lesson'))
        }));

        setAtlasData({
          domains: mappedDomains,
          concepts: mappedConcepts,
          connections: []
        });
      }

      // 2. Fetch Canonical Learning Paths Index
      const paths = await api.v2.getLearningPaths();
      if (Array.isArray(paths)) {
        setLearningPaths(paths);
      }
    } catch (err) {
      console.warn('API error fetching Knowledge Atlas:', err);
      // Explicit development-only fixture flag check
      if (import.meta.env.VITE_ENABLE_DEV_FIXTURES === 'true') {
        setIsDevFixture(true);
        setAtlasData({
          domains: DEFAULT_DOMAINS,
          concepts: DEFAULT_CONCEPTS,
          connections: DEFAULT_CONNECTIONS
        });
      } else {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAtlasData();
  }, [fetchAtlasData]);

  return (
    <div className="knowledge-atlas-page">
      {isDevFixture && <DevFixturesBanner />}

      {/* Page Header */}
      <header className="atlas-header">
        <div className="atlas-header-top">
          <h1 className="atlas-main-title">‘Knowledge Atlas’ index</h1>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            <Link to="/reading-map" className="atlas-reading-map-btn" title="View Reading Map & Progress">
              <BookOpen size={14} />
              <span>Reading Map</span>
            </Link>
            <Link to="/lab-projects" className="atlas-reading-map-btn" title="View Hands-on Lab Projects">
              <Terminal size={14} />
              <span>Lab Projects</span>
            </Link>
            <Link to="/curriculum-import" className="atlas-reading-map-btn" title="Import Curriculum Chapter">
              <Layers size={14} />
              <span>Curriculum Importer</span>
            </Link>
          </div>
        </div>
        <h2 className="atlas-section-subtitle">Major learning domains & curriculum pathways</h2>
      </header>

      {error ? (
        <ErrorState error={error} onRetry={fetchAtlasData} title="Knowledge Atlas Temporarily Unavailable" />
      ) : loading ? (
        <LoadingState message="Mapping cognitive neural mesh..." />
      ) : (
        <>
          {/* Main Interactive Synaptic Bipartite Graph */}
          {atlasData.domains.length > 0 && (
            <main className="atlas-graph-stage">
              <KnowledgeAtlasGraph
                domains={atlasData.domains}
                concepts={atlasData.concepts}
                connections={atlasData.connections}
              />
            </main>
          )}

          {/* Canonical Learning Pathways Directory */}
          {learningPaths.length > 0 && (
            <section style={{ maxWidth: '1200px', margin: '3rem auto 2rem', padding: '0 1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontFamily: 'var(--font-serif, "Newsreader", serif)', fontSize: '1.75rem', color: 'var(--color-ink, #1F2937)', margin: 0 }}>
                  Curriculum Learning Pathways
                </h2>
                <span style={{ fontSize: '0.875rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                  {learningPaths.length} active tracks
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem' }}>
                {learningPaths.map((path) => (
                  <Link
                    key={path.id}
                    to={`/learning-paths/${path.slug}`}
                    style={{
                      backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
                      border: '1px solid var(--color-border-subtle, #E2DDD5)',
                      borderRadius: '10px',
                      padding: '1.5rem',
                      textDecoration: 'none',
                      color: 'inherit',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{
                          backgroundColor: 'rgba(44, 94, 85, 0.08)',
                          color: 'var(--color-sage, #2C5E55)',
                          padding: '0.15rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.7rem',
                          fontWeight: '700',
                          textTransform: 'uppercase'
                        }}>
                          {path.pathType}
                        </span>
                        <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--color-sage, #2C5E55)' }}>
                          {path.progressPercentage}%
                        </span>
                      </div>
                      <h3 style={{ margin: '0.5rem 0', fontSize: '1.15rem', color: 'var(--color-ink, #1F2937)' }}>
                        {path.title}
                      </h3>
                      <p style={{
                        color: 'var(--color-ink-muted, #6B7280)',
                        fontSize: '0.85rem',
                        lineHeight: '1.5',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        margin: 0
                      }}>
                        {path.description}
                      </p>
                    </div>

                    <div style={{ marginTop: '1.25rem' }}>
                      <div style={{
                        width: '100%',
                        height: '4px',
                        backgroundColor: '#E5E7EB',
                        borderRadius: '2px',
                        overflow: 'hidden',
                        marginBottom: '0.75rem'
                      }}>
                        <div style={{
                          width: `${path.progressPercentage}%`,
                          height: '100%',
                          backgroundColor: 'var(--color-sage, #2C5E55)'
                        }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                        <span>{path.completedLessons} / {path.totalLessons} lessons</span>
                        <span style={{ fontWeight: '600', color: 'var(--color-sage, #2C5E55)' }}>Explore →</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
