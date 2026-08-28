import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Plus, Calendar, Shield } from 'lucide-react';
import CodeComparisonSwitcher from '../components/CodeComparisonSwitcher';
import ConceptCheck from '../components/learning/ConceptCheck';
import ImplementationExercise from '../components/learning/ImplementationExercise';
import PracticeQuestions from '../components/learning/PracticeQuestions';
import { getLessonInteractions } from '../data/lessonInteractions';
import { getLessonExerciseAssociation } from '../data/lessonExerciseAssociations';
import { api } from '../api/client';
import { LoadingState, ErrorState, DevFixturesBanner } from '../components/common/StateViews';
import { markLearningPathOpened } from '../utils/recentLearningPaths';
import './ChapterReader.css';
import '../components/learning/learning-interactions.css';

function slugifyHeading(value, usedIds) {
  const base = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'section';
  const count = usedIds.get(base) || 0;
  usedIds.set(base, count + 1);
  return count === 0 ? base : `${base}-${count + 1}`;
}

function formatInline(text) {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean).map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) return <strong key={`${part}-${index}`}>{part.slice(2, -2)}</strong>;
    if (part.startsWith('`') && part.endsWith('`')) return <code key={`${part}-${index}`}>{part.slice(1, -1)}</code>;
    return <React.Fragment key={`${part}-${index}`}>{part}</React.Fragment>;
  });
}

