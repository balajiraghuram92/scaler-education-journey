import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { Plus, Shield, CheckCircle2, Circle, X } from 'lucide-react';
import CodeComparisonSwitcher from '../components/CodeComparisonSwitcher';
import ConceptCheck from '../components/learning/ConceptCheck';
import ImplementationExercise from '../components/learning/ImplementationExercise';
import PracticeQuestions from '../components/learning/PracticeQuestions';
import CodingAssignment from '../components/learning/CodingAssignment';
import MarkdownBlock, { MarkdownBlocks } from '../components/learning/MarkdownBlock';
import { buildContentSections } from '../components/learning/markdownParser';
import { getLessonInteractions } from '../data/lessonInteractions';
import { getLessonExerciseAssociation } from '../data/lessonExerciseAssociations';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { LoadingState, ErrorState, DevFixturesBanner } from '../components/common/StateViews';
import { markLearningPathOpened } from '../utils/recentLearningPaths';
import './ChapterReader.css';
import '../components/learning/learning-interactions.css';
import ChatWidget from '../components/common/ChatWidget';

// Position heartbeat cadence while the tab is visible (server caps secondsDelta at 300).
const HEARTBEAT_INTERVAL_MS = 20000;
const MAX_SECONDS_DELTA = 300;

function computeScrollPercent() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  if (scrollable <= 0) return 0;
  return Math.max(0, Math.min(100, Math.round((window.scrollY / scrollable) * 100)));
}

function splitPracticeQuestions(items) {
  const slices = { checkpoint: [], assignment: [], additional: [] };
  items.forEach((item) => {
    const category = (item.category || 'Assignment').toLowerCase();
    if (category === 'checkpoint') slices.checkpoint.push(item);
    else if (category === 'additional') slices.additional.push(item);
    else slices.assignment.push(item);
  });
  return slices;
}

function ChapterMarkdown({
  sections,
  conceptChecks,
  exerciseIds,
  expandedExerciseIds,
  onToggleExerciseExpanded,
  quiz,
  pythonProblems,
  isAuthenticated
}) {
  const hasConceptsSection = sections.some((section) => section.id === 'concepts-covered');
  const hasPracticeLoop = sections.some((section) => section.id === 'practice-loop');

  const checkpointBlock = quiz.checkpoint.length > 0 && (
    <PracticeQuestions
      id="checkpoint-quiz"
      questions={quiz.checkpoint}
      title="Checkpoint"
      eyebrow="CHECK YOUR UNDERSTANDING"
      isAuthenticated={isAuthenticated}
    />
  );

  const practiceBlock = (
    <>
      {exerciseIds?.map((exerciseId) => (
        <ImplementationExercise
          key={exerciseId}
          exerciseId={exerciseId}
          isExpanded={expandedExerciseIds.has(exerciseId)}
          onToggleExpand={() => onToggleExerciseExpanded(exerciseId)}
        />
      ))}
      {(quiz.assignment.length > 0 || quiz.additional.length > 0) && (
        <PracticeQuestions
          id="assignment-quiz"
          questions={quiz.assignment}
          additionalQuestions={quiz.additional}
          title="Assignment"
          eyebrow="PRACTICE LOOP — MULTIPLE CHOICE"
          additionalTitle="Additional practice"
          isAuthenticated={isAuthenticated}
        />
      )}
      {pythonProblems.length > 0 && (
        <div id="coding-assignments" className="chamber-coding-assignments">
          <p className="learning-eyebrow">PRACTICE LOOP — CODING ASSIGNMENTS</p>
          {pythonProblems.map((problem, index) => (
            <CodingAssignment key={problem.id} problem={problem} index={index} isAuthenticated={isAuthenticated} />
          ))}
        </div>
      )}
    </>
  );

  return (
    <>
      {sections.map((section) => (
        <section key={section.id} id={section.id} className="chapter-content-section">
          {section.title !== 'Introduction' && <h3 className="chamber-section-heading">{section.title}</h3>}
          <div className="chamber-prose">
            <MarkdownBlocks blocks={section.blocks} keyPrefix={section.id} />
          </div>

          {section.id === 'concepts-covered' && conceptChecks.map((check) => <ConceptCheck key={check.id} {...check} />)}
          {section.id === 'concepts-covered' && checkpointBlock}
          {section.id === 'practice-loop' && practiceBlock}
        </section>
      ))}

      {/* Chapters without these sections still get their questions and assignments. */}
      {!hasConceptsSection && checkpointBlock}
      {!hasPracticeLoop && practiceBlock}
    </>
  );
}

