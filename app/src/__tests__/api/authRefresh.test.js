import { afterEach, describe, expect, it, vi } from 'vitest';
import { api, ApiError, SESSION_ENDED_EVENT } from '../../api/client';

function jsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Unauthorized',
    headers: new Headers({ 'content-type': status === 401 ? 'application/problem+json' : 'application/json' }),
    json: vi.fn().mockResolvedValue(body),
    text: vi.fn().mockResolvedValue(JSON.stringify(body))
  };
}

const unauthorized = () => jsonResponse({ title: 'Unauthorized', detail: 'Access token expired.' }, 401);
const refreshFailed = () => jsonResponse({ title: 'Session ended', detail: 'Refresh token revoked.' }, 401);

/**
 * fetch mock where each URL has its own queue of responses (last one repeats).
 */
function routedFetch(routes) {
  const queues = Object.fromEntries(Object.entries(routes).map(([url, responses]) => [url, [...responses]]));
  return vi.fn(async (url) => {
    const queue = queues[url];
    if (!queue) throw new Error(`Unexpected fetch ${url}`);
    const next = queue.length > 1 ? queue.shift() : queue[0];
    return typeof next === 'function' ? next() : next;
  });
}

function callsTo(fetchMock, url) {
  return fetchMock.mock.calls.filter(([calledUrl]) => calledUrl === url).length;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('apiClient transparent session refresh', () => {
  it('refreshes once on a 401 and retries the original request', async () => {
    const fetchMock = routedFetch({
      '/api/me/summary': [unauthorized, () => jsonResponse({ totalLessonsCompleted: 4 })],
      '/api/auth/refresh': [() => jsonResponse({ id: 1, email: 'a@b.c' })]
    });
    vi.stubGlobal('fetch', fetchMock);

    const result = await api.me.summary();

    expect(result).toEqual({ totalLessonsCompleted: 4 });
    expect(callsTo(fetchMock, '/api/me/summary')).toBe(2);
    expect(callsTo(fetchMock, '/api/auth/refresh')).toBe(1);
    expect(fetchMock).toHaveBeenCalledWith('/api/auth/refresh', expect.objectContaining({ method: 'POST', credentials: 'include' }));
  });

  it('shares a single in-flight refresh across concurrent 401s', async () => {
    let releaseRefresh;
    const refreshGate = new Promise((resolve) => {
      releaseRefresh = resolve;
    });
    const fetchMock = routedFetch({
      '/api/me/summary': [unauthorized, () => jsonResponse({ ok: 'summary' })],
      '/api/me/resume': [unauthorized, () => jsonResponse({ ok: 'resume' })],
      '/api/me/activity?limit=50': [unauthorized, () => jsonResponse([])],
      '/api/auth/refresh': [async () => {
        await refreshGate;
        return jsonResponse({ id: 1 });
      }]
    });
    vi.stubGlobal('fetch', fetchMock);

    const pending = Promise.all([api.me.summary(), api.me.resume(), api.me.activity()]);
    await vi.waitFor(() => expect(callsTo(fetchMock, '/api/auth/refresh')).toBe(1));
    releaseRefresh();

    await expect(pending).resolves.toEqual([{ ok: 'summary' }, { ok: 'resume' }, []]);
    expect(callsTo(fetchMock, '/api/auth/refresh')).toBe(1);
  });

  it('emits na:session-ended and throws the original 401 when the refresh fails', async () => {
    const fetchMock = routedFetch({
      '/api/me/resume': [unauthorized],
      '/api/auth/refresh': [refreshFailed]
    });
    vi.stubGlobal('fetch', fetchMock);
    const listener = vi.fn();
    window.addEventListener(SESSION_ENDED_EVENT, listener);

    try {
      const error = await api.me.resume().catch((err) => err);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.status).toBe(401);
      expect(error.message).toBe('Access token expired.');
      expect(listener).toHaveBeenCalledTimes(1);
      expect(callsTo(fetchMock, '/api/me/resume')).toBe(1);
    } finally {
      window.removeEventListener(SESSION_ENDED_EVENT, listener);
    }
  });

  it('does not retry more than once when the retried request is still unauthorized', async () => {
    const fetchMock = routedFetch({
      '/api/me/summary': [unauthorized],
      '/api/auth/refresh': [() => jsonResponse({ id: 1 })]
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(api.me.summary()).rejects.toMatchObject({ status: 401 });
    expect(callsTo(fetchMock, '/api/me/summary')).toBe(2);
    expect(callsTo(fetchMock, '/api/auth/refresh')).toBe(1);
  });

  it.each([
    ['login', () => api.auth.login('a@b.c', 'password123'), '/api/auth/login'],
    ['TOTP verify', () => api.auth.totpVerify('challenge', '123456', true), '/api/auth/totp/verify'],
    ['refresh', () => api.auth.refresh(), '/api/auth/refresh']
  ])('never refreshes for a 401 from %s', async (_name, call, url) => {
    const fetchMock = routedFetch({ [url]: [unauthorized], '/api/auth/refresh': [unauthorized] });
    vi.stubGlobal('fetch', fetchMock);
    const listener = vi.fn();
    window.addEventListener(SESSION_ENDED_EVENT, listener);

    try {
      await expect(call()).rejects.toMatchObject({ status: 401 });
      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(listener).not.toHaveBeenCalled();
    } finally {
      window.removeEventListener(SESSION_ENDED_EVENT, listener);
    }
  });

  it('skips the refresh when skipAuthRefresh is set (initial session probe)', async () => {
    const fetchMock = routedFetch({ '/api/auth/me': [unauthorized], '/api/auth/refresh': [() => jsonResponse({ id: 1 })] });
    vi.stubGlobal('fetch', fetchMock);

    await expect(api.auth.me({ skipAuthRefresh: true })).rejects.toMatchObject({ status: 401 });
    expect(callsTo(fetchMock, '/api/auth/refresh')).toBe(0);
  });

  it('sends rememberMe with the TOTP verification', async () => {
    const fetchMock = routedFetch({ '/api/auth/totp/verify': [() => jsonResponse({ id: 1 })] });
    vi.stubGlobal('fetch', fetchMock);

    await api.auth.totpVerify('challenge-1', '123456', true);

    expect(fetchMock).toHaveBeenCalledWith('/api/auth/totp/verify', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ challengeId: 'challenge-1', code: '123456', rememberMe: true })
    }));
  });

  it('sends the final position heartbeat with keepalive', async () => {
    const fetchMock = routedFetch({ '/api/me/lessons/7/position': [() => jsonResponse({ lessonId: 7 })] });
    vi.stubGlobal('fetch', fetchMock);

    await api.me.sendPositionBeacon(7, { sectionId: 'practice-loop', scrollPercent: 40, secondsDelta: 12 });

    expect(fetchMock).toHaveBeenCalledWith('/api/me/lessons/7/position', expect.objectContaining({
      method: 'PUT',
      keepalive: true,
      body: JSON.stringify({ sectionId: 'practice-loop', scrollPercent: 40, secondsDelta: 12 })
    }));
  });
});
