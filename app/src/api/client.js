/**
 * Neuralascent Unified API Client
 * Enforces strict error propagation (no silent fake demo data in production),
 * RFC 7807 problem details parsing and request correlation IDs.
 */

const API_BASE_URL = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, status, problemDetails = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.problemDetails = problemDetails;
  }
}

export const SESSION_ENDED_EVENT = 'na:session-ended';

// Auth endpoints that must never trigger a transparent refresh: the refresh call itself,
// the credential steps (a 401 there is a real "wrong password / code" answer) and logout.
const NO_REFRESH_PATHS = [/^\/api\/auth\/refresh$/, /^\/api\/auth\/login$/, /^\/api\/auth\/totp\//, /^\/api\/auth\/logout$/];

let refreshInFlight = null;

function endpointPath(endpoint) {
  let path = endpoint;
  if (path.startsWith('http')) {
    try {
      path = new URL(path).pathname;
    } catch {
      return path;
    }
  }
  if (!path.startsWith('/')) path = `/${path}`;
  return path.split(/[?#]/)[0];
}

function canRefreshFor(endpoint) {
  const path = endpointPath(endpoint);
  return !NO_REFRESH_PATHS.some((pattern) => pattern.test(path));
}

function emitSessionEnded(endpoint) {
  if (typeof window === 'undefined' || typeof window.dispatchEvent !== 'function') return;
  window.dispatchEvent(new CustomEvent(SESSION_ENDED_EVENT, { detail: { endpoint } }));
}

/**
 * Rotates the session via the refresh cookie. Concurrent callers share one in-flight
 * request, so a burst of 401s produces a single POST /api/auth/refresh.
 */
export function refreshSession() {
  if (!refreshInFlight) {
    refreshInFlight = performRequest('/api/auth/refresh', { method: 'POST' })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

/**
 * Sends a request. On a 401 it refreshes the session once and retries the original
 * request once; if the refresh fails it emits `na:session-ended` and rethrows the 401.
 * Pass `skipAuthRefresh: true` to opt out (used for the initial session probe).
 */
export async function apiClient(endpoint, options = {}) {
  const { skipAuthRefresh = false, ...requestOptions } = options;

  try {
    return await performRequest(endpoint, requestOptions);
  } catch (err) {
    const shouldRefresh = !skipAuthRefresh
      && err instanceof ApiError
      && err.status === 401
      && canRefreshFor(endpoint);

    if (!shouldRefresh) throw err;

    try {
      await refreshSession();
    } catch {
      emitSessionEnded(endpoint);
      throw err;
    }

    return performRequest(endpoint, requestOptions);
  }
}

async function performRequest(endpoint, options = {}) {
  const {
    method = 'GET',
    headers = {},
    body = null,
    timeoutMs = 15000,
    signal: customSignal,
    ...rest
  } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  const abortFromCaller = () => controller.abort(customSignal.reason);

  if (customSignal) {
    if (customSignal.aborted) {
      controller.abort(customSignal.reason);
    } else {
      customSignal.addEventListener('abort', abortFromCaller, { once: true });
    }
  }

  const signal = controller.signal;

  const correlationId = crypto.randomUUID ? crypto.randomUUID() : `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

  const requestHeaders = {
    'Accept': 'application/json',
    'x-correlation-id': correlationId,
    ...headers,
  };

  if (body && typeof body === 'object' && !(body instanceof FormData)) {
    requestHeaders['Content-Type'] = 'application/json';
  }

  const config = {
    method,
    headers: requestHeaders,
    body: body && typeof body === 'object' && !(body instanceof FormData) ? JSON.stringify(body) : body,
    signal,
    credentials: rest.credentials || 'include',
    ...rest,
  };

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${cleanEndpoint}`;

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);
    customSignal?.removeEventListener('abort', abortFromCaller);

    if (!response.ok) {
      let problemDetails = null;
      let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;

      try {
        const contentType = response.headers.get('content-type');
        if (contentType && (contentType.includes('application/json') || contentType.includes('application/problem+json'))) {
          problemDetails = await response.json();
          errorMsg = problemDetails.detail || problemDetails.title || problemDetails.message || errorMsg;
        } else {
          const text = await response.text();
          if (text) errorMsg = text;
        }
      } catch {
        // Failed to parse error body
      }

      throw new ApiError(errorMsg, response.status, problemDetails);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text();
  } catch (err) {
    clearTimeout(timeoutId);
    customSignal?.removeEventListener('abort', abortFromCaller);

    if (err.name === 'AbortError') {
      throw new ApiError(`Request timeout after ${timeoutMs}ms`, 408);
    }

    if (err instanceof ApiError) {
      throw err;
    }

    throw new ApiError(err.message || 'Network connection failed.', 0);
  }
}

// Convenience methods
export const api = {
  get: (endpoint, options) => apiClient(endpoint, { ...options, method: 'GET' }),
  post: (endpoint, body, options) => apiClient(endpoint, { ...options, method: 'POST', body }),
  put: (endpoint, body, options) => apiClient(endpoint, { ...options, method: 'PUT', body }),
  delete: (endpoint, options) => apiClient(endpoint, { ...options, method: 'DELETE' }),

  exercises: {
    getMetadata: (exerciseId, options = {}) =>
      apiClient(`/api/exercises/${encodeURIComponent(exerciseId)}`, {
        ...options,
        method: 'GET'
      }),
    getSolution: (exerciseId, options = {}) =>
      apiClient(`/api/exercises/${encodeURIComponent(exerciseId)}/solution`, {
        ...options,
        method: 'GET'
      }),
    run: (exerciseId, files, options = {}) => executeExercise('run', exerciseId, files, options),
    // Kept for older API consumers. The learner UI uses getSolution instead.
    check: (exerciseId, files, options = {}) => executeExercise('check', exerciseId, files, options)
  },

  // V2 Specialized API Endpoints
  v2: {
    getLearningPaths: () => apiClient('/api/v2/learning-paths'),
    getLearningPath: (slug) => apiClient(`/api/v2/learning-paths/${slug}`),
    getKnowledgeAtlas: () => apiClient('/api/v2/knowledge-atlas'),
    getReadingMap: () => apiClient('/api/v2/reading-map'),
    getChapter: (courseSlug, moduleSlug, lessonSlug) =>
      apiClient(`/api/v2/chapters/${courseSlug}/${moduleSlug}/${lessonSlug}`),
    setLessonProgress: (lessonId, isCompleted, correlationId) =>
      apiClient('/api/v2/progress/lesson', { method: 'POST', body: { lessonId, isCompleted, correlationId } }),
    setProblemProgress: (problemId, isCompleted, correlationId) =>
      apiClient('/api/v2/progress/problem', { method: 'POST', body: { problemId, isCompleted, correlationId } }),
    setTaskProgress: (taskId, isCompleted, correlationId) =>
      apiClient('/api/v2/progress/task', { method: 'POST', body: { taskId, isCompleted, correlationId } }),
    importCurriculum: (payload) =>
      apiClient('/api/v2/curriculum/import', { method: 'POST', body: payload }),
    getPracticeQuestions: (courseSlug, moduleSlug, lessonSlug) =>
      apiClient(`/api/v2/practice-questions/${encodeURIComponent(courseSlug)}/${encodeURIComponent(moduleSlug)}/${encodeURIComponent(lessonSlug)}`),
    submitPracticeAttempt: (presentationId, selectedOptionKey) =>
      apiClient(`/api/v2/practice-questions/${encodeURIComponent(presentationId)}/attempts`, {
        method: 'POST',
        body: { selectedOptionKey }
      }),
    retryPracticeQuestion: (presentationId) =>
      apiClient(`/api/v2/practice-questions/${encodeURIComponent(presentationId)}/retry`, { method: 'POST' }),
  },

  // Signed-in learner state (all routes return 401 when signed out)
  me: {
    summary: () => apiClient('/api/me/summary'),
    resume: () => apiClient('/api/me/resume'),
    recordVisit: (lessonId) =>
      apiClient(`/api/me/lessons/${encodeURIComponent(lessonId)}/visit`, { method: 'POST' }),
    updatePosition: (lessonId, { sectionId, scrollPercent, secondsDelta }, options = {}) =>
      apiClient(`/api/me/lessons/${encodeURIComponent(lessonId)}/position`, {
        ...options,
        method: 'PUT',
        body: { sectionId, scrollPercent, secondsDelta }
      }),
    // Last heartbeat when the tab is hidden or the reader unmounts: keepalive lets the
    // browser finish the request after the page goes away. Failures are ignored.
    sendPositionBeacon: (lessonId, position) =>
      api.me.updatePosition(lessonId, position, { keepalive: true, skipAuthRefresh: true }).catch(() => null),
    setLessonCompletion: (lessonId, isCompleted) =>
      apiClient(`/api/me/lessons/${encodeURIComponent(lessonId)}/completion`, {
        method: 'PUT',
        body: { isCompleted }
      }),
    setProblemStatus: (problemId, status, solutionRevealed) =>
      apiClient(`/api/me/problems/${encodeURIComponent(problemId)}/status`, {
        method: 'PUT',
        body: solutionRevealed === undefined ? { status } : { status, solutionRevealed }
      }),
    mcqPerformance: (courseSlug) =>
      apiClient(`/api/me/mcq-performance${courseSlug ? `?course=${encodeURIComponent(courseSlug)}` : ''}`),
    activity: (limit = 50) =>
      apiClient(`/api/me/activity?limit=${encodeURIComponent(limit)}`),
  },

  // Chapter notes (personal notes require sign-in)
  notes: {
    create: (lessonId, { title, contentBody, anchorSection = null, noteType = 'PersonalNote' }) =>
      apiClient(`/api/chapters/${encodeURIComponent(lessonId)}/notes`, {
        method: 'POST',
        body: { noteType, title, contentBody, anchorSection, orderIndex: null }
      }),
  },

  // Legacy Endpoints
  legacy: {
    getVerticals: () => apiClient('/api/verticals'),
    getVerticalById: (id) => apiClient(`/api/verticals/${id}`),
    toggleTask: (id) => apiClient(`/api/tasks/${id}/toggle`, { method: 'PUT' }),
    getCourses: () => apiClient('/api/courses'),
    getChapterBySlug: (slug) => apiClient(`/api/chapters/${slug}`),
  },

  // Authentication & Session Endpoints
  auth: {
    signup: (email, password, displayName) =>
      apiClient('/api/auth/signup', { method: 'POST', body: { email, password, displayName } }),
    login: (email, password) =>
      apiClient('/api/auth/login', { method: 'POST', body: { email, password } }),
    totpEnrollStart: (challengeId) =>
      apiClient('/api/auth/totp/enroll/start', { method: 'POST', body: { challengeId } }),
    totpEnrollConfirm: (challengeId, code, rememberMe = false) =>
      apiClient('/api/auth/totp/enroll/confirm', { method: 'POST', body: { challengeId, code, rememberMe: Boolean(rememberMe) } }),
    totpVerify: (challengeId, code, rememberMe = false) =>
      apiClient('/api/auth/totp/verify', { method: 'POST', body: { challengeId, code, rememberMe: Boolean(rememberMe) } }),
    logout: () =>
      apiClient('/api/auth/logout', { method: 'POST' }),
    me: (options = {}) =>
      apiClient('/api/auth/me', { ...options, method: 'GET' }),
    refresh: () => refreshSession(),
    sessions: () =>
      apiClient('/api/auth/sessions', { method: 'GET' }),
    revokeSession: (sessionId) =>
      apiClient(`/api/auth/sessions/${encodeURIComponent(sessionId)}`, { method: 'DELETE' }),
    logoutAll: () =>
      apiClient('/api/auth/logout-all', { method: 'POST' }),
  },

  // Admin User Management Endpoints
  admin: {
    getUsers: (status) =>
      apiClient(`/api/admin/users${status ? `?status=${encodeURIComponent(status)}` : ''}`, { method: 'GET' }),
    approveUser: (id) =>
      apiClient(`/api/admin/users/${id}/approve`, { method: 'POST' }),
    rejectUser: (id, reason) =>
      apiClient(`/api/admin/users/${id}/reject`, { method: 'POST', body: { reason } }),
    resetTotp: (id) =>
      apiClient(`/api/admin/users/${id}/reset-totp`, { method: 'POST' }),
    getUsageToday: () =>
      apiClient('/api/admin/usage/today', { method: 'GET' }),
    getUsageByUser: () =>
      apiClient('/api/admin/usage/by-user', { method: 'GET' }),
  },

  // Lesson-Scoped AI Chat Endpoints
  chat: {
    createConversation: (lessonId, title) =>
      apiClient('/api/chat/conversations', { method: 'POST', body: { lessonId, title } }),
    sendMessage: (conversationId, content, clientRequestId) =>
      apiClient(`/api/chat/conversations/${conversationId}/messages`, {
        method: 'POST',
        body: { content, clientRequestId }
      }),
    getMessages: (conversationId) =>
      apiClient(`/api/chat/conversations/${conversationId}/messages`, { method: 'GET' }),
  },

  // Localization Lab Endpoints (Owner Side)
  localization: {
    getProjects: () => apiClient('/api/localization/projects'),
    getProject: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}`),
    getStrings: (slug, locale) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/strings?locale=${encodeURIComponent(locale)}`),
    updateTranslation: (slug, stringId, locale, targetText) =>
      apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/strings/${stringId}/translations/${encodeURIComponent(locale)}`, { method: 'PUT', body: { targetText } }),
    getWorkflow: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow`),
    addWorkflowStep: (slug, body) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps`, { method: 'POST', body }),
    updateWorkflowStep: (slug, stepId, body) =>
      apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}`, { method: 'PUT', body }),
    reorderWorkflowStep: (slug, stepId, direction) =>
      apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}/reorder`, { method: 'POST', body: { direction } }),
    runWorkflowStep: (slug, stepId) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}/run`, { method: 'POST' }),
    deleteWorkflowStep: (slug, stepId) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}`, { method: 'DELETE' }),
    getSnapshots: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/snapshots`),
    cutSnapshot: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/snapshots`, { method: 'POST' }),
    getMarketplaceOverview: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/marketplace`),
    postToMarketplace: (slug, locale) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/marketplace/${encodeURIComponent(locale)}/post`, { method: 'POST' }),
    getBids: (jobId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/bids`),
    awardBid: (jobId, bidId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/bids/${bidId}/award`, { method: 'POST' }),
    approveSubmission: (jobId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/approve`, { method: 'POST' }),
    sendBackForRevision: (jobId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/send-back`, { method: 'POST' }),
    getProviderHealth: () => apiClient('/api/localization/provider-health'),
    simulateOutage: (provider) => apiClient(`/api/localization/provider-health/${provider}/simulate-outage`, { method: 'POST' }),
    resolveOutage: (provider) => apiClient(`/api/localization/provider-health/${provider}/resolve`, { method: 'POST' }),
  },

  // Vendor Portal Endpoints (Vendor Side)
  vendorPortal: {
    getRoster: () => apiClient('/api/localization/vendor/roster'),
    getOpenJobs: (vendorId) => apiClient(`/api/localization/vendor/${vendorId}/open-jobs`),
    submitBid: (vendorId, jobId, proposedPrice, note) =>
      apiClient(`/api/localization/vendor/${vendorId}/jobs/${jobId}/bids`, { method: 'POST', body: { proposedPrice, note } }),
    getAwardedJobs: (vendorId) => apiClient(`/api/localization/vendor/${vendorId}/awarded-jobs`),
    getJobStrings: (jobId) => apiClient(`/api/localization/vendor/jobs/${jobId}/strings`),
    updateJobString: (jobId, stringId, targetText) =>
      apiClient(`/api/localization/vendor/jobs/${jobId}/strings/${stringId}`, { method: 'PUT', body: { targetText } }),
    submitJob: (jobId) => apiClient(`/api/localization/vendor/jobs/${jobId}/submit`, { method: 'POST' }),
  }
};

function executeExercise(operation, exerciseId, files, options = {}) {
  const { clientRequestId = null, ...requestOptions } = options;
  return apiClient(`/api/exercises/${encodeURIComponent(exerciseId)}/${operation}`, {
    ...requestOptions,
    method: 'POST',
    body: { files, clientRequestId }
  });
}