function buildContentSections(contentBody) {
  const fallback = 'This chapter is being prepared. Return to the pathway for the latest learning outline.';
  const lines = (contentBody || fallback).replace(/\r\n/g, '\n').split('\n');
  const usedIds = new Map([['introduction', 1]]);
  const sections = [{ id: 'introduction', title: 'Introduction', blocks: [] }];
  let current = sections[0];
  let paragraph = [];
  let list = [];
  let listType = null;
  let codeLines = [];
  let inCodeBlock = false;

  const flushParagraph = () => {
    if (paragraph.length > 0) {
      current.blocks.push({ type: 'paragraph', text: paragraph.join(' ') });
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list.length > 0) {
      current.blocks.push({ type: listType, items: list });
      list = [];
      listType = null;
    }
  };
  const flushCode = () => {
    if (codeLines.length > 0) {
      current.blocks.push({ type: 'code', text: codeLines.join('\n') });
      codeLines = [];
    }
  };
  const flushBlocks = () => {
    flushParagraph();
    flushList();
    flushCode();
  };

  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    if (line.startsWith('```')) {
      if (inCodeBlock) flushCode();
      else flushParagraph();
      inCodeBlock = !inCodeBlock;
      return;
    }
    if (inCodeBlock) {
      codeLines.push(rawLine);
      return;
    }
    if (/^#\s+/.test(line)) {
      flushBlocks();
      return;
    }
    if (/^##\s+/.test(line)) {
      flushBlocks();
      const title = line.replace(/^##\s+/, '');
      current = { id: slugifyHeading(title, usedIds), title, blocks: [] };
      sections.push(current);
      return;
    }
    if (/^###\s+/.test(line)) {
      flushBlocks();
      current.blocks.push({ type: 'subheading', text: line.replace(/^###\s+/, '') });
      return;
    }
    const unordered = line.match(/^[-*]\s+(.+)/);
    const ordered = line.match(/^\d+\.\s+(.+)/);
    if (unordered || ordered) {
      const nextType = ordered ? 'ordered-list' : 'unordered-list';
      if (listType && listType !== nextType) flushList();
      flushParagraph();
      listType = nextType;
      list.push((unordered || ordered)[1]);
      return;
    }
    if (!line) {
      flushParagraph();
      flushList();
      return;
    }
    paragraph.push(line);
  });

  flushBlocks();
  return sections.filter((section) => section.blocks.length > 0);
}

function ChapterMarkdown({ sections, interactions, exerciseId, isExerciseExpanded, onToggleExerciseExpanded }) {
  const conceptChecks = interactions?.conceptChecks || [];
  const practiceQuestions = interactions?.practiceQuestions || [];

  return sections.map((section) => (
    <React.Fragment key={section.id}>
      <section id={section.id} className="chapter-content-section">
        {section.title !== 'Introduction' && <h3 className="chamber-section-heading">{section.title}</h3>}
        <div className="chamber-prose">
          {section.blocks.map((block, index) => {
            if (block.type === 'subheading') return <h4 key={`${section.id}-${index}`} className="chamber-subheading">{block.text}</h4>;
            if (block.type === 'unordered-list') return <ul key={`${section.id}-${index}`} className="chapter-markdown-list">{block.items.map((item, itemIndex) => <li key={`${item}-${itemIndex}`}>{formatInline(item)}</li>)}</ul>;
            if (block.type === 'ordered-list') return <ol key={`${section.id}-${index}`} className="chapter-markdown-list chapter-markdown-list--ordered">{block.items.map((item, itemIndex) => <li key={`${item}-${itemIndex}`}>{formatInline(item)}</li>)}</ol>;
            if (block.type === 'code') return <pre key={`${section.id}-${index}`} className="chapter-code-block"><code>{block.text}</code></pre>;
            return <p key={`${section.id}-${index}`}>{formatInline(block.text)}</p>;
          })}
        </div>
      </section>

      {section.id === 'concepts-covered' && conceptChecks.map((check) => <ConceptCheck key={check.id} {...check} />)}
      {section.id === 'practice-loop' && exerciseId && (
        <ImplementationExercise
          key={exerciseId}
          exerciseId={exerciseId}
          isExpanded={isExerciseExpanded}
          onToggleExpand={onToggleExerciseExpanded}
        />
      )}
      {section.id === 'practice-loop' && practiceQuestions?.length > 0 && (
        <PracticeQuestions questions={practiceQuestions} />
      )}
    </React.Fragment>
  ));
}

export default function ChapterReader() {
  const { slug, verticalOrCourseSlug, moduleSlug, lessonSlug } = useParams();

  const [chapter, setChapter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDevFixture, setIsDevFixture] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState('introduction');
  const [personalNotesList, setPersonalNotesList] = useState([]);
  const [newNoteText, setNewNoteText] = useState('');
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [isExerciseExpanded, setIsExerciseExpanded] = useState(false);

  // Resolved lookup slug
  const targetSlug = useMemo(() => {
    if (lessonSlug) return lessonSlug;
    if (slug) return slug;
    return 'structured-concurrency'; // default flagship
  }, [slug, lessonSlug]);

  const contentSections = useMemo(
    () => buildContentSections(chapter?.contentBody),
    [chapter?.contentBody]
  );

  const fetchChapter = async () => {
    setLoading(true);
    setError(null);
    setIsDevFixture(false);
    setIsExerciseExpanded(false);

    try {
      let data = null;
      if (verticalOrCourseSlug && moduleSlug && lessonSlug) {
        data = await api.v2.getChapter(verticalOrCourseSlug, moduleSlug, lessonSlug);
      } else {
        data = await api.legacy.getChapterBySlug(targetSlug);
      }

      if (data) {
        setChapter(data);
        setPersonalNotesList(data.notes || []);
        if (verticalOrCourseSlug && moduleSlug && lessonSlug) {
          const verifiedPathSlug = data.course?.slug || verticalOrCourseSlug;
          if (typeof verifiedPathSlug === 'string' && verifiedPathSlug.trim()) {
            markLearningPathOpened(verifiedPathSlug);
          }
        }
      }
    } catch (err) {
      console.warn('API fetch warning for chapter:', err);
      if (import.meta.env.VITE_ENABLE_DEV_FIXTURES === 'true') {
        setIsDevFixture(true);
        const fallbackData = getFallbackChapter(targetSlug);
        setChapter(fallbackData);
        setPersonalNotesList(fallbackData.notes || []);
      } else {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChapter();
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
      const res = await api.post(`/api/lessons/${chapter.id}/notes`, newNote);
      setPersonalNotesList(prev => [res, ...prev]);
      setNewNoteText('');
      setIsAddingNote(false);
    } catch (err) {
      console.error('Failed to save note:', err);
      // Fallback local reflection
      setPersonalNotesList(prev => [{
        id: Date.now(),
        title: 'Field Reflection (Local)',
        contentBody: newNoteText.trim(),
        createdAt: new Date().toISOString()
      }, ...prev]);
      setNewNoteText('');
      setIsAddingNote(false);
    }
  };

  if (loading) {
    return <LoadingState message="Opening manuscript chapter chamber..." />;
  }

  if (error || !chapter) {
    return <ErrorState error={error} onRetry={fetchChapter} title="Chapter Not Available" />;
  }

  const chapterCourseSlug = chapter.course?.slug || chapter.course?.courseSlug || 'java-spring-lld';
  const lessonInteractions = getLessonInteractions(
    chapterCourseSlug,
    chapter.module?.slug || moduleSlug || '',
    chapter.slug || targetSlug
  );
  const lessonExercise = getLessonExerciseAssociation(
    chapterCourseSlug,
    chapter.module?.slug || moduleSlug || '',
    chapter.slug || targetSlug
  );

  const tocItems = [
    ...contentSections.map((section) => ({ id: section.id, label: section.title, level: 1 })),
    ...(chapter.codeComparisons?.length > 0 ? [{ id: 'code-comparison', label: 'Code comparison', level: 1 }] : []),
    ...(chapter.diagrams?.length > 0 ? [{ id: 'architecture-hierarchy', label: 'Architecture diagram', level: 1 }] : []),
    ...(chapter.problems?.length > 0 ? [{ id: 'practice-problems', label: 'Practice problems', level: 1 }] : [])
  ];

  return (
    <div className={`chapter-reader-page${isExerciseExpanded ? ' chapter-reader-page--exercise-expanded' : ''}`}>
      {isDevFixture && <DevFixturesBanner />}
      <div className="chapter-reader-top-strip">
        <div className="top-strip-inner">
          <span className="panel-tag">PANEL D: CURRICULUM CHAPTER</span>
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
                      to={`/chapter/${sib.fullSlug || sib.slug}`}
                      className={`sibling-link ${sib.id === chapter.id ? 'is-current' : ''}`}
                    >
                      {sib.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Quick Admin TOC Action */}
          <div className="toc-admin-footer">
            <Link to="/curriculum-import" className="toc-map-chapter-btn" title="Map or import new chapter">
              <Plus size={13} />
              <span>Map New Chapter</span>
            </Link>
          </div>
        </aside>

        {/* ========================================================= */}
        {/* COLUMN 2: CENTER READING CHAMBER                          */}
        {/* ========================================================= */}
        <main className="chapter-reading-chamber">
          {/* Breadcrumbs */}
          <nav className="chamber-breadcrumb-trail">
            <Link to="/chapters" className="breadcrumb-crumb">Chapters</Link>
            <span className="breadcrumb-sep">→</span>
            <Link to={`/chapters/${chapterCourseSlug}`} className="breadcrumb-crumb">
              {chapter.course?.title || 'Java & Spring Architecture'}
            </Link>
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

          <ChapterMarkdown
            sections={contentSections}
            interactions={lessonInteractions}
            exerciseId={lessonExercise?.exerciseId}
            isExerciseExpanded={isExerciseExpanded}
            onToggleExerciseExpanded={() => setIsExerciseExpanded((current) => !current)}
          />

          {chapter.codeComparisons?.length > 0 && (
            <section id="code-comparison" className="chapter-content-section">
              <h3 className="chamber-section-heading">Code comparison</h3>
              <CodeComparisonSwitcher comparisons={chapter.codeComparisons} />
            </section>
          )}

          {chapter.diagrams?.length > 0 && (
            <section id="architecture-hierarchy" className="chapter-content-section">
              <h3 className="chamber-section-heading">Architecture diagram</h3>
              {chapter.diagrams.map((diag) => (
                <div key={diag.id} className="chamber-diagram-card">
                  <div className="chamber-svg-canvas" dangerouslySetInnerHTML={{ __html: diag.svgContent }} />
                  {diag.caption && <p className="chamber-diagram-caption">{diag.caption}</p>}
                </div>
              ))}
            </section>
          )}

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
              <Link to={`/chapter/${chapter.previousChapter.fullSlug || chapter.previousChapter.slug}`} className="chamber-nav-btn prev">
                <span className="nav-dir">← Previous Chapter</span>
                <span className="nav-title">{chapter.previousChapter.title}</span>
              </Link>
            ) : <div />}

            {chapter.nextChapter ? (
              <Link to={`/chapter/${chapter.nextChapter.fullSlug || chapter.nextChapter.slug}`} className="chamber-nav-btn next">
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
          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Pathway</h5>
            <Link to={`/chapters/${chapterCourseSlug}`} className="sidebar-meta-link">
              {chapter.course?.title || 'Curriculum pathway'}
            </Link>
          </div>

          <div className="sidebar-hairline-divider" />

          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Module</h5>
            <span className="sidebar-meta-text">{chapter.module?.title || 'Module context is being prepared.'}</span>
          </div>

          <div className="sidebar-hairline-divider" />

          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Further reading</h5>
            <ul className="sidebar-reading-list">
              {chapter.horstmannRef && (
                <li>
                  <a href={chapter.horstmannRef} target="_blank" rel="noreferrer" className="sidebar-meta-link">
                    Primary reference
                  </a>
                </li>
              )}
              {chapter.relatedLessons?.map((lesson) => (
                <li key={`${lesson.targetSlug || lesson.targetTitle}-${lesson.relationshipType}`}>
                  <span className="sidebar-meta-text">{lesson.relationshipType}: {lesson.targetTitle}</span>
                </li>
              ))}
              {!chapter.horstmannRef && !chapter.relatedLessons?.length && (
                <li><span className="sidebar-meta-text">Keep a field note with the most useful reference you find.</span></li>
              )}
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
                  "Add a short field note after trying this chapter in a real system."
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

          <div className="sidebar-hairline-divider" />

          {/* Upcoming Session & Curriculum Admin Trigger */}
          <div className="sidebar-meta-block sidebar-upcoming-block">
            <div className="sidebar-title-row">
              <h5 className="sidebar-meta-title">Upcoming session</h5>
              <Link
                to="/curriculum-import"
                className="sidebar-admin-plus-btn"
                title="Map New Chapter (Admin Portal)"
              >
                <Plus size={13} />
                <span>Map Chapter</span>
              </Link>
            </div>

            <div className="sidebar-upcoming-card">
              <div className="upcoming-tag-row">
                <span className="upcoming-badge">Next Session</span>
                <span className="upcoming-module-tag">{chapter.course?.title || 'Java & Spring'}</span>
              </div>
              <p className="upcoming-title">
                {chapter.nextChapter ? chapter.nextChapter.title : 'Return to the pathway for the next chapter'}
              </p>
              <p className="upcoming-desc">
                {chapter.nextChapter
                  ? 'Continue the sequence when you are ready to apply this chapter in a broader workflow.'
                  : 'Finish the practice loop, capture a field note, and choose the next module from the pathway.'}
              </p>
              <div className="upcoming-admin-hint">
                <Shield size={12} className="admin-lock-icon" />
                <span>Authenticated Admin Action · IAM Protected</span>
              </div>
            </div>
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
