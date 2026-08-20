import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import CodeComparisonSwitcher from '../components/CodeComparisonSwitcher';
import './ChapterReader.css';

export default function ChapterReader() {
  const { slug, verticalOrCourseSlug, moduleSlug, lessonSlug } = useParams();
  const navigate = useNavigate();

  const [chapter, setChapter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSectionId, setActiveSectionId] = useState('introduction');
  const [personalNotesList, setPersonalNotesList] = useState([]);
  const [newNoteText, setNewNoteText] = useState('');
  const [isAddingNote, setIsAddingNote] = useState(false);

  // Resolved lookup slug
  const targetSlug = useMemo(() => {
    if (lessonSlug) return lessonSlug;
    if (slug) return slug;
    return 'structured-concurrency'; // default flagship
  }, [slug, lessonSlug]);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const endpoint = verticalOrCourseSlug && moduleSlug && lessonSlug
      ? `/api/chapters/${verticalOrCourseSlug}/${moduleSlug}/${lessonSlug}`
      : `/api/chapters/${targetSlug}`;

    fetch(endpoint)
      .then((res) => {
        if (!res.ok) {
          // Fallback to generic chapters list or mock
          return fetch(`/api/chapters/${targetSlug}`).then(r => {
            if (!r.ok) throw new Error(`Chapter '${targetSlug}' not found.`);
            return r.json();
          });
        }
        return res.json();
      })
      .then((data) => {
        if (isMounted) {
          setChapter(data);
          setPersonalNotesList(data.notes || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn('API fetch warning, using local fallback state:', err);
        if (isMounted) {
          // Provide rich local state matching Learning-homepage.png if API is unreachable
          const fallbackData = getFallbackChapter(targetSlug);
          setChapter(fallbackData);
          setPersonalNotesList(fallbackData.notes || []);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [targetSlug, verticalOrCourseSlug, moduleSlug, lessonSlug]);

  // ScrollSpy Intersection Observer
  useEffect(() => {
    const handleScroll = () => {
      const sections = document.querySelectorAll('.chapter-content-section[id]');
      const scrollPosition = window.scrollY + 160;

      let currentId = 'introduction';
      sections.forEach((section) => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        if (scrollPosition >= top && scrollPosition < top + height) {
          currentId = section.id;
        }
      });
      setActiveSectionId(currentId);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [chapter]);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNoteText.trim() || !chapter) return;

    const newNote = {
      noteType: 'PersonalNote',
      title: 'Field Reflection',
      contentBody: newNoteText.trim()
    };

    try {
      const res = await fetch(`/api/chapters/${chapter.id}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newNote)
      });
      if (res.ok) {
        const saved = await res.json();
        setPersonalNotesList([...personalNotesList, saved]);
        setNewNoteText('');
        setIsAddingNote(false);
      }
    } catch (err) {
      // Optimistic local add
      setPersonalNotesList([
        ...personalNotesList,
        { id: Date.now(), ...newNote, updatedAt: new Date().toISOString() }
      ]);
      setNewNoteText('');
      setIsAddingNote(false);
    }
  };

  if (loading) {
    return (
      <div className="chapter-reader-page">
        <div className="chapter-reader-loading">
          <div className="reader-spinner" />
          <p>Opening knowledge chamber...</p>
        </div>
      </div>
    );
  }

  if (error || !chapter) {
    return (
      <div className="chapter-reader-page">
        <div className="chapter-reader-error">
          <h3>Chapter Not Available</h3>
          <p>{error || 'Could not load chapter content.'}</p>
          <Link to="/learning" className="back-link">← Return to Learning Atlas</Link>
        </div>
      </div>
    );
  }

  // Generate Table of Contents
  const tocItems = [
    { id: 'introduction', label: 'Introduction', level: 1 },
    { id: 'core-invariants', label: 'Core Invariants', level: 1 },
    { id: 'concept-connection', label: 'Concept Connection', level: 2 },
    { id: 'code-comparison', label: 'Code Comparison', level: 2 },
    { id: 'architecture-hierarchy', label: 'Architecture Hierarchy', level: 2 },
    { id: 'worked-scenario', label: 'Worked Backend Scenario', level: 1 },
    ...(chapter.problems?.length > 0 ? [{ id: 'practice-problems', label: 'Practice Problems & Verification', level: 1 }] : [])
  ];

  return (
    <div className="chapter-reader-page">
      {/* Top Editorial Panel Tag */}
      <div className="chapter-reader-top-strip">
        <div className="top-strip-inner">
          <span className="panel-tag">PANEL D: CONCEPT CHAPTER</span>
        </div>
      </div>

      {/* Chapter Reader 3-Column Master Grid */}
      <div className="chapter-reader-container">
        {/* ========================================================= */}
        {/* COLUMN 1: LEFT TABLE OF CONTENTS RAIL                     */}
        {/* ========================================================= */}
        <aside className="chapter-toc-rail">
          <div className="toc-header-group">
            <h4 className="toc-rail-title">Table of contents</h4>
          </div>

          <nav className="toc-nav-list">
            {tocItems.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className={`toc-nav-link level-${item.level} ${activeSectionId === item.id ? 'is-active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  const target = document.getElementById(item.id);
                  if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }
                }}
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Sibling Chapters In Module */}
          {chapter.siblingChapters?.length > 1 && (
            <div className="toc-siblings-section">
              <h5 className="toc-siblings-title">In this module</h5>
              <ul className="toc-siblings-list">
                {chapter.siblingChapters.map((sib) => (
                  <li key={sib.id}>
                    <Link
                      to={`/chapter/${sib.slug}`}
                      className={`sibling-link ${sib.id === chapter.id ? 'is-current' : ''}`}
                    >
                      {sib.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>

        {/* ========================================================= */}
        {/* COLUMN 2: CENTER READING CHAMBER                          */}
        {/* ========================================================= */}
        <main className="chapter-reading-chamber">
          {/* Breadcrumbs */}
          <nav className="chamber-breadcrumb-trail">
            <Link to="/" className="breadcrumb-crumb">Knowledge Atlas</Link>
            <span className="breadcrumb-sep">→</span>
            <span className="breadcrumb-crumb">{chapter.course?.title || 'Java & Spring Architecture'}</span>
            <span className="breadcrumb-sep">→</span>
            <span className="breadcrumb-crumb is-leaf">{chapter.title}</span>
          </nav>

          {/* Display Header */}
          <header className="chamber-header">
            <h1 className="chamber-display-title">{chapter.title}</h1>
            {chapter.description && (
              <p className="chamber-dek-lead">{chapter.description}</p>
            )}
          </header>

          {/* Section 1: Introduction */}
          <section id="introduction" className="chapter-content-section">
            <div className="chamber-prose">
              <p>
                <strong>{chapter.title}</strong> treats concurrent execution as a structured block of code—mirroring structured programming constructs like <code>if/else</code> and <code>for</code> loops. In traditional concurrent programming ("unstructured concurrency"), the lifecycle of concurrent tasks is detached from the lexical scope that initiated them.
              </p>
              <p>
                When threads are spawned asynchronously across decoupled futures, background promises can outlive their originating caller. This leads to three fundamental engineering failures: leaked CPU/memory resources, orphaned database connection pool exhaustion, and swallowed exceptions.
              </p>
            </div>
          </section>

          {/* Section 2: Core Invariants */}
          <section id="core-invariants" className="chapter-content-section">
            <h3 className="chamber-section-heading">Core Invariants &amp; Scope Hierarchy</h3>
            <div className="chamber-prose">
              <p>
                Under a structured concurrency model, if a task splits into concurrent subtasks, all subtasks must complete or abort before the parent lexical scope exits. Failure in any child immediately cascades cancellation to all sibling tasks and unwinds the scope cleanly.
              </p>
            </div>

            {/* Concept Connection Card */}
            <div id="concept-connection" className="concept-connection-card">
              <h4 className="concept-connection-title">Concept connection</h4>
              <div className="concept-connection-divider" />
              <div className="concept-connection-grid">
                <div className="connection-col">
                  <span className="connection-col-label">Builds on:</span>
                  <ul className="connection-col-list">
                    <li>• Executors, Futures</li>
                    <li>• Virtual Threads</li>
                    <li>• Lexical Lifecycles</li>
                  </ul>
                </div>
                <div className="connection-col">
                  <span className="connection-col-label">Leads to:</span>
                  <ul className="connection-col-list">
                    <li>• Spring asynchronous workflows</li>
                    <li>• Resilient backend design</li>
                    <li>• High-throughput payment gateways</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          {/* Section 3: Code Comparison Switcher */}
          <section id="code-comparison" className="chapter-content-section">
            <h3 className="chamber-section-heading">Code Comparison &amp; Pattern Shift</h3>
            <CodeComparisonSwitcher comparisons={chapter.codeComparisons || []} />
          </section>

          {/* Section 4: Architecture Hierarchy SVG Diagram */}
          <section id="architecture-hierarchy" className="chapter-content-section">
            <h3 className="chamber-section-heading">Architecture &amp; Ownership Topology</h3>
            {chapter.diagrams?.length > 0 ? (
              chapter.diagrams.map((diag) => (
                <div key={diag.id} className="chamber-diagram-card">
                  <div
                    className="chamber-svg-canvas"
                    dangerouslySetInnerHTML={{ __html: diag.svgContent }}
                  />
                  {diag.caption && <p className="chamber-diagram-caption">{diag.caption}</p>}
                </div>
              ))
            ) : (
              <div className="chamber-diagram-card">
                <svg viewBox="0 0 640 220" width="100%" height="100%" className="chamber-svg-canvas" style={{ background: 'transparent' }}>
                  <rect x="220" y="20" width="200" height="40" rx="8" fill="#FFFFFF" stroke="#2C5E55" strokeWidth="2" />
                  <text x="320" y="45" textAnchor="middle" fontSize="13" fontWeight="bold" fill="#2C5E55">Task ownership</text>
                  <path d="M 260 60 L 120 110" stroke="#2C5E55" strokeWidth="1.5" strokeDasharray="4 4" fill="none" />
                  <path d="M 320 60 L 320 110" stroke="#2C5E55" strokeWidth="1.5" fill="none" />
                  <path d="M 380 60 L 520 110" stroke="#2C5E55" strokeWidth="1.5" strokeDasharray="4 4" fill="none" />
                  <rect x="40" y="110" width="160" height="38" rx="6" fill="#FFFFFF" stroke="#2C5E55" strokeWidth="1.5" />
                  <text x="120" y="134" textAnchor="middle" fontSize="12" fill="#1C2421">Ownership</text>
                  <rect x="240" y="110" width="160" height="38" rx="6" fill="#FFFFFF" stroke="#2C5E55" strokeWidth="1.5" />
                  <text x="320" y="134" textAnchor="middle" fontSize="12" fill="#1C2421">Task ownership</text>
                  <rect x="440" y="110" width="160" height="38" rx="6" fill="#FFFFFF" stroke="#2C5E55" strokeWidth="1.5" />
                  <text x="520" y="134" textAnchor="middle" fontSize="12" fill="#1C2421">Fraction</text>
                </svg>
                <p className="chamber-diagram-caption">Fine-line ownership hierarchy</p>
              </div>
            )}
          </section>

          {/* Section 5: Worked Backend Scenario */}
          <section id="worked-scenario" className="chapter-content-section">
            <h3 className="chamber-section-heading">Worked backend scenario</h3>
            <div className="chamber-prose">
              <p>
                In a high-throughput payment gateway, handling concurrent authentication, risk checks, and inventory reservations requires atomic failure semantics. When an downstream fraud service rejects a checkout attempt, continuing the inventory reservation causes stock locking anomalies.
              </p>
              <p>
                By wrapping the three tasks in a bounded structured scope (e.g. <code>StructuredTaskScope.ShutdownOnFailure()</code>), the first failure cancels all sibling virtual threads instantly, guaranteeing that no partial state mutations survive.
              </p>
            </div>
          </section>

          {/* Section 6: Interactive Problems (if present) */}
          {chapter.problems?.length > 0 && (
            <section id="practice-problems" className="chapter-content-section">
              <h3 className="chamber-section-heading">Verification &amp; Test Suite Verification</h3>
              <div className="chamber-problems-stack">
                {chapter.problems.map((prb, idx) => (
                  <div key={prb.id} className="chamber-problem-card">
                    <div className="prb-card-header">
                      <span className="prb-badge">{prb.packageName || `PROBLEM ${idx + 1}`}</span>
                      <h4 className="prb-card-title">{prb.title}</h4>
                      <span className={`prb-diff-tag diff-${prb.difficulty?.toLowerCase()}`}>{prb.difficulty}</span>
                    </div>
                    {prb.problemStatement && (
                      <p className="prb-statement">{prb.problemStatement}</p>
                    )}
                    {prb.testClassName && (
                      <div className="prb-maven-box">
                        <span className="maven-label">Maven Test Command:</span>
                        <code className="maven-cmd">mvn test -Dtest={prb.testClassName}</code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Chapter Navigation Footer */}
          <footer className="chamber-nav-footer">
            {chapter.previousChapter ? (
              <Link to={`/chapter/${chapter.previousChapter.slug}`} className="chamber-nav-btn prev">
                <span className="nav-dir">← Previous Chapter</span>
                <span className="nav-title">{chapter.previousChapter.title}</span>
              </Link>
            ) : <div />}

            {chapter.nextChapter ? (
              <Link to={`/chapter/${chapter.nextChapter.slug}`} className="chamber-nav-btn next">
                <span className="nav-dir">Next Chapter →</span>
                <span className="nav-title">{chapter.nextChapter.title}</span>
              </Link>
            ) : <div />}
          </footer>
        </main>

        {/* ========================================================= */}
        {/* COLUMN 3: RIGHT CONTEXTUAL SIDEBAR                        */}
        {/* ========================================================= */}
        <aside className="chapter-context-sidebar">
          {/* Related Lesson */}
          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Related lesson</h5>
            <Link to="/vertical/java-spring-lld" className="sidebar-meta-link">
              Concurrency → Structured Concurrency
            </Link>
          </div>

          <div className="sidebar-hairline-divider" />

          {/* Prerequisite */}
          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Prerequisite</h5>
            <Link to="/chapter/03-oop-2-access-modifiers-encapsulation" className="sidebar-meta-link">
              Structured concurrency → Structured Concurrency
            </Link>
          </div>

          <div className="sidebar-hairline-divider" />

          {/* Further Reading */}
          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Further reading</h5>
            <ul className="sidebar-reading-list">
              <li>
                <a href="https://openjdk.org/jeps/453" target="_blank" rel="noreferrer" className="sidebar-meta-link">
                  JEP 453: Structured Concurrency
                </a>
              </li>
              <li>
                <a href="https://docs.spring.io" target="_blank" rel="noreferrer" className="sidebar-meta-link">
                  Spring asynchronous workflows
                </a>
              </li>
              <li>
                <span className="sidebar-meta-text">Further reading for resilient backend design</span>
              </li>
            </ul>
          </div>

          <div className="sidebar-hairline-divider" />

          {/* Personal Note */}
          <div className="sidebar-meta-block">
            <div className="sidebar-title-row">
              <h5 className="sidebar-meta-title">Personal note</h5>
              <button
                type="button"
                className="add-note-btn"
                onClick={() => setIsAddingNote(!isAddingNote)}
              >
                {isAddingNote ? 'Cancel' : '+ Note'}
              </button>
            </div>

            {personalNotesList.length > 0 ? (
              personalNotesList.map((note, idx) => (
                <blockquote key={note.id || idx} className="sidebar-personal-note-box">
                  <p className="note-text">"{note.contentBody}"</p>
                </blockquote>
              ))
            ) : (
              <blockquote className="sidebar-personal-note-box">
                <p className="note-text">
                  "Remember to always join or cancel subtasks before exiting. Never catch InterruptedException without restoring the interrupt flag on carrier threads."
                </p>
              </blockquote>
            )}

            {isAddingNote && (
              <form onSubmit={handleAddNote} className="add-note-form">
                <textarea
                  className="add-note-input"
                  placeholder="Type an engineering reflection..."
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  rows={3}
                />
                <button type="submit" className="save-note-btn">Save Note</button>
              </form>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

// Fallback generator for initial render / demo
function getFallbackChapter(slug) {
  return {
    id: 1,
    slug: slug || 'structured-concurrency',
    title: 'Structured Concurrency',
    description: 'Structured concurrency treats concurrent work as a hierarchy with explicit ownership.',
    course: { title: 'Java & Spring Architecture', slug: 'java-spring-lld' },
    codeComparisons: [
      {
        id: 1,
        title: 'Unstructured vs Structured Concurrency',
        beforeLabel: 'Unstructured concurrency',
        beforeLanguage: 'java',
        beforeCode: `// ❌ Unstructured Concurrency (CompletableFuture)
public Response handleCheckout(UUID orderId, UUID customerId) {
    CompletableFuture<Pricing> pricingFuture = CompletableFuture.supplyAsync(
        () -> pricingClient.calculate(orderId)
    );
    CompletableFuture<FraudScore> fraudFuture = CompletableFuture.supplyAsync(
        () -> fraudService.evaluate(customerId)
    );
    CompletableFuture<InventoryHold> inventoryFuture = CompletableFuture.supplyAsync(
        () -> inventoryClient.reserve(orderId)
    );

    // If fraudFuture fails, pricing and inventory continue running in background!
    return CompletableFuture.allOf(pricingFuture, fraudFuture, inventoryFuture)
        .thenApply(v -> new Response(pricingFuture.join(), fraudFuture.join(), inventoryFuture.join()))
        .join();
}`,
        afterLabel: 'Structured concurrency',
        afterLanguage: 'java',
        afterCode: `// ✅ Structured Concurrency (Java 21 StructuredTaskScope)
public Response handleCheckout(UUID orderId, UUID customerId) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Supplier<Pricing> pricing = scope.fork(() -> pricingClient.calculate(orderId));
        Supplier<FraudScore> fraud = scope.fork(() -> fraudService.evaluate(customerId));
        Supplier<InventoryHold> inventory = scope.fork(() -> inventoryClient.reserve(orderId));

        scope.join(); // Blocks until all finish OR one fails
        scope.throwIfFailed(OrderProcessingException::new); // Cascades instant cancel

        return new Response(pricing.get(), fraud.get(), inventory.get());
    } // AutoCloseable: ensures all virtual threads drained
}`,
        explanation: 'StructuredTaskScope guarantees that child tasks are terminated before the try-with-resources block exits.'
      }
    ],
    notes: [
      {
        id: 1,
        noteType: 'PersonalNote',
        contentBody: 'Remember to always join or cancel subtasks before exiting. Never catch InterruptedException without restoring the interrupt flag on carrier threads.'
      }
    ]
  };
}
