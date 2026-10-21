import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { api, ApiError, SESSION_ENDED_EVENT } from '../api/client';

const AuthContext = createContext(null);

// The access cookie lives ~30 minutes. Rotating every ~20 minutes while the tab is
// visible keeps it fresh for every consumer of that cookie, including the Python
// ai-agent service, which validates the same short-lived token but cannot refresh it.
export const PROACTIVE_REFRESH_INTERVAL_MS = 20 * 60 * 1000;

function isUnauthorized(err) {
  return err instanceof ApiError && err.status === 401;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionNotice, setSessionNotice] = useState(null);
  const userRef = useRef(null);
  const lastRefreshAtRef = useRef(Date.now());

  useEffect(() => {
    userRef.current = user;
  }, [user]);

  const applySignedInUser = useCallback((nextUser) => {
    lastRefreshAtRef.current = Date.now();
    setSessionNotice(null);
    setUser(nextUser);
    return nextUser;
  }, []);

  const endSession = useCallback((showNotice) => {
    if (showNotice && userRef.current) {
      setSessionNotice({
        title: 'Your session ended',
        message: 'Sign in again to keep saving your reading progress and answers.'
      });
    }
    userRef.current = null;
    setUser(null);
  }, []);

  // Initial probe: /me first; if the access cookie has expired, try the refresh cookie
  // before concluding the visitor is signed out. No "session ended" notice here.
  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await api.auth.me({ skipAuthRefresh: true });
      applySignedInUser(currentUser);
      // The existing access cookie's age is unknown, so rotate on the first check.
      lastRefreshAtRef.current = 0;
      return currentUser;
    } catch (err) {
      if (isUnauthorized(err)) {
        try {
          const refreshedUser = await api.auth.refresh();
          return applySignedInUser(refreshedUser);
        } catch {
          // Refresh cookie missing or expired: signed out.
        }
      }
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, [applySignedInUser]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // The API client emits this when a 401 could not be recovered by a refresh.
  useEffect(() => {
    const handleSessionEnded = () => endSession(true);
    window.addEventListener(SESSION_ENDED_EVENT, handleSessionEnded);
    return () => window.removeEventListener(SESSION_ENDED_EVENT, handleSessionEnded);
  }, [endSession]);

  // Proactive refresh while signed in and the tab is visible.
  useEffect(() => {
    if (!user) return undefined;

    const refreshIfDue = async () => {
      if (document.visibilityState !== 'visible') return;
      if (Date.now() - lastRefreshAtRef.current < PROACTIVE_REFRESH_INTERVAL_MS) return;
      lastRefreshAtRef.current = Date.now();
      try {
        const refreshedUser = await api.auth.refresh();
        if (refreshedUser && typeof refreshedUser === 'object') setUser(refreshedUser);
      } catch (err) {
        if (isUnauthorized(err)) endSession(true);
      }
    };

    const intervalId = window.setInterval(refreshIfDue, 60 * 1000);
    document.addEventListener('visibilitychange', refreshIfDue);
    return () => {
      window.clearInterval(intervalId);
      document.removeEventListener('visibilitychange', refreshIfDue);
    };
  }, [user, endSession]);

  const login = async (email, password) => {
    return await api.auth.login(email, password);
  };

  const totpEnrollStart = async (challengeId) => {
    return await api.auth.totpEnrollStart(challengeId);
  };

  const totpEnrollConfirm = async (challengeId, code, rememberMe = false) => {
    const loggedInUser = await api.auth.totpEnrollConfirm(challengeId, code, rememberMe);
    return applySignedInUser(loggedInUser);
  };

  const totpVerify = async (challengeId, code, rememberMe = false) => {
    const loggedInUser = await api.auth.totpVerify(challengeId, code, rememberMe);
    return applySignedInUser(loggedInUser);
  };

  const signup = async (email, password, displayName) => {
    return await api.auth.signup(email, password, displayName);
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch {
      // The session may already be gone; sign out locally either way.
    } finally {
      endSession(false);
    }
  };

  const logoutAll = async () => {
    try {
      return await api.auth.logoutAll();
    } finally {
      endSession(false);
    }
  };

  const listSessions = useCallback(() => api.auth.sessions(), []);

  const revokeSession = useCallback((sessionId) => api.auth.revokeSession(sessionId), []);

  const dismissSessionNotice = useCallback(() => setSessionNotice(null), []);

  const value = {
    user,
    isAuthenticated: Boolean(user),
    isAdmin: user?.role === 'Admin',
    loading,
    sessionNotice,
    dismissSessionNotice,
    login,
    totpEnrollStart,
    totpEnrollConfirm,
    totpVerify,
    signup,
    logout,
    logoutAll,
    listSessions,
    revokeSession,
    refreshUser
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// For components that work signed in or out (and in isolated tests without a provider).
const SIGNED_OUT = Object.freeze({ user: null, isAuthenticated: false, isAdmin: false, loading: false });

export function useOptionalAuth() {
  return useContext(AuthContext) || SIGNED_OUT;
}
