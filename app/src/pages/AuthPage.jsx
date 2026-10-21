import { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api, ApiError } from '../api/client';
import { LoadingState } from '../components/common/StateViews';
import QRCode from 'qrcode';
import {
  ShieldCheck,
  Mail,
  Lock,
  User,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  KeyRound,
  Copy,
  Check,
  Smartphone,
  ArrowLeft,
  QrCode
} from 'lucide-react';
import './AuthPage.css';

function locationToPath(from) {
  if (!from) return null;
  if (typeof from === 'string') return from;
  if (typeof from === 'object' && from.pathname) {
    return `${from.pathname}${from.search || ''}${from.hash || ''}`;
  }
  return null;
}

async function resolvePostLoginTarget(from) {
  const explicit = locationToPath(from);
  if (explicit && explicit !== '/login') return explicit;

  try {
    const resume = await api.me.resume();
    if (resume?.lastLesson?.fullSlug) return `/chapter/${resume.lastLesson.fullSlug}`;
  } catch {
    // No resume point yet; fall through to the library.
  }
  return '/chapters';
}

function RememberMeCheckbox({ checked, onChange }) {
  return (
    <label className="auth-remember-row" htmlFor="auth-remember-me">
      <input
        id="auth-remember-me"
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span>
        <strong>Keep me signed in on this device</strong>
        <span>Stay signed in for 30 days. Leave unchecked on a shared computer.</span>
      </span>
    </label>
  );
}

