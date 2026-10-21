import { useCallback, useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, BarChart3, Laptop, LogOut, Target } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { formatDuration, timeAgo } from '../utils/timeAgo';
import './Profile.css';

const ACTIVITY_LABELS = {
  LessonOpened: 'Opened',
  LessonReopened: 'Returned to',
  LessonCompleted: 'Completed',
  McqAnswered: 'Answered a question in',
  ProblemAttempted: 'Attempted an assignment in',
  ProblemCompleted: 'Solved an assignment in',
  ProblemReopened: 'Reopened an assignment in',
  SolutionRevealed: 'Viewed a reference solution in'
};

export function describeUserAgent(userAgent) {
  if (!userAgent) return 'Unknown device';
  const ua = userAgent;
  let browser = 'Browser';
  if (/Edg\//.test(ua)) browser = 'Edge';
  else if (/OPR\//.test(ua)) browser = 'Opera';
  else if (/Firefox\//.test(ua)) browser = 'Firefox';
  else if (/Chrome\//.test(ua)) browser = 'Chrome';
  else if (/Safari\//.test(ua)) browser = 'Safari';
  else if (/curl|python|okhttp|axios|node/i.test(ua)) browser = 'API client';

  let os = '';
  if (/iPhone|iPad|iPod/.test(ua)) os = 'iOS';
  else if (/Android/.test(ua)) os = 'Android';
  else if (/Windows/.test(ua)) os = 'Windows';
  else if (/Mac OS X|Macintosh/.test(ua)) os = 'macOS';
  else if (/Linux/.test(ua)) os = 'Linux';

  return os ? `${browser} on ${os}` : browser;
}

function percent(part, whole) {
  if (!whole) return 0;
  return Math.round((part / whole) * 100);
}

function SectionHeading({ id, icon: Icon, kicker, title, children }) {
  return (
    <div className="profile-section-heading">
      <div>
        <span className="profile-kicker"><Icon size={13} aria-hidden="true" /> {kicker}</span>
        <h2 id={id}>{title}</h2>
      </div>
      {children}
    </div>
  );
}

function LearningSummary({ summary }) {
  const accuracy = percent(summary.totalMcqCorrect, summary.totalMcqAnswered);

  return (
    <section className="profile-learning-section" aria-labelledby="profile-summary-heading">
      <SectionHeading id="profile-summary-heading" icon={BarChart3} kicker="Learning summary" title="Your progress">
        <div className="profile-stat-row">
          <span><strong>{summary.totalLessonsCompleted}</strong> chapters completed</span>
          <span><strong>{summary.totalLessonsInProgress}</strong> in progress</span>
          <span><strong>{summary.totalMcqAnswered ? `${accuracy}%` : '—'}</strong> MCQ accuracy</span>
          <span><strong>{summary.assignmentsSolved}</strong> assignments solved</span>
          <span><strong>{formatDuration(summary.totalTimeSpentSeconds)}</strong> reading time</span>
        </div>
      </SectionHeading>

      {summary.courses?.length > 0 ? (
        <div className="profile-course-grid">
          {summary.courses.map((course) => {
            const courseAccuracy = percent(course.mcqCorrect, course.mcqAnswered);
            return (
              <Link key={course.courseId} to={`/chapters/${course.courseSlug}`} className="profile-course-card">
                <div className="profile-course-topline">
                  <span className="profile-course-title">{course.courseTitle}</span>
                  <span className="profile-course-percent">{course.progressPercentage}%</span>
                </div>
                <div className="profile-progress-bar" aria-hidden="true">
                  <span style={{ width: `${Math.min(100, course.progressPercentage)}%` }} />
                </div>
                <dl className="profile-course-stats">
                  <div><dt>Completed</dt><dd>{course.completedLessons} / {course.totalLessons}</dd></div>
                  <div><dt>In progress</dt><dd>{course.inProgressLessons}</dd></div>
                  <div><dt>MCQ accuracy</dt><dd>{course.mcqAnswered ? `${courseAccuracy}% of ${course.mcqAnswered}` : '—'}</dd></div>
                  <div><dt>Assignments</dt><dd>{course.assignmentsSolved} solved</dd></div>
                </dl>
                {course.lastActivityAt && (
                  <span className="profile-course-activity">Last activity {timeAgo(course.lastActivityAt)}</span>
                )}
              </Link>
            );
          })}
        </div>
      ) : (
        <p className="profile-empty">Open a chapter to start building your learning record.</p>
      )}
    </section>
  );
}

function WeakestTopics({ topics }) {
  const answered = topics.filter((topic) => topic.answeredCount > 0).slice(0, 5);

  return (
    <section className="profile-learning-section profile-learning-section--half" aria-labelledby="profile-weakest-heading">
      <SectionHeading id="profile-weakest-heading" icon={Target} kicker="Revise next" title="Weakest topics" />
      {answered.length > 0 ? (
        <ol className="profile-list">
          {answered.map((topic) => (
            <li key={topic.lessonId} className="profile-list-item">
              <Link to={`/chapter/${topic.fullSlug}`} className="profile-list-link">{topic.lessonTitle}</Link>
              <span className="profile-list-meta">
                {topic.accuracyPercentage}% · {topic.correctCount}/{topic.answeredCount} correct
                {topic.questionCount > topic.answeredCount && ` · ${topic.questionCount - topic.answeredCount} unanswered`}
              </span>
            </li>
          ))}
        </ol>
      ) : (
        <p className="profile-empty">Answer a few chapter MCQs and your weakest topics will show up here.</p>
      )}
    </section>
  );
}

function RecentActivity({ events }) {
  const recent = events.slice(0, 15);

  return (
    <section className="profile-learning-section profile-learning-section--half" aria-labelledby="profile-activity-heading">
      <SectionHeading id="profile-activity-heading" icon={Activity} kicker="History" title="Recent activity" />
      {recent.length > 0 ? (
        <ul className="profile-list">
          {recent.map((event) => (
            <li key={event.id} className="profile-list-item">
              <span className="profile-list-text">
                {ACTIVITY_LABELS[event.eventType] || event.eventType}{' '}
                <strong>{event.lessonTitle || 'a chapter'}</strong>
              </span>
              <span className="profile-list-meta">{timeAgo(event.occurredAt)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="profile-empty">No activity yet.</p>
      )}
    </section>
  );
}

function ActiveSessions({ sessions, onRevoke, onSignOutAll, busyId, busyAll }) {
  return (
    <section className="profile-learning-section" aria-labelledby="profile-sessions-heading">
      <SectionHeading id="profile-sessions-heading" icon={Laptop} kicker="Security" title="Active sessions">
        <button type="button" className="learning-button" onClick={onSignOutAll} disabled={busyAll}>
          <LogOut size={13} /> {busyAll ? 'Signing out...' : 'Sign out of all devices'}
        </button>
      </SectionHeading>
      {sessions.length > 0 ? (
        <ul className="profile-list profile-session-list">
          {sessions.map((session) => (
            <li key={session.id} className="profile-list-item profile-session-item">
              <div className="profile-session-copy">
                <span className="profile-list-text">
                  <strong>{describeUserAgent(session.userAgent)}</strong>
                  {session.isCurrent && <span className="profile-badge">This device</span>}
                  {session.rememberMe && <span className="profile-badge profile-badge--quiet">Kept signed in</span>}
                </span>
                <span className="profile-list-meta">
                  Last active {timeAgo(session.lastSeenAt) || 'unknown'}
                  {session.ipAddress && ` · ${session.ipAddress}`}
                  {session.createdAt && ` · signed in ${timeAgo(session.createdAt)}`}
                </span>
              </div>
              <button
                type="button"
                className="learning-button"
                onClick={() => onRevoke(session)}
                disabled={busyId === session.id}
              >
                {session.isCurrent ? 'Sign out' : 'Revoke'}
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="profile-empty">No other sessions.</p>
      )}
    </section>
  );
}

/**
 * The signed-in learner's dashboard on /profile: progress summary, weakest topics,
 * recent activity and session management. Signed-out visitors get a sign-in prompt.
 */
export default function ProfileLearning() {
  const { isAuthenticated, loading: authLoading, user, logout, logoutAll, listSessions, revokeSession } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [data, setData] = useState({ summary: null, topics: [], events: [], sessions: [] });
  const [loadError, setLoadError] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [busyAll, setBusyAll] = useState(false);

  const load = useCallback(async () => {
    setLoadError(null);
    const [summary, topics, events, sessions] = await Promise.allSettled([
      api.me.summary(),
      api.me.mcqPerformance(),
      api.me.activity(15),
      listSessions()
    ]);
    const valueOf = (result, fallback) => (result.status === 'fulfilled' && result.value ? result.value : fallback);
    setData({
      summary: valueOf(summary, null),
      topics: valueOf(topics, []),
      events: valueOf(events, []),
      sessions: valueOf(sessions, [])
    });
    if ([summary, topics, events, sessions].some((result) => result.status === 'rejected')) {
      setLoadError('Some of your learning data could not be loaded.');
    }
  }, [listSessions]);

  useEffect(() => {
    if (isAuthenticated) load();
  }, [isAuthenticated, load]);

  if (authLoading) return null;

  if (!isAuthenticated) {
    return (
      <section className="profile-learning-signin">
        <span className="profile-kicker"><BarChart3 size={13} aria-hidden="true" /> Your learning</span>
        <p>Sign in to see your progress, weakest topics, recent activity and active sessions.</p>
        <Link to="/login" state={{ from: location }} className="learning-button learning-button--run">Sign in</Link>
      </section>
    );
  }

  const handleRevoke = async (session) => {
    if (session.isCurrent) {
      await logout();
      navigate('/login', { replace: true });
      return;
    }
    setBusyId(session.id);
    try {
      await revokeSession(session.id);
      setData((current) => ({ ...current, sessions: current.sessions.filter((item) => item.id !== session.id) }));
    } catch {
      setLoadError('That session could not be revoked. Please try again.');
    } finally {
      setBusyId(null);
    }
  };

  const handleSignOutAll = async () => {
    setBusyAll(true);
    try {
      await logoutAll();
    } catch {
      // Cookies are cleared server-side; local state is cleared regardless.
    } finally {
      setBusyAll(false);
      navigate('/login', { replace: true });
    }
  };

  return (
    <div className="profile-learning">
      <header className="profile-learning-header">
        <span className="profile-kicker">Signed in as {user?.displayName || user?.email}</span>
        <h1 className="profile-learning-title">Your learning record</h1>
      </header>

      {loadError && <p className="profile-error" role="alert">{loadError}</p>}

      {data.summary && <LearningSummary summary={data.summary} />}

      <div className="profile-learning-columns">
        <WeakestTopics topics={data.topics} />
        <RecentActivity events={data.events} />
      </div>

      <ActiveSessions
        sessions={data.sessions}
        onRevoke={handleRevoke}
        onSignOutAll={handleSignOutAll}
        busyId={busyId}
        busyAll={busyAll}
      />
    </div>
  );
}
