import React from 'react';
import { Flag } from 'lucide-react';

const STAGES = ['New', 'Translated', 'Reviewed', 'Approved'];

/**
 * Stage indicator shared by the Strings table and the edit drawer:
 * an amber flag plus "Needs Review" when flagged, otherwise a four-dot
 * track plus a one-word label.
 */
export default function StageIndicator({ stage, needsReview }) {
  if (needsReview) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#A6772C', fontWeight: '600', fontSize: '0.8rem' }}>
        <Flag size={14} />
        <span>Needs Review</span>
      </div>
    );
  }

  const stageIndex = STAGES.indexOf(stage);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        {STAGES.map((s, sIdx) => {
          const isFilled = stageIndex >= sIdx && stageIndex !== -1;
          return (
            <span
              key={s}
              title={s}
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isFilled ? 'var(--color-sage, #2C5E55)' : '#FFFFFF',
                border: isFilled ? 'none' : '1.5px solid var(--color-ink-muted, #6B7280)',
                display: 'inline-block'
              }}
            />
          );
        })}
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-muted, #6B7280)', marginTop: '2px' }}>
        {stage}
      </div>
    </div>
  );
}
