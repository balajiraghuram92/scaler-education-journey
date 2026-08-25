/**
 * Neuralascent Unified API Client
 * Enforces strict error propagation (no silent fake demo data in production),
 * RFC 7807 problem details parsing, API authentication, and request correlation IDs.
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

export async function apiClient(endpoint, options = {}) {
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

  const apiKey = import.meta.env.VITE_API_KEY;
  if (apiKey) {
    requestHeaders['x-api-key'] = apiKey;
  }

  if (body && typeof body === 'object' && !(body instanceof FormData)) {
    requestHeaders['Content-Type'] = 'application/json';
  }

  const config = {
    method,
    headers: requestHeaders,
    body: body && typeof body === 'object' && !(body instanceof FormData) ? JSON.stringify(body) : body,
    signal,
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
    run: (exerciseId, files, options = {}) => executeExercise('run', exerciseId, files, options),
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
  },

  // Legacy Endpoints
  legacy: {
    getVerticals: () => apiClient('/api/verticals'),
    getVerticalById: (id) => apiClient(`/api/verticals/${id}`),
    toggleTask: (id) => apiClient(`/api/tasks/${id}/toggle`, { method: 'PUT' }),
    getCourses: () => apiClient('/api/courses'),
    getChapterBySlug: (slug) => apiClient(`/api/chapters/${slug}`),
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
