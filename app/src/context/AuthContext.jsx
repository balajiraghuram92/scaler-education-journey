import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api, ApiError } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await api.auth.me();
      setUser(currentUser);
      return currentUser;
    } catch (err) {
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (email, password) => {
    return await api.auth.login(email, password);
  };

  const totpEnrollStart = async (challengeId) => {
    return await api.auth.totpEnrollStart(challengeId);
  };

  const totpEnrollConfirm = async (challengeId, code) => {
    const loggedInUser = await api.auth.totpEnrollConfirm(challengeId, code);
    setUser(loggedInUser);
    return loggedInUser;
  };

  const totpVerify = async (challengeId, code) => {
    const loggedInUser = await api.auth.totpVerify(challengeId, code);
    setUser(loggedInUser);
    return loggedInUser;
  };

  const signup = async (email, password, displayName) => {
    return await api.auth.signup(email, password, displayName);
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    isAuthenticated: Boolean(user),
    isAdmin: user?.role === 'Admin',
    loading,
    login,
    totpEnrollStart,
    totpEnrollConfirm,
    totpVerify,
    signup,
    logout,
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
