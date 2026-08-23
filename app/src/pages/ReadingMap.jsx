import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Check, ArrowRight, BookOpen, Layers, Clock, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import { LoadingState, ErrorState, EmptyState, DevFixturesBanner } from '../components/common/StateViews';
import './ReadingMap.css';

const DEFAULT_READING_MAP = {
  readThisWeek: [
    { id: 1, category: 'ReadThisWeek', title: 'Virtual threads', isCompleted: true },
    { id: 2, category: 'ReadThisWeek', title: 'Structured concurrency', isCompleted: true }
  ],
  revisited: [
    { id: 5, category: 'Revisited', title: 'Spring async and resilience', isCompleted: false }
  ],
  deferred: [
    { id: 6, category: 'Deferred', title: 'Next sometime', isCompleted: false }
  ],
  lists: [],
  prerequisites: [],
  activityTimeline: [],
  knowledgeThreads: []
};

export default function ReadingMap() {
  const [readingData, setReadingData] = useState({
    items: [],
    threads: [],
    recentActivities: [],
    statistics: { totalItems: 0, completedItems: 0, progressPercentage: 0 }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDevFixture, setIsDevFixture] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');

  const fetchReadingMap = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsDevFixture(false);
    try {
      const data = await api.v2.getReadingMap();
      if (data) {
        setReadingData({
          items: data.items || [],
          threads: data.threads || [],
          recentActivities: data.recentActivities || [],
          statistics: data.statistics || { totalItems: 0, completedItems: 0, progressPercentage: 0 }
        });
      }
    } catch (err) {
      console.warn('API error fetching Reading Map:', err);
      if (import.meta.env.VITE_ENABLE_DEV_FIXTURES === 'true') {
        setIsDevFixture(true);
        setReadingData({
          items: [...DEFAULT_READING_MAP.readThisWeek, ...DEFAULT_READING_MAP.revisited, ...DEFAULT_READING_MAP.deferred],
          threads: DEFAULT_READING_MAP.knowledgeThreads,
          recentActivities: [],
          statistics: { totalItems: 4, completedItems: 2, progressPercentage: 50 }
        });
      } else {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReadingMap();
  }, [fetchReadingMap]);

  const filteredItems = selectedCategory === 'All'
    ? readingData.items
    : readingData.items.filter(i => i.category === selectedCategory);

  return (
    <div className="reading-map-page">
      {isDevFixture && <DevFixturesBanner />}

      {/* Top Editorial Banner */}
      <div className="reading-map-top-strip">
        <div className="top-strip-inner">
          <span className="panel-tag">PANEL B: READING MAP & CURATED JOURNEY</span>
          <span className="synapse-badge">
            <Sparkles size={12} />
            Synaptic Bridge
          </span>
        </div>
      </div>

      <div className="reading-map-container">
        {/* Header with Stats */}
        <header className="reading-map-header">
          <div className="header-text-group">
            <h1 className="reading-map-main-title">Reading Map & Knowledge Flow</h1>
            <p className="reading-map-subtitle">
              Curated reading queue, sequential learning tracks, and cognitive progression.
            </p>
          </div>

          <div className="reading-map-stats-card">
            <div className="stat-item">
              <span className="stat-value">{readingData.statistics.completedItems} / {readingData.statistics.totalItems}</span>
              <span className="stat-label">Items Read</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{readingData.statistics.progressPercentage}%</span>
              <span className="stat-label">Queue Progress</span>
            </div>
          </div>
        </header>

        {error ? (
          <ErrorState error={error} onRetry={fetchReadingMap} title="Unable to Load Reading Map" />
        ) : loading ? (
          <LoadingState message="Syncing Reading Map & Activity..." />
        ) : (
          <div className="reading-map-layout">
            {/* Left Column: Categorized Reading Queue */}
            <section className="reading-queue-section">
              <div className="section-header">
                <h2 className="section-title">
                  <BookOpen size={18} />
                  Reading Queue
                </h2>
                <div className="category-filter-pills">
                  {['All', 'ReadThisWeek', 'Revisited', 'Deferred', 'Lists', 'Prerequisites'].map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`filter-pill ${selectedCategory === cat ? 'active' : ''}`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              {filteredItems.length === 0 ? (
                <EmptyState message="No reading items in this category." />
              ) : (
                <div className="reading-items-list">
                  {filteredItems.map((item) => (
                    <div key={item.id} className={`reading-item-card ${item.isCompleted ? 'completed' : ''}`}>
                      <div className="reading-item-left">
                        <div className={`status-checkbox ${item.isCompleted ? 'checked' : ''}`}>
                          {item.isCompleted && <Check size={12} />}
                        </div>
                        <div className="reading-item-info">
                          <span className="reading-item-title">{item.title}</span>
                          {item.subText && <span className="reading-item-subtext">{item.subText}</span>}
                        </div>
                      </div>
                      <span className="reading-item-category-tag">{item.category}</span>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Right Column: Knowledge Threads & Activity */}
            <aside className="knowledge-threads-section">
              <div className="section-header">
                <h2 className="section-title">
                  <Layers size={18} />
                  Knowledge Threads
                </h2>
              </div>

              <div className="threads-list">
                {readingData.threads?.map((thread) => (
                  <div key={thread.id} className="thread-card">
                    <span className="thread-domain-tag">{thread.domain}</span>
                    <p className="thread-path-text">{thread.rawPath}</p>
                  </div>
                ))}
              </div>

              {readingData.recentActivities?.length > 0 && (
                <div className="recent-activity-box" style={{ marginTop: '2rem' }}>
                  <h3 style={{ fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Clock size={16} /> Recent Activity
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
                    {readingData.recentActivities.slice(0, 5).map((act) => (
                      <div key={act.id} style={{ padding: '0.4rem 0.6rem', backgroundColor: '#FFF', borderRadius: '4px', border: '1px solid #E5E7EB' }}>
                        <strong>{act.eventType}</strong> {act.lessonTitle ? `• ${act.lessonTitle}` : ''}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </aside>
          </div>
        )}
      </div>
    </div>
  );
}
