import { useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { CheckCircle2, CircleDot, Terminal } from 'lucide-react';
import { api } from '../../api/client';
import MarkdownBlock from './MarkdownBlock';
import './PracticeQuestions.css';
import './CodingAssignment.css';

const STATUS_BUTTONS = [
  { status: 'Attempted', label: 'Attempted', icon: CircleDot },
  { status: 'Solved', label: 'Solved', icon: CheckCircle2 }
];

function difficultyClass(difficulty) {
  return (difficulty || '').toLowerCase().replace(/[^a-z0-9]+/g, '-');
}

/**
 * A Python coding assignment from chapter.problems (language === 'python'):
 * statement, requirements, worked example, hints, run command and a reference
 * solution behind a <details>. Signed-in learners can mark it Attempted/Solved.
 */
export default function CodingAssignment({ problem, index, isAuthenticated = false }) {
  const location = useLocation();
  const [userStatus, setUserStatus] = useState(problem.userStatus || null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const revealRecordedRef = useRef(Boolean(problem.userStatus?.solutionRevealedAt));

  const currentStatus = userStatus?.status || 'NotStarted';

  const saveStatus = async (status, solutionRevealed) => {
    if (!isAuthenticated) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.me.setProblemStatus(problem.id, status, solutionRevealed);
      if (updated && typeof updated === 'object') setUserStatus(updated);
    } catch {
      setError('Your assignment status could not be saved. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusClick = (status) => {
    saveStatus(currentStatus === status ? 'NotStarted' : status);
  };

  const handleSolutionToggle = (event) => {
    if (!event.currentTarget.open || revealRecordedRef.current || !isAuthenticated) return;
    revealRecordedRef.current = true;
    // Revealing counts as at least an attempt; never downgrade a Solved status.
    saveStatus(currentStatus === 'NotStarted' ? 'Attempted' : currentStatus, true);
  };

  const isFromCourseTests = problem.sourceType === 'FROM_MATERIAL';

  return (
    <article className="chamber-problem-card coding-assignment" id={`assignment-${problem.slug || problem.id}`}>
      <div className="prb-card-header coding-assignment__header">
        <span className="prb-badge">ASSIGNMENT {String(index + 1).padStart(2, '0')}</span>
        <h4 className="prb-card-title">{problem.title}</h4>
        {problem.difficulty && (
          <span className={`prb-diff-tag diff-${difficultyClass(problem.difficulty)}`}>{problem.difficulty}</span>
        )}
        <span className={`practice-badge ${isFromCourseTests ? 'practice-badge--source' : 'practice-badge--ai'}`}>
          {isFromCourseTests ? 'From course tests' : 'Practice'}
        </span>
      </div>

      <div className="coding-assignment__body chamber-prose">
        <MarkdownBlock text={problem.problemStatement} />

        {problem.requirementsBody && (
          <>
            <h5 className="coding-assignment__label">Requirements</h5>
            <MarkdownBlock text={problem.requirementsBody} />
          </>
        )}

        {problem.workedExample && (
          <>
            <h5 className="coding-assignment__label">Worked example</h5>
            <MarkdownBlock text={problem.workedExample} />
          </>
        )}
      </div>

      {problem.hints && (
        <details className="coding-assignment__disclosure">
          <summary>Hints</summary>
          <div className="chamber-prose coding-assignment__disclosure-body">
            <MarkdownBlock text={problem.hints} />
          </div>
        </details>
      )}

      {problem.runCommand && (
        <div className="prb-maven-box coding-assignment__run">
          <Terminal size={13} aria-hidden="true" />
          <span className="maven-label">Run:</span>
          <code className="maven-cmd">{problem.runCommand}</code>
        </div>
      )}

      {problem.referenceSolution && (
        <details className="coding-assignment__disclosure coding-assignment__solution" onToggle={handleSolutionToggle}>
          <summary>Reveal reference solution</summary>
          <div className="chamber-prose coding-assignment__disclosure-body">
            <p className="coding-assignment__note">Try the tests first. Compare your design with this one rather than copying it.</p>
            <MarkdownBlock text={problem.referenceSolution} />
          </div>
        </details>
      )}

      <div className="coding-assignment__footer">
        {isAuthenticated ? (
          <div className="coding-assignment__status" role="group" aria-label={`Status for ${problem.title}`}>
            {STATUS_BUTTONS.map(({ status, label, icon: Icon }) => (
              <button
                key={status}
                type="button"
                className={`learning-button${currentStatus === status ? ' learning-button--run' : ''}`}
                aria-pressed={currentStatus === status}
                disabled={saving}
                onClick={() => handleStatusClick(status)}
              >
                <Icon size={13} /> {label}
              </button>
            ))}
            {userStatus?.solutionRevealedAt && (
              <span className="coding-assignment__meta">Reference solution viewed</span>
            )}
          </div>
        ) : (
          <Link to="/login" state={{ from: location }} className="learning-inline-link">
            Sign in to track this assignment
          </Link>
        )}
        {error && <p className="coding-assignment__error" role="alert">{error}</p>}
      </div>
    </article>
  );
}
