import { describe, expect, it, vi } from 'vitest';
import { api } from '../../api/client';

function jsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Bad Request',
    headers: new Headers({ 'content-type': 'application/json' }),
    json: vi.fn().mockResolvedValue(body)
  };
}

describe('localizationOps API client', () => {
  it('builds the usage query string from set parameters', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ meters: [] }));
    vi.stubGlobal('fetch', fetchMock);

    await api.localizationOps.getUsage({ project: 'p1', month: '2026-11' });

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/localization/ops/usage?project=p1&month=2026-11',
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('omits unset usage parameters from the query string', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ meters: [] }));
    vi.stubGlobal('fetch', fetchMock);

    await api.localizationOps.getUsage({ month: '2026-11' });
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/localization/ops/usage?month=2026-11',
      expect.objectContaining({ method: 'GET' })
    );

    await api.localizationOps.getUsage({});
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/localization/ops/usage',
      expect.objectContaining({ method: 'GET' })
    );
  });
});
