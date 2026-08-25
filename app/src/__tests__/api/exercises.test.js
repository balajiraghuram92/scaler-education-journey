import { describe, expect, it, vi } from 'vitest';
import { api } from '../../api/client';

function jsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Service Unavailable',
    headers: new Headers({ 'content-type': 'application/json' }),
    json: vi.fn().mockResolvedValue(body)
  };
}

describe('exercise API client', () => {
  it('loads learner-safe exercise metadata', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: 'exercise-1', files: [], evidence: [] }));
    vi.stubGlobal('fetch', fetchMock);

    await api.exercises.getMetadata('exercise-1');

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/exercises/exercise-1',
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('sends only the complete file payload to Run', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ status: 'success' }));
    vi.stubGlobal('fetch', fetchMock);
    const files = [
      { path: 'src/main/java/Point.java', content: 'point' },
      { path: 'src/main/java/ThreedPoint.java', content: 'three' }
    ];

    await api.exercises.run('exercise/one', files, { clientRequestId: 'request-1' });

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/exercises/exercise%2Fone/run',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ files, clientRequestId: 'request-1' })
      })
    );
  });

  it('uses the Check endpoint separately from Run', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ status: 'testFailure' }));
    vi.stubGlobal('fetch', fetchMock);

    await api.exercises.check('exercise-1', []);

    expect(fetchMock.mock.calls[0][0]).toBe('/api/exercises/exercise-1/check');
    expect(fetchMock.mock.calls[0][1].method).toBe('POST');
  });

  it('normalizes an API problem response', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({
      title: 'Exercise runner unavailable.',
      detail: 'The exercise execution service is temporarily unavailable.'
    }, 503));
    vi.stubGlobal('fetch', fetchMock);

    await expect(api.exercises.run('exercise-1', [])).rejects.toMatchObject({
      status: 503,
      message: 'The exercise execution service is temporarily unavailable.'
    });
  });
});