function CompletionControl({ isAuthenticated, isCompleted, saving, onToggle, loginState, variant }) {
  if (!isAuthenticated) {
    return (
      <Link to="/login" state={loginState} className={`chapter-completion-signin chapter-completion--${variant}`}>
        Sign in to track progress
      </Link>
    );
  }

  return (
    <button
      type="button"
      className={`chapter-completion-btn chapter-completion--${variant}${isCompleted ? ' is-complete' : ''}`}
      aria-pressed={isCompleted}
      disabled={saving}
      onClick={onToggle}
    >
      {isCompleted ? <CheckCircle2 size={15} /> : <Circle size={15} />}
      <span>{isCompleted ? 'Chapter complete' : 'Mark chapter complete'}</span>
    </button>
  );
}

export default function ChapterReader() {
  const { slug, verticalOrCourseSlug, moduleSlug, lessonSlug } = useParams();
  const location = useLocation();
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [chapter, setChapter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDevFixture, setIsDevFixture] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState('introduction');
  const [personalNotesList, setPersonalNotesList] = useState([]);
  const [newNoteText, setNewNoteText] = useState('');
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [noteError, setNoteError] = useState(null);
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [expandedExerciseIds, setExpandedExerciseIds] = useState(() => new Set());
  const [isCompleted, setIsCompleted] = useState(false);
  const [completionSaving, setCompletionSaving] = useState(false);
  const [completionError, setCompletionError] = useState(null);
  const [practiceItems, setPracticeItems] = useState(null);
  const [showResumeHint, setShowResumeHint] = useState(false);

  const positionRef = useRef({ sectionId: 'introduction', scrollPercent: 0 });
  const resumedChapterRef = useRef(null);

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

  const chapterCourseSlug = chapter?.course?.slug || verticalOrCourseSlug || '';
  const chapterModuleSlug = chapter?.module?.slug || moduleSlug || '';
  const chapterLessonSlug = chapter?.slug || targetSlug;

  const fetchChapter = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsDevFixture(false);
    setExpandedExerciseIds(new Set());
    setPracticeItems(null);
    setShowResumeHint(false);
    setNoteError(null);
    setCompletionError(null);

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
        setIsCompleted(Boolean(data.isCompleted));
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
        setIsCompleted(false);
      } else {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [targetSlug, verticalOrCourseSlug, moduleSlug, lessonSlug]);

  // Wait for the session probe so an expired access cookie is refreshed first;
  // otherwise the chapter would load without the learner's progress.
  useEffect(() => {
    if (authLoading) return;
    fetchChapter();
  }, [authLoading, fetchChapter]);

  // Practice questions are fetched once per chapter (and again on sign-in/out so
  // previous attempts appear), then sliced into Checkpoint / Assignment / Additional.
  useEffect(() => {
    if (!chapter?.id || authLoading || loading) return undefined;
    if (!chapterCourseSlug || !chapterModuleSlug || !chapterLessonSlug) {
      setPracticeItems([]);
      return undefined;
    }

    let cancelled = false;
    api.v2.getPracticeQuestions(chapterCourseSlug, chapterModuleSlug, chapterLessonSlug)
      .then((items) => {
        if (!cancelled) setPracticeItems(Array.isArray(items) ? items : []);
      })
      .catch((err) => {
        console.warn('Could not fetch practice questions:', err);
        if (!cancelled) setPracticeItems([]);
      });

    return () => {
      cancelled = true;
    };
  }, [chapter?.id, chapterCourseSlug, chapterModuleSlug, chapterLessonSlug, isAuthenticated, authLoading, loading]);

  const lessonInteractions = useMemo(
    () => getLessonInteractions(chapterCourseSlug, chapterModuleSlug, chapterLessonSlug),
    [chapterCourseSlug, chapterModuleSlug, chapterLessonSlug]
  );

  const quiz = useMemo(() => {
    if (practiceItems === null) return { checkpoint: [], assignment: [], additional: [] };
    if (practiceItems.length > 0) return splitPracticeQuestions(practiceItems);
    // No API questions for this lesson: fall back to the static, locally evaluated set.
    return { checkpoint: [], assignment: lessonInteractions?.practiceQuestions || [], additional: [] };
  }, [practiceItems, lessonInteractions]);

  // Record the open for signed-in learners.
  useEffect(() => {
    if (!isAuthenticated || !chapter?.id || isDevFixture || loading) return;
    api.me.recordVisit(chapter.id).catch((err) => console.warn('Could not record chapter visit:', err));
  }, [chapter?.id, isAuthenticated, isDevFixture, loading]);

  // Resume: scroll to the URL hash or the saved section once per chapter load.
  useEffect(() => {
    if (!chapter?.id || loading) return undefined;
    if (resumedChapterRef.current === chapter.id) return undefined;
    resumedChapterRef.current = chapter.id;

    const hashTarget = decodeURIComponent((location.hash || '').replace(/^#/, ''));
    const savedProgress = isAuthenticated ? chapter.userProgress : null;
    const savedSection = savedProgress?.lastSectionId || null;
    const target = hashTarget || savedSection;
    const savedPercent = savedProgress?.scrollPercent || 0;

    const timer = window.setTimeout(() => {
      const element = target ? document.getElementById(target) : null;
      if (element) {
        element.scrollIntoView?.({ block: 'start' });
        if (savedSection && target === savedSection && target !== 'introduction') setShowResumeHint(true);
      } else if (!hashTarget && savedPercent > 5) {
        const scrollable = document.documentElement.scrollHeight - window.innerHeight;
        window.scrollTo?.({ top: Math.round((scrollable * savedPercent) / 100) });
        setShowResumeHint(true);
      }
    }, 80);

    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chapter?.id, loading]);

  // ScrollSpy: active section + last known reading position for heartbeats.
  useEffect(() => {
    if (!chapter || loading) return undefined;

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
      positionRef.current = { sectionId: currentId, scrollPercent: computeScrollPercent() };
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [chapter, loading]);

  // Position heartbeats, counting only time while the tab is visible.
  useEffect(() => {
    if (!isAuthenticated || !chapter?.id || isDevFixture || loading) return undefined;

    const lessonId = chapter.id;
    let visibleSince = document.visibilityState === 'visible' ? Date.now() : null;

    const takeSeconds = () => {
      if (visibleSince === null) return 0;
      const seconds = Math.floor((Date.now() - visibleSince) / 1000);
      visibleSince += seconds * 1000;
      return Math.min(seconds, MAX_SECONDS_DELTA);
    };
    const snapshot = (secondsDelta) => ({ ...positionRef.current, secondsDelta });

    const intervalId = window.setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      api.me.updatePosition(lessonId, snapshot(takeSeconds())).catch(() => null);
    }, HEARTBEAT_INTERVAL_MS);

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        api.me.sendPositionBeacon(lessonId, snapshot(takeSeconds()));
        visibleSince = null;
      } else {
        visibleSince = Date.now();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.clearInterval(intervalId);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      api.me.sendPositionBeacon(lessonId, snapshot(takeSeconds()));
    };
  }, [chapter?.id, isAuthenticated, isDevFixture, loading]);

  const handleToggleComplete = async () => {
    if (!chapter?.id || completionSaving) return;
    setCompletionSaving(true);
    setCompletionError(null);
    try {
      const result = await api.me.setLessonCompletion(chapter.id, !isCompleted);
      setIsCompleted(typeof result?.isCompleted === 'boolean' ? result.isCompleted : !isCompleted);
    } catch (err) {
      console.error('Failed to update chapter completion:', err);
      setCompletionError('Progress could not be saved. Please try again.');
    } finally {
      setCompletionSaving(false);
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNoteText.trim() || !chapter || isSavingNote) return;

    setIsSavingNote(true);
    setNoteError(null);
    try {
      const res = await api.notes.create(chapter.id, {
        title: 'Field Reflection',
        contentBody: newNoteText.trim(),
        anchorSection: activeSectionId
      });
      setPersonalNotesList((prev) => [res, ...prev]);
      setNewNoteText('');
      setIsAddingNote(false);
    } catch (err) {
      console.error('Failed to save note:', err);
      setNoteError('Your note could not be saved. Please try again.');
    } finally {
      setIsSavingNote(false);
    }
  };

  const toggleExerciseExpanded = useCallback((exerciseId) => setExpandedExerciseIds((current) => {
    const next = new Set(current);
    if (next.has(exerciseId)) {
      next.delete(exerciseId);
    } else {
      next.add(exerciseId);
    }
    return next;
  }), []);

  if (loading || authLoading) {
    return <LoadingState message="Opening manuscript chapter chamber..." />;
  }

  if (error || !chapter) {
    return <ErrorState error={error} onRetry={fetchChapter} title="Chapter Not Available" />;
  }

  const lessonExercise = getLessonExerciseAssociation(chapterCourseSlug, chapterModuleSlug, chapterLessonSlug);
  const problems = chapter.problems || [];
  const pythonProblems = problems.filter((problem) => (problem.language || '').toLowerCase() === 'python');
  const javaProblems = problems.filter((problem) => (problem.language || '').toLowerCase() !== 'python');
  const courseTitle = chapter.course?.title || 'Curriculum pathway';
  const loginState = { from: location };

  const tocItems = [
    ...contentSections.map((section) => ({ id: section.id, label: section.title, level: 1 })),
    ...(chapter.codeComparisons?.length > 0 ? [{ id: 'code-comparison', label: 'Code comparison', level: 1 }] : []),
    ...(chapter.diagrams?.length > 0 ? [{ id: 'architecture-hierarchy', label: 'Architecture diagram', level: 1 }] : []),
    ...(javaProblems.length > 0 ? [{ id: 'practice-problems', label: 'Practice problems', level: 1 }] : [])
  ];

  return (
    <div className={`chapter-reader-page${expandedExerciseIds.size > 0 ? ' chapter-reader-page--exercise-expanded' : ''}`}>
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
                      className={`sibling-link ${sib.id === chapter.id ? 'is-current' : ''}${sib.isCompleted ? ' is-completed' : ''}`}
                    >
                      {sib.isCompleted && <CheckCircle2 size={12} className="sibling-done-icon" aria-label="Completed" />}
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
              {courseTitle}
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

          {showResumeHint && (
            <div className="chapter-resume-hint" role="status">
              <span>Resumed where you left off.</span>
              <button
                type="button"
                className="learning-text-button"
                onClick={() => {
                  setShowResumeHint(false);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              >
                Start from the top
              </button>
              <button
                type="button"
                className="chapter-resume-hint__dismiss"
                onClick={() => setShowResumeHint(false)}
                aria-label="Dismiss resume notice"
              >
                <X size={14} />
              </button>
            </div>
          )}

          <ChapterMarkdown
            sections={contentSections}
            conceptChecks={lessonInteractions?.conceptChecks || []}
            exerciseIds={lessonExercise?.exerciseIds}
            expandedExerciseIds={expandedExerciseIds}
            onToggleExerciseExpanded={toggleExerciseExpanded}
            quiz={quiz}
            pythonProblems={pythonProblems}
            isAuthenticated={isAuthenticated}
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

          {/* Java problems keep the Maven verification card; Python ones render in the practice loop. */}
          {javaProblems.length > 0 && (
            <section id="practice-problems" className="chapter-content-section">
              <h3 className="chamber-section-heading">Verification &amp; Test Suite Verification</h3>
              <div className="chamber-problems-stack">
                {javaProblems.map((prb, idx) => (
                  <div key={prb.id} className="chamber-problem-card">
                    <div className="prb-card-header">
                      <span className="prb-badge">{prb.packageName || `PROBLEM ${idx + 1}`}</span>
                      <h4 className="prb-card-title">{prb.title}</h4>
                      <span className={`prb-diff-tag diff-${prb.difficulty?.toLowerCase()}`}>{prb.difficulty}</span>
                    </div>
                    {prb.problemStatement && (
                      <MarkdownBlock text={prb.problemStatement} className="prb-statement" />
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

          <div className="chamber-completion-row">
            <CompletionControl
              isAuthenticated={isAuthenticated}
              isCompleted={isCompleted}
              saving={completionSaving}
              onToggle={handleToggleComplete}
              loginState={loginState}
              variant="footer"
            />
            {completionError && <span className="chamber-completion-error" role="alert">{completionError}</span>}
          </div>

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
            <h5 className="sidebar-meta-title">Your progress</h5>
            <CompletionControl
              isAuthenticated={isAuthenticated}
              isCompleted={isCompleted}
              saving={completionSaving}
              onToggle={handleToggleComplete}
              loginState={loginState}
              variant="sidebar"
            />
          </div>

          <div className="sidebar-hairline-divider" />

          <div className="sidebar-meta-block">
            <h5 className="sidebar-meta-title">Pathway</h5>
            <Link to={`/chapters/${chapterCourseSlug}`} className="sidebar-meta-link">
              {courseTitle}
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
              {isAuthenticated && (
                <button
                  type="button"
                  className="add-note-btn"
                  onClick={() => {
                    setIsAddingNote(!isAddingNote);
                    setNoteError(null);
                  }}
                >
                  {isAddingNote ? 'Cancel' : '+ Note'}
                </button>
              )}
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

            {!isAuthenticated && (
              <Link to="/login" state={loginState} className="sidebar-meta-link">
                Sign in to keep personal notes
              </Link>
            )}

            {isAuthenticated && isAddingNote && (
              <form onSubmit={handleAddNote} className="add-note-form">
                <textarea
                  className="add-note-input"
                  placeholder="Type an engineering reflection..."
                  value={newNoteText}
                  onChange={(e) => setNewNoteText(e.target.value)}
                  rows={3}
                />
                {noteError && <span className="add-note-error" role="alert">{noteError}</span>}
                <button type="submit" className="save-note-btn" disabled={isSavingNote}>
                  {isSavingNote ? 'Saving...' : 'Save Note'}
                </button>
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
                <span className="upcoming-module-tag">{chapter.nextChapter?.moduleTitle || courseTitle}</span>
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

      <ChatWidget lessonId={chapter?.id} lessonTitle={chapter?.title} />
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
