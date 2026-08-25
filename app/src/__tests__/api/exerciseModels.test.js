import { describe, expect, it } from 'vitest';
import { EVIDENCE_STATUSES, mergeEvidence } from '../../api/exerciseModels';

describe('exercise model helpers', () => {
  it('merges execution evidence by stable ID and preserves metadata order', () => {
    const metadataEvidence = [
      { id: 'first', label: 'First behavior' },
      { id: 'second', label: 'Second behavior' },
      { id: 'third', label: 'Third behavior' }
    ];

    const merged = mergeEvidence(metadataEvidence, [
      { id: 'third', status: 'failed', message: 'Failed third.' },
      { id: 'first', status: 'passed', message: null }
    ]);

    expect(merged).toEqual([
      { id: 'first', label: 'First behavior', status: 'passed', message: null },
      { id: 'second', label: 'Second behavior', status: EVIDENCE_STATUSES.NOT_RUN, durationMilliseconds: 0, message: null },
      { id: 'third', label: 'Third behavior', status: 'failed', message: 'Failed third.' }
    ]);
  });
});