export default function AuthPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');

  // 2FA state machine: 'credentials' | 'totp-enroll' | 'totp-verify'
  const [step, setStep] = useState('credentials');
  const [challengeId, setChallengeId] = useState(null);
  const [enrollData, setEnrollData] = useState(null); // { otpAuthUri, manualEntryCode }
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [copiedKey, setCopiedKey] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isRedirecting, setIsRedirecting] = useState(false);

  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [signupSuccessMessage, setSignupSuccessMessage] = useState(null);

  const { login, signup, totpEnrollStart, totpEnrollConfirm, totpVerify, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from;

  useEffect(() => {
    if (enrollData?.otpAuthUri) {
      QRCode.toDataURL(enrollData.otpAuthUri, {
        width: 200,
        margin: 2,
        color: {
          dark: '#1B1B18',
          light: '#FFFFFF',
        }
      })
        .then((url) => setQrCodeDataUrl(url))
        .catch((err) => {
          console.error('Failed to generate TOTP QR code offline:', err);
          setQrCodeDataUrl('');
        });
    } else {
      setQrCodeDataUrl('');
    }
  }, [enrollData]);

  const resetToCredentials = () => {
    setStep('credentials');
    setChallengeId(null);
    setEnrollData(null);
    setQrCodeDataUrl('');
    setTotpCode('');
    setError(null);
    setCopiedKey(false);
  };

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (isSignUp) {
        const response = await signup(email, password, displayName);
        setSignupSuccessMessage(
          response.message || 'Your account registration has been submitted and is pending administrator approval.'
        );
        setEmail('');
        setPassword('');
        setDisplayName('');
      } else {
        const res = await login(email, password);
        setChallengeId(res.challengeId);

        if (res.requiresEnrollment) {
          const enroll = await totpEnrollStart(res.challengeId);
          setEnrollData(enroll);
          setStep('totp-enroll');
        } else {
          setStep('totp-verify');
        }
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTotpSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const cleanCode = totpCode.trim().replace(/\s+/g, '');
      setIsRedirecting(true);
      if (step === 'totp-enroll') {
        await totpEnrollConfirm(challengeId, cleanCode, rememberMe);
      } else {
        await totpVerify(challengeId, cleanCode, rememberMe);
      }
      const target = await resolvePostLoginTarget(from);
      navigate(target, { replace: true });
    } catch (err) {
      setIsRedirecting(false);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Verification failed. Please check the code and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(true);
      setTimeout(() => setCopiedKey(false), 2500);
    } catch {
      // Fallback if clipboard API not available
    }
  };

  if (user && isRedirecting) {
    return <LoadingState message="Opening where you left off..." />;
  }

  if (user) {
    return (
      <div className="auth-page-container">
        <div className="auth-card">
          <div className="auth-header">
            <span className="auth-kicker">Session Active</span>
            <h1 className="auth-title">Signed In as {user.displayName || user.email}</h1>
            <p className="auth-subtitle">
              Role: <span className="auth-role-badge">{user.role}</span> &bull; Status: <span className="auth-status-badge">{user.status}</span>
            </p>
          </div>

          <div className="auth-actions-group">
            <Link to="/chapters" className="auth-btn-primary">
              Continue to Chapters <ArrowRight size={16} />
            </Link>
            {user.role === 'Admin' && (
              <Link to="/admin/users" className="auth-btn-secondary">
                Go to Admin Dashboard
              </Link>
            )}
            <button
              type="button"
              onClick={async () => {
                await logout();
              }}
              className="auth-btn-tertiary"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page-container">
      <div className="auth-card">
        {step === 'credentials' && (
          <>
            {/* Editorial Kicker & Header */}
            <div className="auth-header">
              <span className="auth-kicker">Neuralascent Identity</span>
              <h1 className="auth-title">
                {isSignUp ? 'Request Access' : 'Sign In to Neuralascent'}
              </h1>
              <p className="auth-subtitle">
                {isSignUp
                  ? 'New learner registrations are reviewed by an administrator prior to access activation.'
                  : 'Sign in to access your reading rooms, interactive labs, and learning pathways.'}
              </p>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="auth-tab-bar" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={!isSignUp}
                className={`auth-tab ${!isSignUp ? 'active' : ''}`}
                onClick={() => {
                  setIsSignUp(false);
                  setError(null);
                  setSignupSuccessMessage(null);
                }}
              >
                Sign In
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={isSignUp}
                className={`auth-tab ${isSignUp ? 'active' : ''}`}
                onClick={() => {
                  setIsSignUp(true);
                  setError(null);
                  setSignupSuccessMessage(null);
                }}
              >
                Request Access
              </button>
            </div>

            {/* Feedback Notices */}
            {signupSuccessMessage && (
              <div className="auth-notice success">
                <CheckCircle2 size={18} className="notice-icon" />
                <div className="notice-content">
                  <strong>Registration Submitted</strong>
                  <p>{signupSuccessMessage}</p>
                  <button
                    type="button"
                    className="auth-link-btn"
                    onClick={() => {
                      setIsSignUp(false);
                      setSignupSuccessMessage(null);
                    }}
                  >
                    Switch to Sign In
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div className="auth-notice error">
                <AlertCircle size={18} className="notice-icon" />
                <div className="notice-content">
                  <strong>Authentication Notice</strong>
                  <p>{error}</p>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleCredentialsSubmit} className="auth-form">
              {isSignUp && (
                <div className="form-group">
                  <label htmlFor="auth-display-name">Full Name or Alias</label>
                  <div className="input-wrapper">
                    <User size={16} className="input-icon" />
                    <input
                      id="auth-display-name"
                      type="text"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="e.g. Alex Mercer"
                      maxLength={120}
                    />
                  </div>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="auth-email">Email Address</label>
                <div className="input-wrapper">
                  <Mail size={16} className="input-icon" />
                  <input
                    id="auth-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    maxLength={320}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="auth-password">Password</label>
                <div className="input-wrapper">
                  <Lock size={16} className="input-icon" />
                  <input
                    id="auth-password"
                    type="password"
                    required
                    minLength={10}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Minimum 10 characters"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="auth-btn-submit"
              >
                {isSubmitting
                  ? (isSignUp ? 'Submitting Request...' : 'Signing In...')
                  : (isSignUp ? 'Submit Registration Request' : 'Sign In')}
              </button>
            </form>
          </>
        )}

        {step === 'totp-enroll' && (
          <>
            <div className="auth-header">
              <span className="auth-kicker">Security Setup</span>
              <h1 className="auth-title">Setup Two-Factor Auth</h1>
              <p className="auth-subtitle">
                Two-factor authentication is required. Scan the QR code or add the secret key to your authenticator app (Google Authenticator, Authy, 1Password).
              </p>
            </div>

            {error && (
              <div className="auth-notice error">
                <AlertCircle size={18} className="notice-icon" />
                <div className="notice-content">
                  <strong>Verification Notice</strong>
                  <p>{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleTotpSubmit} className="auth-form">
              <div className="totp-setup-card">
                <div className="totp-setup-instruction">
                  <span className="totp-step-num">1</span>
                  <span>Scan QR Code or enter setup key in your authenticator app:</span>
                </div>

                {qrCodeDataUrl ? (
                  <div className="totp-qr-container" style={{ textAlign: 'center', margin: '14px 0 10px 0' }}>
                    <img
                      src={qrCodeDataUrl}
                      alt="Authenticator Setup QR Code"
                      style={{
                        width: '180px',
                        height: '180px',
                        display: 'inline-block',
                        background: '#FFFFFF',
                        padding: '8px',
                        borderRadius: '8px',
                        border: '1px solid var(--border-subtle, #E4E0D7)',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
                      }}
                    />
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted, #726E65)', marginTop: '6px' }}>
                      <QrCode size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
                      Rendered securely and offline on your device
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '16px', color: 'var(--text-muted)' }}>
                    Generating QR code...
                  </div>
                )}

                {enrollData?.manualEntryCode && (
                  <div className="totp-secret-box">
                    <div className="totp-secret-key" title="Manual Entry Key">
                      {enrollData.manualEntryCode}
                    </div>
                    <button
                      type="button"
                      className="totp-copy-btn"
                      onClick={() => copyToClipboard(enrollData.manualEntryCode)}
                      title="Copy secret key"
                    >
                      {copiedKey ? <Check size={16} /> : <Copy size={16} />}
                      <span>{copiedKey ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                )}

                {enrollData?.otpAuthUri && (
                  <a
                    href={enrollData.otpAuthUri}
                    className="totp-app-link"
                    title="Direct link for mobile authenticators"
                  >
                    <Smartphone size={14} /> Open in Authenticator App
                  </a>
                )}

                <div className="totp-setup-instruction" style={{ marginTop: 'var(--space-md)' }}>
                  <span className="totp-step-num">2</span>
                  <span>Enter the 6-digit code shown in your app:</span>
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <div className="input-wrapper">
                    <KeyRound size={16} className="input-icon" />
                    <input
                      id="auth-totp-enroll-code"
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]*"
                      maxLength={6}
                      autoFocus
                      required
                      value={totpCode}
                      onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="000000"
                      className="totp-code-input"
                    />
                  </div>
                </div>
              </div>

              <RememberMeCheckbox checked={rememberMe} onChange={setRememberMe} />

              <button
                type="submit"
                disabled={isSubmitting || totpCode.trim().length !== 6}
                className="auth-btn-submit"
              >
                {isSubmitting ? 'Confirming Enrollment...' : 'Confirm & Complete Sign In'}
              </button>

              <button
                type="button"
                onClick={resetToCredentials}
                className="auth-btn-back"
              >
                <ArrowLeft size={14} /> Back to Sign In
              </button>
            </form>
          </>
        )}

        {step === 'totp-verify' && (
          <>
            <div className="auth-header">
              <span className="auth-kicker">Second Factor</span>
              <h1 className="auth-title">Security Code</h1>
              <p className="auth-subtitle">
                Enter the 6-digit code generated by your authenticator app for <strong>{email}</strong>.
              </p>
            </div>

            {error && (
              <div className="auth-notice error">
                <AlertCircle size={18} className="notice-icon" />
                <div className="notice-content">
                  <strong>Verification Notice</strong>
                  <p>{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleTotpSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="auth-totp-verify-code">6-Digit Security Code</label>
                <div className="input-wrapper">
                  <KeyRound size={16} className="input-icon" />
                  <input
                    id="auth-totp-verify-code"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    autoFocus
                    required
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="000000"
                    className="totp-code-input"
                  />
                </div>
              </div>

              <RememberMeCheckbox checked={rememberMe} onChange={setRememberMe} />

              <button
                type="submit"
                disabled={isSubmitting || totpCode.trim().length !== 6}
                className="auth-btn-submit"
              >
                {isSubmitting ? 'Verifying Code...' : 'Verify & Sign In'}
              </button>

              <button
                type="button"
                onClick={resetToCredentials}
                className="auth-btn-back"
              >
                <ArrowLeft size={14} /> Back to Sign In
              </button>
            </form>
          </>
        )}

        <div className="auth-footer-note">
          <ShieldCheck size={14} />
          <span>Protected via RFC 6238 TOTP 2FA and AES-GCM encrypted credentials.</span>
        </div>
      </div>
    </div>
  );
}
