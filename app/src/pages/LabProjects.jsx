import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Terminal } from 'lucide-react';
import { api } from '../api/client';
import { LoadingState, ErrorState, EmptyState, DevFixturesBanner } from '../components/common/StateViews';

function getDevFixtures() {
  if (import.meta.env.VITE_ENABLE_DEV_FIXTURES !== 'true') {
    return null;
  }
  return {
    title: 'Engineering Lab Sandboxes (Dev Fixture)',
    description: 'Hands-on project architectures: Rebuild, Break, and Narrate real-world production systems.',
    modules: [
      {
        id: 1,
        title: 'Lab A — Warehouse Management System (WMS) Defect Detection',
        description: 'Real-time telemetry, automated triage, and distributed event-driven fault isolation.',
        lessons: [
          { id: 1, title: 'WMS Architecture & Event Ingestion', estimatedMinutes: 45, difficulty: 'Advanced', isCompleted: false },
          { id: 2, title: 'Fault Injection & Chaos Engineering Harness', estimatedMinutes: 60, difficulty: 'Advanced', isCompleted: false }
        ]
      },
      {
        id: 2,
        title: 'Lab B — Unity Localization & Asset Delivery Platform',
        description: 'High-throughput internationalization asset pipeline with low-latency CDN synchronization.',
        lessons: [
          { id: 3, title: 'Localization Pipeline & Dynamic String Table Sync', estimatedMinutes: 40, difficulty: 'Intermediate', isCompleted: false, path: '/lab-projects/localization' },
          { id: 4, title: 'Asset Bundle Streaming & Version Negotiation', estimatedMinutes: 50, difficulty: 'Advanced', isCompleted: false, path: '/lab-projects/localization' }
        ]
      }
    ]
  };
}

export default function LabProjects() {
  const [labsPath, setLabsPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDevFixture, setIsDevFixture] = useState(false);

  const fetchLabs = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsDevFixture(false);
    try {
      // Fetch from canonical learning paths v2 endpoint
      let detailed = null;
      try {
        detailed = await api.v2.getLearningPath('lab-projects');
      } catch (err) {
        if (err?.status === 404) {
          const allPaths = await api.v2.getLearningPaths();
          const found = Array.isArray(allPaths) ? allPaths.find(p => p.slug === 'lab-projects' || p.slug === 'labs') : null;
          if (found) {
            detailed = await api.v2.getLearningPath(found.slug);
          }
        } else {
          throw err;
        }
      }

      if (detailed && Array.isArray(detailed.modules) && detailed.modules.length > 0) {
        setLabsPath(detailed);
      } else {
        // Explicit empty state if 404, no data, no modules, or empty path
        setLabsPath(null);
      }
    } catch (err) {
      console.warn('API error fetching Lab Projects:', err);
      if (err?.status === 404) {
        setLabsPath(null);
      } else if (import.meta.env.VITE_ENABLE_DEV_FIXTURES === 'true') {
        const fixtures = getDevFixtures();
        if (fixtures) {
          setIsDevFixture(true);
          setLabsPath(fixtures);
        } else {
          setError(err);
          setLabsPath(null);
        }
      } else {
        setError(err);
        setLabsPath(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLabs();
  }, [fetchLabs]);

  return (
    <div style={{ maxWidth: '1080px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      {isDevFixture && <DevFixturesBanner />}

      {/* Editorial Header */}
      <div style={{ marginBottom: '1rem', fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-sage, #2C5E55)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        ENGINEERING LABS & PROJECT SANDBOXES
      </div>

      <header style={{
        backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
        border: '1px solid var(--color-border-subtle, #E2DDD5)',
        borderRadius: '12px',
        padding: '2rem',
        marginBottom: '2rem',
        boxShadow: '0 4px 20px rgba(0,0,0,0.03)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontFamily: 'var(--font-serif, "Newsreader", serif)', fontSize: '2.25rem', color: 'var(--color-ink, #1F2937)', margin: '0 0 0.75rem 0' }}>
              {labsPath?.title || 'Engineering Lab Sandboxes'}
            </h1>
            <p style={{ color: 'var(--color-ink-muted, #6B7280)', lineHeight: '1.6', maxWidth: '720px', margin: 0 }}>
              {labsPath?.description || 'Hands-on project architectures and system sandboxes.'}
            </p>
          </div>
          <span style={{
            backgroundColor: 'rgba(44, 94, 85, 0.08)',
            color: 'var(--color-sage, #2C5E55)',
            padding: '0.35rem 0.8rem',
            borderRadius: '6px',
            fontSize: '0.8rem',
            fontWeight: '700',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Terminal size={14} />
            Live Project Track
          </span>
        </div>
      </header>

      {error ? (
        <ErrorState error={error} onRetry={fetchLabs} title="Unable to Load Lab Projects" />
      ) : loading ? (
        <LoadingState message="Initializing project sandboxes..." />
      ) : !labsPath || !labsPath.modules || labsPath.modules.length === 0 ? (
        <EmptyState message="No active lab project courses found in the curriculum." icon="🛠️" />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          {labsPath.modules.map((mod, idx) => (
            <div key={mod.id || idx} style={{
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
                  <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--color-sage, #2C5E55)', textTransform: 'uppercase' }}>
                    Project Lab {idx + 1}
                  </span>
                  <h3 style={{ margin: '0.25rem 0 0 0', fontSize: '1.2rem', color: 'var(--color-ink, #1F2937)' }}>
                    {mod.title}
                  </h3>
                </div>
              </div>

              <div style={{ padding: '1.5rem' }}>
                <p style={{ color: 'var(--color-ink-muted, #6B7280)', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '1.5rem' }}>
                  {mod.description}
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {mod.lessons?.map((les) => {
                    const destination = les.path || (mod.title?.includes('Lab B') || mod.id === 2 ? '/lab-projects/localization' : null);
                    const content = (
                      <div style={{
                        padding: '1rem',
                        border: '1px solid #F3F4F6',
                        borderRadius: '6px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        backgroundColor: '#FAFAFA',
                        transition: 'border-color 0.15s ease',
                        cursor: destination ? 'pointer' : 'default'
                      }}>
                        <div>
                          <div style={{ fontWeight: '600', color: 'var(--color-ink, #1F2937)' }}>{les.title}</div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)', marginTop: '0.2rem' }}>
                            ⏱ {les.estimatedMinutes} min • {les.difficulty}
                          </div>
                        </div>
                        <span style={{
                          fontSize: '0.8rem',
                          fontWeight: '600',
                          color: 'var(--color-sage, #2C5E55)',
                          backgroundColor: '#FFF',
                          border: '1px solid var(--color-border-subtle, #E2DDD5)',
                          padding: '0.3rem 0.75rem',
                          borderRadius: '4px'
                        }}>
                          {destination ? 'Launch Sandbox →' : 'Sandbox Ready'}
                        </span>
                      </div>
                    );

                    return destination ? (
                      <Link key={les.id} to={destination} style={{ textDecoration: 'none', color: 'inherit' }}>
                        {content}
                      </Link>
                    ) : (
                      <div key={les.id}>
                        {content}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
