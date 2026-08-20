import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { 
  CheckCircle2, Circle, HelpCircle, ChevronDown, ChevronUp, Copy, Check, 
  Terminal, Sparkles, BookOpen, Layers, Code2, PlusCircle, RefreshCw,
  Award, FileText, CheckCircle
} from 'lucide-react';
import './JavaPracticeDashboard.css';

export default function JavaPracticeDashboard({ vertical, onUpdate }) {
  const [courseData, setCourseData] = useState(null);
  const [selectedModuleId, setSelectedModuleId] = useState(null);
  const [selectedLessonId, setSelectedLessonId] = useState(null);
  const [lessonDetail, setLessonDetail] = useState(null);
  const [isStudyGuideOpen, setIsStudyGuideOpen] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeProblemId, setActiveProblemId] = useState(null);

  const fetchCourseData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/courses/java-spring-lld`, {
        headers: {
          'x-api-key': import.meta.env.VITE_API_KEY || ''
        }
      });
      if (res.ok) {
        const data = await res.json();
        setCourseData(data);
        if (data.modules && data.modules.length > 0) {
          const initialMod = data.modules[0];
          setSelectedModuleId(initialMod.id);
          if (initialMod.lessons && initialMod.lessons.length > 0) {
            // Default to Lesson 3 (OOP-2) if present, otherwise first lesson
            const oop2 = initialMod.lessons.find(l => l.slug.includes('oop-2')) || initialMod.lessons[0];
            setSelectedLessonId(oop2.id);
          }
        }
      }
    } catch (err) {
      console.error('Failed to fetch course data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCourseData();
  }, [fetchCourseData]);

  // Fetch full details of the active lesson
  useEffect(() => {
    if (!selectedLessonId) return;

    fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/lessons/${selectedLessonId}`, {
      headers: {
        'x-api-key': import.meta.env.VITE_API_KEY || ''
      }
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) {
          setLessonDetail(data);
          if (data.problems && data.problems.length > 0) {
            setActiveProblemId(data.problems[0].id);
          }
        }
      })
      .catch(err => console.error('Failed to fetch lesson detail:', err));
  }, [selectedLessonId]);

  const toggleProblemStatus = async (problemId) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/problems/${problemId}/progress`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': import.meta.env.VITE_API_KEY || ''
        }
      });
      if (res.ok) {
        setLessonDetail(prev => {
          if (!prev) return null;
          return {
            ...prev,
            problems: prev.problems.map(p => 
              p.id === problemId ? { ...p, isCompleted: !p.isCompleted } : p
            )
          };
        });
        fetchCourseData();
        if (onUpdate) onUpdate();
      }
    } catch (err) {
      console.error('Failed to toggle problem progress:', err);
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const scrollToProblem = (id) => {
    setActiveProblemId(id);
    const el = document.getElementById(`problem-card-${id}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (loading && !courseData) {
    return (
      <div className="java-header-card text-center" style={{ padding: '60px' }}>
        <RefreshCw size={36} className="spin" style={{ color: '#2563eb', margin: '0 auto 16px' }} />
        <p style={{ color: '#64748b' }}>Loading Java & Spring Architecture Workspace...</p>
      </div>
    );
  }

  const problems = lessonDetail?.problems || [];
  const resources = lessonDetail?.resources || [];
  const completedProblemsCount = problems.filter(p => p.isCompleted).length;
  const problemsProgress = problems.length > 0 ? Math.round((completedProblemsCount / problems.length) * 100) : 0;

  const currentModule = courseData?.modules?.find(m => m.id === selectedModuleId);

  return (
    <div className="java-dashboard">
      {/* 1. Header Card with Title & Quick Actions */}
      <div className="java-header-card">
        <div className="java-header-top">
          <div className="java-title-group">
            <h1>{lessonDetail?.title || "Java & Spring Architecture"}</h1>
            <div className="java-subtitle">
              <span>{currentModule?.title || "OOP Foundations"}</span> &middot; 
              <span> {lessonDetail?.horstmannRef ? `Ref: ${lessonDetail.horstmannRef}` : "Scaler Java LLD 1"}</span>
            </div>
          </div>
          <div className="java-header-actions">
            <Link 
              to={lessonDetail?.slug ? `/chapter/${lessonDetail.slug}` : '/chapter/structured-concurrency'}
              className="java-btn-action"
              style={{ textDecoration: 'none', background: '#F8F6F0', color: '#2C5E55', borderColor: '#2C5E55' }}
            >
              <BookOpen size={16} />
              <span>Chapter Reader →</span>
            </Link>
            <button 
              className="java-btn-action" 
              onClick={() => setIsStudyGuideOpen(!isStudyGuideOpen)}
            >
              <Layers size={16} />
              <span>{isStudyGuideOpen ? "Hide Study Guide" : "15 Study Guide Topics"}</span>
            </button>
            <button className="java-btn-action java-btn-primary" onClick={fetchCourseData}>
              <RefreshCw size={14} className={loading ? 'spin' : ''} />
              <span>Sync Progress</span>
            </button>
          </div>
        </div>

        {/* Module Selector Pills */}
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px', margin: '16px 0 8px' }}>
          {courseData?.modules?.map(m => (
            <button
              key={m.id}
              onClick={() => {
                setSelectedModuleId(m.id);
                if (m.lessons && m.lessons.length > 0) {
                  setSelectedLessonId(m.lessons[0].id);
                }
              }}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '0.82rem',
                fontWeight: '600',
                border: '1px solid',
                borderColor: selectedModuleId === m.id ? '#2563eb' : '#e2e8f0',
                background: selectedModuleId === m.id ? '#eff6ff' : '#ffffff',
                color: selectedModuleId === m.id ? '#1d4ed8' : '#64748b',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s'
              }}
            >
              {m.badge || m.title}: {m.title}
            </button>
          ))}
        </div>

        {/* Lesson Selector Dropdown if module has multiple lessons */}
        {currentModule && currentModule.lessons?.length > 1 && (
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', padding: '6px 0 12px' }}>
            {currentModule.lessons.map(l => (
              <button
                key={l.id}
                onClick={() => setSelectedLessonId(l.id)}
                style={{
                  padding: '5px 12px',
                  borderRadius: '99px',
                  fontSize: '0.78rem',
                  fontWeight: selectedLessonId === l.id ? '700' : '500',
                  border: '1px solid',
                  borderColor: selectedLessonId === l.id ? '#3b82f6' : '#cbd5e1',
                  background: selectedLessonId === l.id ? '#3b82f6' : '#f8fafc',
                  color: selectedLessonId === l.id ? '#ffffff' : '#475569',
                  cursor: 'pointer'
                }}
              >
                {l.title.split('—')[0].trim()}
              </button>
            ))}
          </div>
        )}

        {/* Progress Bar */}
        <div className="java-progress-box">
          <div className="java-stat-text">
            <span>
              {completedProblemsCount} / {problems.length} problems green 
              <small> &mdash; {completedProblemsCount} of {problems.length} solved ({problemsProgress}%)</small>
            </span>
            <span style={{ fontSize: '0.9rem', color: problemsProgress === 100 ? '#10b981' : '#2563eb' }}>
              {problemsProgress === 100 ? "✓ Suite Fully Mastered" : "In Progress"}
            </span>
          </div>
          <div className="java-bar-track">
            <div className="java-bar-fill" style={{ width: `${problemsProgress}%` }}></div>
          </div>
        </div>

        {/* Problem Navigation Chips */}
        {problems.length > 0 && (
          <div className="java-nav-chips">
            {problems.map((p, idx) => (
              <button
                key={p.id}
                onClick={() => scrollToProblem(p.id)}
                className={`java-chip ${p.isCompleted ? 'pass' : 'pending'} ${activeProblemId === p.id ? 'active' : ''}`}
              >
                <span className="java-chip-dot"></span>
                <span>{p.title}</span>
                <span className="java-chip-badge">{p.difficulty}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 2. Collapsible 15-Topic Study Guide */}
      {resources.length > 0 && (
        <div className="java-study-guide">
          <div 
            className="java-study-guide-header"
            onClick={() => setIsStudyGuideOpen(!isStudyGuideOpen)}
          >
            <div className="java-study-guide-title">
              <BookOpen size={20} style={{ color: '#2563eb' }} />
              <span>Study Guide &mdash; All 15 OOP-2 Topics Explained with Worked Examples</span>
            </div>
            {isStudyGuideOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>

          {isStudyGuideOpen && (
            <div className="java-study-guide-body">
              <div className="java-topics-grid">
                {resources.map(res => (
                  <div key={res.id} className="java-topic-card">
                    <h4 className="java-topic-title">
                      <Code2 size={16} style={{ color: '#2563eb' }} />
                      {res.title}
                    </h4>
                    <div className="java-topic-body">{res.contentBody}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Problem Cards Grid / Split View */}
      {problems.length === 0 ? (
        <div className="java-header-card text-center" style={{ padding: '40px' }}>
          <FileText size={36} style={{ color: '#94a3b8', margin: '0 auto 12px' }} />
          <h3>No practice problems assigned to this lecture</h3>
          <p style={{ color: '#64748b' }}>Select Lesson 3 (OOP-2) from the switcher above to explore the 5 practice problem suites.</p>
        </div>
      ) : (
        problems.map((problem) => (
          <div
            key={problem.id}
            id={`problem-card-${problem.id}`}
            className={`java-problem-card ${problem.isCompleted ? 'pass' : 'pending'}`}
          >
            {/* Problem Card Header */}
            <div className="java-card-head">
              <div>
                <div className="java-card-eyebrow">
                  {problem.packageName} &middot; <span className="java-diff-tag">{problem.difficulty}</span>
                </div>
                <h2 className="java-card-title">{problem.title}</h2>
                <div className="java-card-meta">
                  Test Suite: <code>{problem.testClassName}.java</code>
                </div>
              </div>

              <div className="java-card-status">
                <button
                  onClick={() => toggleProblemStatus(problem.id)}
                  className={`java-pill ${problem.isCompleted ? 'pass' : 'pending'}`}
                >
                  {problem.isCompleted ? <CheckCircle2 size={14} /> : <Circle size={14} />}
                  <span>{problem.isCompleted ? 'SOLVED / GREEN' : 'MARK SOLVED'}</span>
                </button>
              </div>
            </div>

            {/* Split View: Statement & Requirements vs Results/Assertions */}
            <div className="java-split-pane">
              {/* Left Pane: Problem Statement & Requirements */}
              <div className="java-statement-pane">
                <div className="java-section-header">
                  <BookOpen size={16} />
                  <span>Problem Statement</span>
                </div>
                <div className="java-statement-text">{problem.problemStatement}</div>

                <div className="java-section-header">
                  <Layers size={16} />
                  <span>Requirements & Constraints</span>
                </div>
                <div className="java-statement-text">{problem.requirementsBody}</div>

                {problem.workedExample && (
                  <div>
                    <div className="java-section-header">
                      <Code2 size={16} />
                      <span>Worked Example</span>
                    </div>
                    <div className="java-code-block">
                      <button
                        className="java-code-copy-btn"
                        onClick={() => copyToClipboard(problem.workedExample, `code-${problem.id}`)}
                      >
                        {copiedId === `code-${problem.id}` ? <Check size={12} /> : <Copy size={12} />}
                        <span>{copiedId === `code-${problem.id}` ? 'Copied' : 'Copy'}</span>
                      </button>
                      <pre><code>{problem.workedExample}</code></pre>
                    </div>
                  </div>
                )}

                {problem.hints && (
                  <div className="java-hints-drawer">
                    <strong>💡 Architectural Hints & Invariants:</strong>
                    <div style={{ marginTop: '4px', whiteSpace: 'pre-wrap' }}>{problem.hints}</div>
                  </div>
                )}
              </div>

              {/* Right Pane: Test Assertions & Grading Checklist */}
              <div className="java-result-pane">
                <div className="java-section-header">
                  <Terminal size={16} />
                  <span>JUnit 5 Test Suite Verification</span>
                </div>

                <ul className="java-tests-list">
                  <li className="java-test-item">
                    <CheckCircle2 size={16} style={{ color: problem.isCompleted ? '#10b981' : '#94a3b8' }} className="java-test-ico" />
                    <div>
                      <div className="java-test-name">testReflectionInvariants()</div>
                      <div className="java-test-desc">Verifies private final fields, accessor modifiers & class sealing</div>
                    </div>
                  </li>
                  <li className="java-test-item">
                    <CheckCircle2 size={16} style={{ color: problem.isCompleted ? '#10b981' : '#94a3b8' }} className="java-test-ico" />
                    <div>
                      <div className="java-test-name">testArgumentValidation()</div>
                      <div className="java-test-desc">Checks IllegalArgumentException for boundary & null inputs</div>
                    </div>
                  </li>
                  <li className="java-test-item">
                    <CheckCircle2 size={16} style={{ color: problem.isCompleted ? '#10b981' : '#94a3b8' }} className="java-test-ico" />
                    <div>
                      <div className="java-test-name">testDomainBehavior()</div>
                      <div className="java-test-desc">Validates calculations, copy semantics, and string formats</div>
                    </div>
                  </li>
                  <li className="java-test-item">
                    <CheckCircle2 size={16} style={{ color: problem.isCompleted ? '#10b981' : '#94a3b8' }} className="java-test-ico" />
                    <div>
                      <div className="java-test-name">testContractSymmetry()</div>
                      <div className="java-test-desc">Checks equals/hashCode reflexivity, symmetry and null-safety</div>
                    </div>
                  </li>
                </ul>

                <div className="java-quick-info">
                  <strong>Maven Test Command:</strong>
                  <div style={{ marginTop: '6px', fontFamily: 'monospace', fontSize: '0.8rem', background: '#ffffff', padding: '6px 8px', borderRadius: '4px', border: '1px solid #bfdbfe' }}>
                    mvn test -Dtest={problem.testClassName}
                  </div>
                </div>

                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                  <button
                    onClick={() => toggleProblemStatus(problem.id)}
                    style={{
                      width: '100%',
                      padding: '10px 16px',
                      borderRadius: '8px',
                      fontWeight: '600',
                      fontSize: '0.88rem',
                      border: 'none',
                      cursor: 'pointer',
                      background: problem.isCompleted ? '#f0fdf4' : '#2563eb',
                      color: problem.isCompleted ? '#166534' : '#ffffff',
                      border: problem.isCompleted ? '1px solid #bbf7d0' : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      transition: 'all 0.2s'
                    }}
                  >
                    {problem.isCompleted ? <CheckCircle size={16} /> : <Award size={16} />}
                    <span>{problem.isCompleted ? 'Completed (Click to Reset)' : 'Mark Problem Solved'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
