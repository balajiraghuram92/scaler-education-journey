import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import KnowledgeAtlasGraph, { DEFAULT_DOMAINS, DEFAULT_CONCEPTS, DEFAULT_CONNECTIONS } from '../components/KnowledgeAtlasGraph';
import './Home.css';

export default function Home() {
  const [atlasData, setAtlasData] = useState({
    domains: DEFAULT_DOMAINS,
    concepts: DEFAULT_CONCEPTS,
    connections: DEFAULT_CONNECTIONS
  });
  const [loading, setLoading] = useState(true);

  const fetchAtlasData = useCallback(() => {
    setLoading(true);
    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/knowledge-atlas`, {
      headers: {
        'x-api-key': import.meta.env.VITE_API_KEY || ''
      }
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.domains) && data.domains.length > 0) {
          const mappedDomains = data.domains.map(d => ({
            id: d.slug,
            label: d.name
          }));
          const mappedConcepts = data.concepts.map(c => {
            if (c.slug === 'concurrency') {
              return {
                id: 'concurrency',
                title: 'Concurrency',
                popoverTitle: 'Java Concurrency',
                subLabel: 'Java Concurrency',
                connectedDomains: ['foundations', 'backend', 'reliability'],
                prerequisites: [{ name: 'Java Concurrency', status: 'included' }],
                relatedLessons: ['Java Concurrency', 'Structured Concurrency'],
                nextLessons: ['Java Concurrency', 'Next Security']
              };
            }
            return {
              id: c.slug,
              title: c.title,
              subLabel: c.subLabel,
              connectedDomains: c.connectedDomains || [],
              prerequisites: c.prerequisites || [],
              relatedLessons: c.relatedLessons || [],
              nextLessons: c.nextLessons || []
            };
          });
          const mappedConnections = (data.connections || []).map(conn => ({
            from: conn.from,
            to: conn.to
          }));

          setAtlasData({
            domains: mappedDomains,
            concepts: mappedConcepts,
            connections: mappedConnections
          });
        }
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Backend knowledge-atlas API offline, using default Knowledge Atlas schema:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchAtlasData();
  }, [fetchAtlasData]);

  useEffect(() => {
    const handleUpdate = () => {
      fetchAtlasData();
    };
    window.addEventListener('verticalsUpdated', handleUpdate);
    return () => window.removeEventListener('verticalsUpdated', handleUpdate);
  }, [fetchAtlasData]);

  return (
    <div className="knowledge-atlas-page">
      {/* Page Header */}
      <header className="atlas-header">
        <div className="atlas-header-top">
          <h1 className="atlas-main-title">‘Knowledge Atlas’ index</h1>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <Link to="/chapter/structured-concurrency" className="atlas-reading-map-btn" title="View Long-form Concept Chapters">
              <span>Concept Chapters</span>
              <ArrowRight size={14} />
            </Link>
            <Link to="/reading-map" className="atlas-reading-map-btn" title="View Reading Map & Progress">
              <span>Reading Map</span>
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>
        <h2 className="atlas-section-subtitle">Major learning domains</h2>
      </header>

      {/* Main Interactive Synaptic Bipartite Graph */}
      <main className="atlas-graph-stage">
        <KnowledgeAtlasGraph
          domains={atlasData.domains}
          concepts={atlasData.concepts}
          connections={atlasData.connections}
        />
      </main>
    </div>
  );
}


