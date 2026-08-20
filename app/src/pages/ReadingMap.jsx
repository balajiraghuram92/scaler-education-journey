import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Check, ArrowRight, BookOpen, Layers, Clock, Sparkles } from 'lucide-react';
import './ReadingMap.css';

const DEFAULT_READING_MAP = {
  readThisWeek: [
    { id: 1, category: 'ReadThisWeek', title: 'Virtual threads', isCompleted: true },
    { id: 2, category: 'ReadThisWeek', title: 'Structured concurrency', isCompleted: true },
    { id: 3, category: 'ReadThisWeek', title: 'Structured concurrency (8)', isCompleted: true },
    { id: 4, category: 'ReadThisWeek', title: 'Structured concurrency', isCompleted: true }
  ],
  revisited: [
    { id: 5, category: 'Revisited', title: 'Spring async and resilience', isCompleted: false }
  ],
  deferred: [
    { id: 6, category: 'Deferred', title: 'Next sometime', isCompleted: false },
    { id: 7, category: 'Deferred', title: 'Deferred tomorrow', isCompleted: false }
  ],
  lists: [
    { id: 8, category: 'Lists', title: 'APIs in (2)', isCompleted: false },
    { id: 9, category: 'Lists', title: 'Deferred (1)', isCompleted: false }
  ],
  prerequisites: [
    { id: 10, category: 'Prerequisites', title: 'Java Concurrency', isCompleted: false }
  ],
  activityTimeline: [
    { id: 1, dayLabel: 'Mon', activityCount: 1, orderIndex: 1 },
    { id: 2, dayLabel: 'Tue', activityCount: 1, orderIndex: 2 },
    { id: 3, dayLabel: 'Wed', activityCount: 3, orderIndex: 3 },
    { id: 4, dayLabel: 'Thu', activityCount: 6, orderIndex: 4 },
    { id: 5, dayLabel: 'Fri', activityCount: 2, orderIndex: 5 },
    { id: 6, dayLabel: 'Sat', activityCount: 4, orderIndex: 6 },
    { id: 7, dayLabel: 'Sun', activityCount: 0, orderIndex: 7 },
    { id: 8, dayLabel: 'Sun', activityCount: 5, orderIndex: 8 }
  ],
  knowledgeThreads: [
    {
      id: 1,
      domain: 'Java',
      rawPath: 'Java → concurrency → virtual threads → structured concurrency',
      nodes: ['Java', 'concurrency', 'virtual threads', 'structured concurrency']
    },
    {
      id: 2,
      domain: 'Backend',
      rawPath: 'Backend → APIs → async processing → resilience',
      nodes: ['Backend', 'APIs', 'async processing', 'resilience']
    },
    {
      id: 3,
      domain: 'Cloud',
      rawPath: 'Cloud → containers → orchestration → networking',
      nodes: ['Cloud', 'containers', 'orchestration', 'networking']
    }
  ]
};

