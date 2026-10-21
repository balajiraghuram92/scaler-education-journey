import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Layers, Terminal } from 'lucide-react';
import KnowledgeAtlasGraph, { DEFAULT_DOMAINS, DEFAULT_CONCEPTS, DEFAULT_CONNECTIONS } from '../components/KnowledgeAtlasGraph';
import RecentLearningPathTracker from '../components/RecentLearningPathTracker';
import ResumeCard from '../components/learning/ResumeCard';
import { api } from '../api/client';
import { ErrorState, LoadingState, DevFixturesBanner } from '../components/common/StateViews';
import { readRecentLearningPathActivity, sortLearningPathsByRecency } from '../utils/recentLearningPaths';
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
  const [recentActivity] = useState(() => readRecentLearningPathActivity());

  const sortedLearningPaths = useMemo(
    () => sortLearningPathsByRecency(learningPaths, recentActivity),
    [learningPaths, recentActivity]
  );

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
        const mappedConnections = (data.connections || [])
          .map(connection => ({
            from: connection.from || connection.source,
            to: connection.to || connection.target
          }))
          .filter(connection => connection.from && connection.to);

        setAtlasData({
          domains: mappedDomains,
          concepts: mappedConcepts,
          connections: mappedConnections
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
          <div className="atlas-header-actions">
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

          <ResumeCard />

          {sortedLearningPaths.length > 0 && (
            <>
              <RecentLearningPathTracker paths={sortedLearningPaths} />
            </>
          )}
        </>
      )}
    </div>
  );
}
