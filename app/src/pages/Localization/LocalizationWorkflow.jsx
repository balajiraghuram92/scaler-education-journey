import React, { useState, useEffect, useCallback } from 'react';
import { ArrowUp, ArrowDown, Trash2, Play, Plus, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import LocalizationShell from './LocalizationShell';
import useLocalizationProject from './useLocalizationProject';
import { api } from '../../api/client';
import { timeAgo } from '../../utils/timeAgo';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';

const ALL_ACTIONS = [
  'Mark Translated',
  'Send to Review',
  'Approve',
  'Auto-Translate via Google MT',
  'Post to Marketplace',
  'Run MT Optimize',
  'Score QPS',
  'Auto-Route'
];

export default function LocalizationWorkflow() {
  const { slug: projectSlug, loading: projectLoading, error: projectError } = useLocalizationProject();
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [runningStepId, setRunningStepId] = useState(null);
  const [stepNotice, setStepNotice] = useState(null); // { stepId, type: 'info'|'error'|'success', message }

  const fetchSteps = useCallback(async () => {
    if (!projectSlug) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.localization.getWorkflow(projectSlug);
      if (Array.isArray(data)) {
        setSteps(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to load workflow steps.');
    } finally {
      setLoading(false);
    }
  }, [projectSlug]);

  useEffect(() => {
    fetchSteps();
  }, [fetchSteps]);

  const handleAddStep = async () => {
    try {
      const newStep = await api.localization.addWorkflowStep(projectSlug, {
        trigger: 'On Manual Click',
        action: 'Mark Translated',
        conditionExpression: null
      });
      setSteps((prev) => [...prev, newStep]);
      setStepNotice({ stepId: newStep.id, type: 'success', message: 'Step added successfully.' });
    } catch (err) {
      setStepNotice({ stepId: null, type: 'error', message: err.message || 'Failed to add step.' });
    }
  };

  const handleReorder = async (stepId, direction) => {
    try {
      await api.localization.reorderWorkflowStep(projectSlug, stepId, direction);
      await fetchSteps();
    } catch (err) {
      setStepNotice({ stepId, type: 'error', message: err.message || `Failed to move step ${direction}.` });
    }
  };

  const handleDelete = async (stepId) => {
    try {
      await api.localization.deleteWorkflowStep(projectSlug, stepId);
      setSteps((prev) => prev.filter((s) => s.id !== stepId));
    } catch (err) {
      setStepNotice({ stepId, type: 'error', message: err.message || 'Failed to delete step.' });
    }
  };

  const handleUpdateStep = async (step, updates) => {
    const prevStep = { ...step };
    setSteps((prev) => prev.map((s) => (s.id === step.id ? { ...s, ...updates } : s)));
    try {
      await api.localization.updateWorkflowStep(projectSlug, step.id, {
        trigger: updates.trigger !== undefined ? updates.trigger : step.trigger,
        action: updates.action !== undefined ? updates.action : step.action,
        conditionExpression: updates.conditionExpression !== undefined ? updates.conditionExpression : step.conditionExpression
      });
    } catch (err) {
      setSteps((prev) => prev.map((s) => (s.id === step.id ? prevStep : s)));
      setStepNotice({ stepId: step.id, type: 'error', message: err.message || 'Failed to update workflow step.' });
    }
  };

  const handleRun = async (stepId) => {
    setRunningStepId(stepId);
    setStepNotice(null);
    try {
      const updated = await api.localization.runWorkflowStep(projectSlug, stepId);
      setSteps((prev) => prev.map((s) => (s.id === stepId ? updated : s)));
      setStepNotice({
        stepId,
        type: 'success',
        message: `Run successful: ${updated.lastRunOutcome}`
      });
    } catch (err) {
      const is501 = err.status === 501;
      setStepNotice({
        stepId,
        type: is501 ? 'boundary' : 'error',
        message: is501
          ? `501 Not Implemented (Hand-Written AI Boundary): ${err.message}`
          : err.message || 'Execution failed.'
      });
    } finally {
      setRunningStepId(null);
    }
  };

  const renderNotice = (notice) => (
    <div
      style={{
        padding: '0.6rem 0.85rem',
        borderRadius: '4px',
        fontSize: '0.8rem',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        backgroundColor:
          notice.type === 'boundary'
            ? '#FEF3C7'
            : notice.type === 'error'
            ? '#FEE2E2'
            : '#ECFDF5',
        color:
          notice.type === 'boundary'
            ? '#92400E'
            : notice.type === 'error'
            ? '#991B1B'
            : '#065F46',
        border: `1px solid ${
          notice.type === 'boundary'
            ? '#FCD34D'
            : notice.type === 'error'
            ? '#FCA5A5'
            : '#A7F3D0'
        }`
      }}
    >
      {notice.type === 'success' ? (
        <CheckCircle2 size={14} />
      ) : (
        <AlertCircle size={14} />
      )}
      <span>{notice.message}</span>
    </div>
  );

  return (
    <LocalizationShell activeTab="workflow">
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
            Localization Workflow Orchestrator
          </h2>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
            Define, reorder, and execute sequential translation lifecycle rules.
          </p>
        </div>
      </div>

      {stepNotice && stepNotice.stepId === null && (
        <div style={{ marginBottom: '1rem' }}>
          {renderNotice(stepNotice)}
        </div>
      )}

      {projectError ? (
        <ErrorState error={{ message: projectError }} title="Unable to Load Project" />
      ) : error ? (
        <ErrorState error={error} onRetry={fetchSteps} title="Unable to Load Workflow" />
      ) : (projectLoading || !projectSlug || loading) ? (
        <LoadingState message="Loading workflow configuration..." />
      ) : steps.length === 0 ? (
        <EmptyState message="No workflow steps defined." icon="⚙️" />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
          {steps.map((step, idx) => {
            const isFirst = idx === 0;
            const isLast = idx === steps.length - 1;
            const noticeForThis = stepNotice && stepNotice.stepId === step.id ? stepNotice : null;

            return (
              <div
                key={step.id}
                style={{
                  backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
                  border: '1px solid var(--color-border-subtle, #E2DDD5)',
                  borderRadius: '8px',
                  padding: '1.25rem 1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem',
                  transition: 'border-color 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  {/* Step Numeral + Trigger & Action selects */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap', flex: 1 }}>
                    {/* Numeral */}
                    <span
                      style={{
                        fontFamily: 'var(--font-serif, "Newsreader", serif)',
                        fontSize: '1.85rem',
                        fontWeight: '700',
                        color: 'var(--color-sage, #2C5E55)',
                        minWidth: '28px'
                      }}
                    >
                      {idx + 1}
                    </span>

                    {/* Trigger Select */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <label style={{ fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-ink-muted, #6B7280)' }}>
                        Trigger
                      </label>
                      <select
                        value={step.trigger}
                        onChange={(e) => handleUpdateStep(step, { trigger: e.target.value })}
                        style={{
                          padding: '0.4rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid var(--color-border-subtle, #E2DDD5)',
                          backgroundColor: '#FFFFFF',
                          color: 'var(--color-ink, #1F2937)',
                          fontSize: '0.85rem',
                          fontWeight: '500',
                          cursor: 'pointer'
                        }}
                      >
                        <option value="On Manual Click">On Manual Click</option>
                      </select>
                    </div>

                    {/* Action Select */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <label style={{ fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-ink-muted, #6B7280)' }}>
                        Action
                      </label>
                      <select
                        value={step.action}
                        onChange={(e) => handleUpdateStep(step, { action: e.target.value })}
                        style={{
                          padding: '0.4rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid var(--color-border-subtle, #E2DDD5)',
                          backgroundColor: '#FFFFFF',
                          color: 'var(--color-ink, #1F2937)',
                          fontSize: '0.85rem',
                          fontWeight: '600',
                          cursor: 'pointer'
                        }}
                      >
                        {ALL_ACTIONS.map((a) => (
                          <option key={a} value={a}>
                            {a}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Icon Actions: Up, Down, Delete, Run */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {/* Up button */}
                    <button
                      type="button"
                      disabled={isFirst}
                      onClick={() => handleReorder(step.id, 'up')}
                      title="Move Step Up"
                      style={{
                        background: 'none',
                        border: '1px solid var(--color-border-subtle, #E2DDD5)',
                        borderRadius: '4px',
                        padding: '6px',
                        cursor: isFirst ? 'not-allowed' : 'pointer',
                        color: isFirst ? 'var(--color-border-subtle, #E2DDD5)' : 'var(--color-ink, #1F2937)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      <ArrowUp size={14} />
                    </button>

                    {/* Down button */}
                    <button
                      type="button"
                      disabled={isLast}
                      onClick={() => handleReorder(step.id, 'down')}
                      title="Move Step Down"
                      style={{
                        background: 'none',
                        border: '1px solid var(--color-border-subtle, #E2DDD5)',
                        borderRadius: '4px',
                        padding: '6px',
                        cursor: isLast ? 'not-allowed' : 'pointer',
                        color: isLast ? 'var(--color-border-subtle, #E2DDD5)' : 'var(--color-ink, #1F2937)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      <ArrowDown size={14} />
                    </button>

                    {/* Delete button */}
                    <button
                      type="button"
                      onClick={() => handleDelete(step.id)}
                      title="Delete Step"
                      style={{
                        background: 'none',
                        border: '1px solid #FEE2E2',
                        borderRadius: '4px',
                        padding: '6px',
                        cursor: 'pointer',
                        color: '#DC2626',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      <Trash2 size={14} />
                    </button>

                    {/* Run button */}
                    <button
                      type="button"
                      disabled={runningStepId === step.id}
                      onClick={() => handleRun(step.id)}
                      title="Run Step"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: '6px',
                        borderRadius: '4px',
                        border: 'none',
                        backgroundColor: 'var(--color-sage, #2C5E55)',
                        color: '#FFFFFF',
                        cursor: runningStepId === step.id ? 'wait' : 'pointer'
                      }}
                    >
                      {runningStepId === step.id ? (
                        <RefreshCw size={13} className="spin" />
                      ) : (
                        <Play size={13} fill="currentColor" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Subtitle Line: LastRunOutcome or Italic "Never run yet" */}
                <div style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                  {step.lastRunAt ? (
                    <span>
                      Last ran {timeAgo(step.lastRunAt)} — {step.lastRunOutcome || 'Completed'}
                    </span>
                  ) : (
                    <em style={{ fontStyle: 'italic' }}>Never run yet</em>
                  )}
                </div>

                {/* Inline execution notice */}
                {noticeForThis && renderNotice(noticeForThis)}
              </div>
            );
          })}
        </div>
      )}

      {/* "+ Add Step" control */}
      <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
        <button
          type="button"
          onClick={handleAddStep}
          title="Add Step"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            backgroundColor: '#FFFFFF',
            border: '1px dashed var(--color-sage, #2C5E55)',
            color: 'var(--color-sage, #2C5E55)',
            borderRadius: '6px',
            padding: '0.6rem',
            cursor: 'pointer'
          }}
        >
          <Plus size={16} />
        </button>
      </div>
    </LocalizationShell>
  );
}