export default function ReadingMap() {
  const [readingData, setReadingData] = useState(DEFAULT_READING_MAP);
  const [loading, setLoading] = useState(true);
  const [newItemText, setNewItemText] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ReadThisWeek');
  const [isAdding, setIsAdding] = useState(false);

  const fetchReadingMap = useCallback(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/reading-map`, {
      headers: {
        'x-api-key': import.meta.env.VITE_API_KEY || ''
      }
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && (data.readThisWeek || data.knowledgeThreads)) {
          setReadingData({
            readThisWeek: data.readThisWeek || [],
            revisited: data.revisited || [],
            deferred: data.deferred || [],
            lists: data.lists || [],
            prerequisites: data.prerequisites || [],
            activityTimeline: data.activityTimeline?.length > 0 ? data.activityTimeline : DEFAULT_READING_MAP.activityTimeline,
            knowledgeThreads: data.knowledgeThreads?.length > 0 ? data.knowledgeThreads : DEFAULT_READING_MAP.knowledgeThreads
          });
        }
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Backend reading-map API offline, utilizing default reading map dataset:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchReadingMap();
  }, [fetchReadingMap]);

  useEffect(() => {
    const handleUpdate = () => {
      fetchReadingMap();
    };
    window.addEventListener('verticalsUpdated', handleUpdate);
    window.addEventListener('readingMapUpdated', handleUpdate);
    return () => {
      window.removeEventListener('verticalsUpdated', handleUpdate);
      window.removeEventListener('readingMapUpdated', handleUpdate);
    };
  }, [fetchReadingMap]);

  const toggleItem = async (item) => {
    // Optimistic UI Update
    setReadingData((prev) => {
      const updateList = (list) =>
        list.map((i) => (i.id === item.id ? { ...i, isCompleted: !i.isCompleted } : i));

      return {
        ...prev,
        readThisWeek: updateList(prev.readThisWeek),
        revisited: updateList(prev.revisited),
        deferred: updateList(prev.deferred),
        lists: updateList(prev.lists),
        prerequisites: updateList(prev.prerequisites)
      };
    });

    try {
      await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/reading-map/items/${item.id}/toggle`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': import.meta.env.VITE_API_KEY || ''
        }
      });
    } catch (err) {
      console.error('Failed to toggle reading item:', err);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!newItemText.trim()) return;

    const optimisticItem = {
      id: Date.now(),
      category: selectedCategory,
      title: newItemText.trim(),
      isCompleted: selectedCategory === 'ReadThisWeek'
    };

    setReadingData((prev) => {
      const keyMap = {
        ReadThisWeek: 'readThisWeek',
        Revisited: 'revisited',
        Deferred: 'deferred',
        Lists: 'lists',
        Prerequisites: 'prerequisites'
      };
      const listKey = keyMap[selectedCategory] || 'readThisWeek';
      return {
        ...prev,
        [listKey]: [...prev[listKey], optimisticItem]
      };
    });

    const itemToAdd = newItemText.trim();
    setNewItemText('');
    setIsAdding(false);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/reading-map/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': import.meta.env.VITE_API_KEY || ''
        },
        body: JSON.stringify({
          category: selectedCategory,
          title: itemToAdd
        })
      });

      if (response.ok) {
        fetchReadingMap();
      }
    } catch (err) {
      console.error('Failed to create reading item:', err);
    }
  };

  const maxActivity = Math.max(...readingData.activityTimeline.map((a) => a.activityCount), 1);

  return (
    <div className="reading-map-page">
      {/* Editorial Canvas Container */}
      <div className="reading-map-container">
        
        {/* Top Header */}
        <header className="reading-map-header">
          <h1 className="reading-map-title">‘Reading Map’</h1>
          <div className="reading-map-controls">
            <button
              type="button"
              className="editorial-pill-btn"
              onClick={() => setIsAdding(!isAdding)}
              title="Add a new study or reading topic"
            >
              <Plus size={14} className={isAdding ? 'rotate-45' : ''} />
              <span>{isAdding ? 'Cancel' : 'Add Entry'}</span>
            </button>
          </div>
        </header>

        {/* Quick Add Form (Inline Accordion) */}
        {isAdding && (
          <form className="reading-add-form" onSubmit={handleAddItem}>
            <div className="form-inner">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="category-select"
              >
                <option value="ReadThisWeek">Read this week</option>
                <option value="Revisited">Revisited</option>
                <option value="Deferred">Deferred</option>
                <option value="Lists">Lists</option>
                <option value="Prerequisites">Prerequisites</option>
              </select>
              <input
                type="text"
                value={newItemText}
                onChange={(e) => setNewItemText(e.target.value)}
                placeholder="Enter topic title (e.g. Virtual threads, Concurrency)..."
                className="entry-input"
                autoFocus
              />
              <button type="submit" className="submit-entry-btn">
                Add to Map
              </button>
            </div>
          </form>
        )}

        {/* Main 3-Column Editorial Grid */}
        <main className="reading-map-grid">
          
          {/* Column 1: Reading Status Stream */}
          <section className="grid-column column-status-stream">
            {/* Read this week */}
            <div className="reading-section">
              <h2 className="section-title">Read this week</h2>
              <div className="section-divider" />
              <ul className="reading-list">
                {readingData.readThisWeek.map((item) => (
                  <li
                    key={item.id}
                    className={`reading-list-item ${item.isCompleted ? 'is-completed' : ''}`}
                    onClick={() => toggleItem(item)}
                    title="Click to toggle status"
                  >
                    <span className="bullet-point">•</span>
                    <span className="item-text">{item.title}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Revisited */}
            <div className="reading-section">
              <h2 className="section-title">Revisited</h2>
              <div className="section-divider" />
              <ul className="reading-list">
                {readingData.revisited.map((item) => (
                  <li
                    key={item.id}
                    className={`reading-list-item ${item.isCompleted ? 'is-completed' : ''}`}
                    onClick={() => toggleItem(item)}
                    title="Click to toggle status"
                  >
                    <span className="bullet-point">•</span>
                    <span className="item-text">{item.title}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Deferred */}
            <div className="reading-section">
              <h2 className="section-title">Deferred</h2>
              <div className="section-divider" />
              <ul className="reading-list">
                {readingData.deferred.map((item) => (
                  <li
                    key={item.id}
                    className={`reading-list-item ${item.isCompleted ? 'is-completed' : ''}`}
                    onClick={() => toggleItem(item)}
                    title="Click to toggle status"
                  >
                    <span className="bullet-point">•</span>
                    <span className="item-text">{item.title}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* Column 2: Lists & Queues */}
          <section className="grid-column column-lists">
            <div className="reading-section">
              <h2 className="section-title">Lists</h2>
              <div className="section-divider" />
              <ul className="reading-list">
                {readingData.lists.map((item) => (
                  <li
                    key={item.id}
                    className={`reading-list-item ${item.isCompleted ? 'is-completed' : ''}`}
                    onClick={() => toggleItem(item)}
                    title="Click to toggle status"
                  >
                    <span className="bullet-point">•</span>
                    <span className="item-text">{item.title}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* Column 3: Prerequisites, Timeline Activity & Knowledge Threads */}
          <section className="grid-column column-pathways">
            
            {/* Prerequisites */}
            <div className="reading-section">
              <h2 className="section-title">Prerequisites</h2>
              <div className="section-divider" />
              <ul className="reading-list">
                {readingData.prerequisites.map((item) => (
                  <li
                    key={item.id}
                    className={`reading-list-item ${item.isCompleted ? 'is-completed' : ''}`}
                    onClick={() => toggleItem(item)}
                    title="Click to toggle status"
                  >
                    <span className="bullet-point">•</span>
                    <span className="item-text">{item.title}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Next & Activity Timeline */}
            <div className="reading-section next-section">
              <h2 className="section-title">Next</h2>
              
              {/* Daily Activity Sparkline */}
              <div className="timeline-sparkline-wrapper">
                <div className="sparkline-chart">
                  {readingData.activityTimeline.map((act, index) => {
                    const heightPercent = act.activityCount > 0 
                      ? Math.max(15, (act.activityCount / maxActivity) * 100) 
                      : 4;

                    return (
                      <div key={act.id || index} className="sparkline-col" title={`${act.dayLabel}: ${act.activityCount} study sessions`}>
                        <div className="sparkline-bar-track">
                          <div
                            className={`sparkline-bar ${act.activityCount === 0 ? 'is-zero' : ''}`}
                            style={{ height: `${heightPercent}%` }}
                          />
                        </div>
                        <span className="day-label">{act.dayLabel}</span>
                      </div>
                    );
                  })}
                  <div className="timeline-baseline-arrow">
                    <svg viewBox="0 0 24 24" className="arrow-svg">
                      <path d="M5 12h14M12 5l7 7-7 7" stroke="#8C9A94" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Knowledge Threads */}
            <div className="reading-section threads-section">
              <h2 className="section-title">Knowledge threads</h2>
              <div className="section-divider" />
              
              <div className="threads-list">
                {readingData.knowledgeThreads.map((thread) => (
                  <div key={thread.id} className="knowledge-thread-line">
                    <div className="thread-nodes-flow">
                      {thread.nodes && thread.nodes.length > 0 ? (
                        thread.nodes.map((node, nIdx) => (
                          <React.Fragment key={nIdx}>
                            <span className={`thread-node ${nIdx === 0 ? 'is-domain' : ''}`}>
                              {node}
                            </span>
                            {nIdx < thread.nodes.length - 1 && (
                              <span className="thread-arrow">→</span>
                            )}
                          </React.Fragment>
                        ))
                      ) : (
                        <span className="thread-raw-path">{thread.rawPath}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </section>

        </main>

      </div>
    </div>
  );
}
