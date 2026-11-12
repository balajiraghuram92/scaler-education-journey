import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { api } from '../../api/client';
import { LoadingState, ErrorState, EmptyState } from '../../components/common/StateViews';

const USAGE_METERS = ['machine-translation', 'llm-optimize', 'llm-score'];
const UNIT_KINDS = ['char', 'input-token', 'output-token'];
const TIERS = ['Silver', 'Gold', 'Platinum'];
const ACCESS_DENIED_MESSAGE = 'Operations access requires an administrator account.';

function currentUtcMonth() {
  return new Date().toISOString().slice(0, 7);
}

function formatUnits(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toLocaleString('en-US');
}

function formatCost(value) {
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(4);
}

function formatDate(value) {
  if (!value) return '—';
  const time = new Date(value).getTime();
  if (Number.isNaN(time)) return value;
  return new Date(value).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDateTime(value) {
  if (!value) return '—';
  const time = new Date(value).getTime();
  if (Number.isNaN(time)) return value;
  return new Date(value).toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function toDateInput(value) {
  if (!value) return '';
  const time = new Date(value).getTime();
  if (Number.isNaN(time)) return '';
  return new Date(value).toISOString().slice(0, 10);
}

const opsTd = { padding: '0.6rem 0.85rem', borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)', color: 'var(--color-ink, #1F2937)' };
const subheadingStyle = { margin: '0 0 0.6rem 0', fontSize: '0.9rem', fontWeight: '700', color: 'var(--color-ink, #1F2937)' };
const labelStyle = { display: 'block', fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--color-ink-muted, #6B7280)', marginBottom: '0.3rem' };
const inputStyle = { padding: '0.45rem 0.7rem', borderRadius: '6px', border: '1px solid var(--color-border-subtle, #E2DDD5)', backgroundColor: '#FFFFFF', color: 'var(--color-ink, #1F2937)', fontSize: '0.85rem', outline: 'none' };

function Section({ title, children }) {
  return (
    <section
      style={{
        backgroundColor: '#FFFFFF',
        border: '1px solid var(--color-border-subtle, #E2DDD5)',
        borderRadius: '8px',
        padding: '1.25rem 1.5rem',
        marginBottom: '1.5rem'
      }}
    >
      <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', fontFamily: 'var(--font-serif, "Newsreader", serif)', color: 'var(--color-ink, #1F2937)' }}>
        {title}
      </h2>
      {children}
    </section>
  );
}

function OpsTable({ headers, children }) {
  return (
    <div style={{ border: '1px solid var(--color-border-subtle, #E2DDD5)', overflowX: 'auto', marginBottom: '1.25rem' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
        <thead>
          <tr
            style={{
              borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
              fontSize: '0.72rem',
              letterSpacing: '0.04em',
              color: 'var(--color-ink-muted, #6B7280)',
              textTransform: 'uppercase'
            }}
          >
            {headers.map((h) => (
              <th key={h} style={{ padding: '0.6rem 0.85rem' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

function DailyChart({ meter, days }) {
  const sorted = [...days].sort((a, b) => (a.date < b.date ? -1 : 1));
  const max = Math.max(1, ...sorted.map((d) => d.units || 0));
  const width = 560;
  const height = 150;
  const padLeft = 8;
  const padRight = 8;
  const padTop = 14;
  const padBottom = 26;
  const innerWidth = width - padLeft - padRight;
  const innerHeight = height - padTop - padBottom;
  const slot = innerWidth / Math.max(1, sorted.length);
  const barWidth = Math.max(3, slot - 5);
  const labelStep = Math.max(1, Math.ceil(sorted.length / 8));
  return (
    <div style={{ marginBottom: '1rem' }}>
      <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-ink, #1F2937)', marginBottom: '0.25rem' }}>
        {meter}
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', display: 'block' }} role="img" aria-label={`${meter} daily usage`}>
        <text x={padLeft} y={padTop - 4} fontSize="9" fill="#6B7280">max {formatUnits(max)}</text>
        {sorted.map((day, i) => {
          const barHeight = Math.max(day.units > 0 ? 2 : 0, ((day.units || 0) / max) * innerHeight);
          const x = padLeft + i * slot + (slot - barWidth) / 2;
          const y = padTop + innerHeight - barHeight;
          return (
            <rect key={day.date} x={x} y={y} width={barWidth} height={barHeight} fill="var(--color-sage, #2C5E55)">
              <title>{`${day.date}: ${formatUnits(day.units)} units`}</title>
            </rect>
          );
        })}
        {sorted.map((day, i) => (
          i % labelStep === 0 ? (
            <text key={`label-${day.date}`} x={padLeft + i * slot + slot / 2} y={height - 8} textAnchor="middle" fontSize="9" fill="#6B7280">
              {day.date ? day.date.slice(5) : ''}
            </text>
          ) : null
        ))}
      </svg>
    </div>
  );
}

export default function LocalizationOps() {
  const [accessDenied, setAccessDenied] = useState(false);
  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);
  const [selectedProject, setSelectedProject] = useState('');
  const [month, setMonth] = useState(currentUtcMonth);

  const [usage, setUsage] = useState(null);
  const [usageLoading, setUsageLoading] = useState(true);
  const [usageError, setUsageError] = useState(null);

  const [events, setEvents] = useState([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState(null);

  const [rates, setRates] = useState([]);
  const [ratesLoading, setRatesLoading] = useState(true);
  const [ratesError, setRatesError] = useState(null);
  const [rateForm, setRateForm] = useState({ meter: USAGE_METERS[0], unitKind: UNIT_KINDS[0], usdPerMillion: '', validFrom: '' });
  const [addingRate, setAddingRate] = useState(false);
  const [rateFormError, setRateFormError] = useState(null);
  const [rateSaved, setRateSaved] = useState(false);

  const [caps, setCaps] = useState([]);
  const [capsLoading, setCapsLoading] = useState(false);
  const [capsError, setCapsError] = useState(null);

  const [controls, setControls] = useState(null);
  const [controlsLoading, setControlsLoading] = useState(false);
  const [controlsError, setControlsError] = useState(null);
  const [controlsForm, setControlsForm] = useState({ aiEnabled: true, mtLimit: '', llmLimit: '' });
  const [controlsTouched, setControlsTouched] = useState({ aiEnabled: false, mt: false, llm: false });
  const [savingControls, setSavingControls] = useState(false);
  const [controlsFormError, setControlsFormError] = useState(null);
  const [controlsSaved, setControlsSaved] = useState(false);

  const [teams, setTeams] = useState([]);
  const [teamsLoading, setTeamsLoading] = useState(true);
  const [teamsError, setTeamsError] = useState(null);

  const [agreement, setAgreement] = useState(null);
  const [agreementLoading, setAgreementLoading] = useState(false);
  const [agreementError, setAgreementError] = useState(null);
  const [agreementForm, setAgreementForm] = useState({ tier: TIERS[0], validFrom: '', teamByLocale: {} });
  const [savingAgreement, setSavingAgreement] = useState(false);
  const [agreementFormError, setAgreementFormError] = useState(null);
  const [agreementSaved, setAgreementSaved] = useState(false);

  const noteAccessDenied = useCallback((err) => {
    if (err && err.status === 403) {
      setAccessDenied(true);
      return true;
    }
    return false;
  }, []);

  function applyControlsToForm(data) {
    const list = Array.isArray(data?.caps) ? data.caps : [];
    const mt = list.find((c) => c.kind === 'machine-translation');
    const llm = list.find((c) => c.kind === 'llm');
    setControlsForm({
      aiEnabled: data?.aiEnabled !== false,
      mtLimit: mt?.monthlyLimit === null || mt?.monthlyLimit === undefined ? '' : String(mt.monthlyLimit),
      llmLimit: llm?.monthlyLimit === null || llm?.monthlyLimit === undefined ? '' : String(llm.monthlyLimit)
    });
    setControlsTouched({ aiEnabled: false, mt: false, llm: false });
  }

  function applyAgreementToForm(data) {
    const list = Array.isArray(data?.teams) ? data.teams : [];
    const teamByLocale = {};
    list.forEach((t) => {
      if (t.vendorTeamId !== null && t.vendorTeamId !== undefined) teamByLocale[t.localeCode] = String(t.vendorTeamId);
    });
    setAgreementForm({
      tier: data?.tier || TIERS[0],
      validFrom: toDateInput(data?.validFrom),
      teamByLocale
    });
  }

  const fetchProjects = useCallback(async () => {
    setProjectsLoading(true);
    setProjectsError(null);
    try {
      const data = await api.localization.getProjects();
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      if (!noteAccessDenied(err)) setProjectsError(err.message || 'Failed to load projects.');
    } finally {
      setProjectsLoading(false);
    }
  }, [noteAccessDenied]);

  useEffect(() => { fetchProjects(); }, [fetchProjects]);

  const fetchUsage = useCallback(async () => {
    setUsageLoading(true);
    setUsageError(null);
    try {
      const data = await api.localizationOps.getUsage({
        project: selectedProject || undefined,
        month: month || undefined
      });
      setUsage(data);
    } catch (err) {
      if (!noteAccessDenied(err)) setUsageError(err.message || 'Failed to load usage.');
    } finally {
      setUsageLoading(false);
    }
  }, [selectedProject, month, noteAccessDenied]);

  useEffect(() => { fetchUsage(); }, [fetchUsage]);

  const fetchEvents = useCallback(async () => {
    setEventsLoading(true);
    setEventsError(null);
    try {
      const data = await api.localizationOps.getUsageEvents({
        project: selectedProject || undefined,
        limit: 100
      });
      setEvents(Array.isArray(data) ? data : data ? [data] : []);
    } catch (err) {
      if (!noteAccessDenied(err)) setEventsError(err.message || 'Failed to load usage events.');
    } finally {
      setEventsLoading(false);
    }
  }, [selectedProject, noteAccessDenied]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  const fetchRates = useCallback(async () => {
    setRatesLoading(true);
    setRatesError(null);
    try {
      const data = await api.localizationOps.getRates();
      setRates(Array.isArray(data) ? data : []);
    } catch (err) {
      if (!noteAccessDenied(err)) setRatesError(err.message || 'Failed to load rates.');
    } finally {
      setRatesLoading(false);
    }
  }, [noteAccessDenied]);

  useEffect(() => { fetchRates(); }, [fetchRates]);

  const fetchTeams = useCallback(async () => {
    setTeamsLoading(true);
    setTeamsError(null);
    try {
      const data = await api.localizationOps.getTeams();
      setTeams(Array.isArray(data) ? data : []);
    } catch (err) {
      if (!noteAccessDenied(err)) setTeamsError(err.message || 'Failed to load vendor teams.');
    } finally {
      setTeamsLoading(false);
    }
  }, [noteAccessDenied]);

  useEffect(() => { fetchTeams(); }, [fetchTeams]);

  const fetchCaps = useCallback(async () => {
    if (!selectedProject) {
      setCaps([]);
      setCapsError(null);
      return;
    }
    setCapsLoading(true);
    setCapsError(null);
    try {
      const data = await api.localizationOps.getControls(selectedProject);
      setCaps(Array.isArray(data?.caps) ? data.caps : []);
    } catch (err) {
      if (!noteAccessDenied(err)) setCapsError(err.message || 'Failed to load caps.');
    } finally {
      setCapsLoading(false);
    }
  }, [selectedProject, noteAccessDenied]);

  useEffect(() => { fetchCaps(); }, [fetchCaps]);

  const fetchControls = useCallback(async () => {
    if (!selectedProject) {
      setControls(null);
      setControlsError(null);
      return;
    }
    setControlsLoading(true);
    setControlsError(null);
    setControlsSaved(false);
    try {
      const data = await api.localizationOps.getControls(selectedProject);
      setControls(data);
      applyControlsToForm(data);
    } catch (err) {
      if (!noteAccessDenied(err)) setControlsError(err.message || 'Failed to load controls.');
    } finally {
      setControlsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProject, noteAccessDenied]);

  useEffect(() => { fetchControls(); }, [fetchControls]);

  const fetchAgreement = useCallback(async () => {
    if (!selectedProject) {
      setAgreement(null);
      setAgreementError(null);
      return;
    }
    setAgreementLoading(true);
    setAgreementError(null);
    setAgreementSaved(false);
    try {
      const data = await api.localizationOps.getAgreement(selectedProject);
      setAgreement(data);
      applyAgreementToForm(data);
    } catch (err) {
      if (err && err.status === 404) {
        setAgreement(null);
        applyAgreementToForm(null);
      } else if (!noteAccessDenied(err)) {
        setAgreementError(err.message || 'Failed to load the service agreement.');
      }
    } finally {
      setAgreementLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProject, noteAccessDenied]);

  useEffect(() => { fetchAgreement(); }, [fetchAgreement]);

  const handleSaveControls = async () => {
    const body = {};
    if (controlsTouched.aiEnabled) body.aiEnabled = controlsForm.aiEnabled;
    if (controlsTouched.mt) body.machineTranslationMonthlyLimit = controlsForm.mtLimit === '' ? null : Number(controlsForm.mtLimit);
    if (controlsTouched.llm) body.llmMonthlyLimit = controlsForm.llmLimit === '' ? null : Number(controlsForm.llmLimit);
    setSavingControls(true);
    setControlsFormError(null);
    setControlsSaved(false);
    try {
      const data = await api.localizationOps.updateControls(selectedProject, body);
      setControls(data);
      setCaps(Array.isArray(data?.caps) ? data.caps : []);
      applyControlsToForm(data);
      setControlsSaved(true);
    } catch (err) {
      if (!noteAccessDenied(err)) setControlsFormError(err.message || 'Failed to save controls.');
    } finally {
      setSavingControls(false);
    }
  };

  const handleAddRate = async (e) => {
    e.preventDefault();
    setAddingRate(true);
    setRateFormError(null);
    setRateSaved(false);
    try {
      const body = {
        meter: rateForm.meter,
        unitKind: rateForm.unitKind,
        usdPerMillion: Number(rateForm.usdPerMillion)
      };
      if (rateForm.validFrom) body.validFrom = rateForm.validFrom;
      await api.localizationOps.addRate(body);
      setRateForm((prev) => ({ ...prev, usdPerMillion: '', validFrom: '' }));
      setRateSaved(true);
      await fetchRates();
    } catch (err) {
      if (!noteAccessDenied(err)) setRateFormError(err.message || 'Failed to add rate.');
    } finally {
      setAddingRate(false);
    }
  };

  const selectedProjectLocales = (projects.find((p) => p.slug === selectedProject)?.locales || []).map((l) => l.localeCode);
  const agreementTeamLocales = (Array.isArray(agreement?.teams) ? agreement.teams : []).map((t) => t.localeCode);
  const agreementLocales = selectedProjectLocales.length > 0 ? selectedProjectLocales : [...new Set(agreementTeamLocales)];

  const handleSaveAgreement = async () => {
    const teams = agreementLocales
      .filter((localeCode) => agreementForm.teamByLocale[localeCode])
      .map((localeCode) => ({ localeCode, vendorTeamId: Number(agreementForm.teamByLocale[localeCode]) }));
    const body = { tier: agreementForm.tier, validFrom: agreementForm.validFrom, teams };
    setSavingAgreement(true);
    setAgreementFormError(null);
    setAgreementSaved(false);
    try {
      const data = await api.localizationOps.saveAgreement(selectedProject, body);
      setAgreement(data);
      applyAgreementToForm(data);
      setAgreementSaved(true);
    } catch (err) {
      if (!noteAccessDenied(err)) setAgreementFormError(err.message || 'Failed to save the service agreement.');
    } finally {
      setSavingAgreement(false);
    }
  };

  const controlsDirty = controlsTouched.aiEnabled || controlsTouched.mt || controlsTouched.llm;

  const byDayByMeter = {};
  (usage?.byDay || []).forEach((day) => {
    if (!byDayByMeter[day.meter]) byDayByMeter[day.meter] = [];
    byDayByMeter[day.meter].push(day);
  });
  const usageRowCount = (usage?.meters || []).length + (usage?.byOperation || []).length + (usage?.byLocale || []).length + (usage?.byDay || []).length;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-parchment, #F8F6F0)' }}>
      <div style={{ maxWidth: '1380px', margin: '0 auto', padding: '2rem', boxSizing: 'border-box' }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <Link
            to="/lab-projects/localization"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.85rem',
              color: 'var(--color-sage, #2C5E55)',
              textDecoration: 'none',
              fontWeight: '600'
            }}
          >
            <ArrowLeft size={16} /> Back to Localization Lab
          </Link>
        </div>

        <div style={{ marginBottom: '1.75rem' }}>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-sage, #2C5E55)', fontWeight: '700' }}>
            Administration
          </span>
          <h1
            style={{
              margin: '0.25rem 0 0 0',
              fontSize: '1.75rem',
              fontFamily: 'var(--font-serif, "Newsreader", serif)',
              color: 'var(--color-ink, #1F2937)'
            }}
          >
            Localization Operations
          </h1>
          <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.9rem', color: 'var(--color-ink-muted, #6B7280)' }}>
            Provider usage, monthly caps, the AI switch, rates, vendor teams and service agreements.
          </p>
        </div>

        {accessDenied ? (
          <div
            style={{
              padding: '1.5rem 2rem',
              backgroundColor: '#FFFBEB',
              border: '1px solid #FDE68A',
              borderRadius: '8px',
              color: '#92400E',
              fontSize: '0.95rem',
              fontWeight: '600',
              textAlign: 'center'
            }}
          >
            {ACCESS_DENIED_MESSAGE}
          </div>
        ) : (
          <>
            <Section title="Project and month">
              {projectsLoading ? (
                <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>Loading projects…</p>
              ) : projectsError ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '0.85rem', color: '#991B1B' }}>{projectsError}</span>
                  <button
                    type="button"
                    onClick={fetchProjects}
                    style={{ padding: '0.35rem 0.75rem', borderRadius: '4px', border: '1px solid var(--color-border-subtle, #E2DDD5)', backgroundColor: '#FFFFFF', fontSize: '0.8rem', fontWeight: '600', cursor: 'pointer' }}
                  >
                    Retry
                  </button>
                </div>
              ) : (
                <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
                  <div>
                    <label htmlFor="ops-project" style={labelStyle}>Project</label>
                    <select id="ops-project" value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)} style={{ ...inputStyle, minWidth: '240px' }}>
                      <option value="">All projects</option>
                      {projects.map((p) => (
                        <option key={p.slug} value={p.slug}>{p.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label htmlFor="ops-month" style={labelStyle}>Month</label>
                    <input id="ops-month" type="month" value={month} onChange={(e) => setMonth(e.target.value)} style={inputStyle} />
                  </div>
                </div>
              )}
            </Section>

            {selectedProject && (
              <Section title="Caps">
                {capsLoading ? (
                  <LoadingState message="Loading caps..." />
                ) : capsError ? (
                  <ErrorState error={capsError} onRetry={fetchCaps} title="Unable to Load Caps" />
                ) : caps.length === 0 ? (
                  <EmptyState message="No cap information for this project." icon="📊" />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {caps.map((cap) => {
                      const hasLimit = cap.monthlyLimit !== null && cap.monthlyLimit !== undefined;
                      const ratio = hasLimit && cap.monthlyLimit > 0 ? (cap.used || 0) / cap.monthlyLimit : 0;
                      const barColor = hasLimit && (cap.used || 0) >= cap.monthlyLimit
                        ? '#DC2626'
                        : hasLimit && ratio >= 0.8
                        ? '#F59E0B'
                        : 'var(--color-sage, #2C5E55)';
                      return (
                        <div key={cap.kind}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.35rem' }}>
                            <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--color-ink, #1F2937)' }}>
                              {cap.kind}
                            </span>
                            <span style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                              {hasLimit ? `${formatUnits(cap.used)} / ${formatUnits(cap.monthlyLimit)}` : `${formatUnits(cap.used)} used · No cap`}
                            </span>
                          </div>
                          {hasLimit && (
                            <div style={{ height: '10px', backgroundColor: '#F3F4F6', borderRadius: '5px', overflow: 'hidden' }}>
                              <div style={{ width: `${Math.min(100, ratio * 100)}%`, height: '100%', backgroundColor: barColor }} />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </Section>
            )}

            {selectedProject && (
              <Section title="Controls">
                {controlsLoading ? (
                  <LoadingState message="Loading controls..." />
                ) : controlsError ? (
                  <ErrorState error={controlsError} onRetry={fetchControls} title="Unable to Load Controls" />
                ) : !controls ? (
                  <EmptyState message="No controls for this project." icon="🎛️" />
                ) : (
                  <div>
                    {controlsFormError && (
                      <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#FEF2F2', border: '1px solid #F87171', borderRadius: '6px', color: '#991B1B', fontSize: '0.85rem', marginBottom: '1rem' }}>
                        {controlsFormError}
                      </div>
                    )}
                    {controlsSaved && (
                      <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: '6px', color: '#166534', fontSize: '0.85rem', marginBottom: '1rem' }}>
                        Controls saved.
                      </div>
                    )}
                    <label htmlFor="ops-ai-enabled" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '0.9rem', fontWeight: '600', color: 'var(--color-ink, #1F2937)', marginBottom: '1rem', cursor: 'pointer' }}>
                      <input
                        id="ops-ai-enabled"
                        type="checkbox"
                        checked={controlsForm.aiEnabled}
                        onChange={(e) => {
                          setControlsForm((prev) => ({ ...prev, aiEnabled: e.target.checked }));
                          setControlsTouched((prev) => ({ ...prev, aiEnabled: true }));
                        }}
                      />
                      AI assistance enabled
                    </label>
                    <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                      <div>
                        <label htmlFor="ops-mt-limit" style={labelStyle}>Machine translation cap (characters)</label>
                        <input
                          id="ops-mt-limit"
                          type="number"
                          min="0"
                          placeholder="No cap"
                          value={controlsForm.mtLimit}
                          onChange={(e) => {
                            setControlsForm((prev) => ({ ...prev, mtLimit: e.target.value }));
                            setControlsTouched((prev) => ({ ...prev, mt: true }));
                          }}
                          style={{ ...inputStyle, minWidth: '200px' }}
                        />
                      </div>
                      <div>
                        <label htmlFor="ops-llm-limit" style={labelStyle}>Model token cap</label>
                        <input
                          id="ops-llm-limit"
                          type="number"
                          min="0"
                          placeholder="No cap"
                          value={controlsForm.llmLimit}
                          onChange={(e) => {
                            setControlsForm((prev) => ({ ...prev, llmLimit: e.target.value }));
                            setControlsTouched((prev) => ({ ...prev, llm: true }));
                          }}
                          style={{ ...inputStyle, minWidth: '200px' }}
                        />
                      </div>
                    </div>
                    <p style={{ margin: '0 0 1rem 0', fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                      Empty a limit to remove the cap. Fields you do not touch are left unchanged.
                    </p>
                    <button
                      type="button"
                      disabled={!controlsDirty || savingControls}
                      onClick={handleSaveControls}
                      style={{
                        padding: '0.55rem 1.25rem',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: !controlsDirty ? 'rgba(44, 94, 85, 0.4)' : 'var(--color-sage, #2C5E55)',
                        color: '#FFFFFF',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        cursor: !controlsDirty || savingControls ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {savingControls ? 'Saving…' : 'Save controls'}
                    </button>
                  </div>
                )}
              </Section>
            )}

            <Section title="Usage this month">
              {usageLoading ? (
                <LoadingState message="Loading usage..." />
              ) : usageError ? (
                <ErrorState error={usageError} onRetry={fetchUsage} title="Unable to Load Usage" />
              ) : !usage || usageRowCount === 0 ? (
                <EmptyState message="No usage recorded for this selection." icon="📊" />
              ) : (
                <div>
                  {(usage.ratesMissing || []).length > 0 && (
                    <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#FEF3C7', border: '1px solid #FCD34D', borderRadius: '6px', color: '#92400E', fontSize: '0.85rem', marginBottom: '1rem' }}>
                      No price set for: {(usage.ratesMissing || []).map((r) => `${r.meter}/${r.unitKind}`).join(', ')}; cost shown as 0 for these.
                    </div>
                  )}
                  {(usage.meters || []).length > 0 && (
                    <div>
                      <h3 style={subheadingStyle}>By meter</h3>
                      <OpsTable headers={['Meter', 'Calls', 'Failed', 'Cache hits', 'Units', 'Units out', 'Cost (USD)']}>
                        {(usage.meters || []).map((row) => (
                          <tr key={row.meter}>
                            <td style={opsTd}>{row.meter}</td>
                            <td style={opsTd}>{formatUnits(row.calls)}</td>
                            <td style={opsTd}>{formatUnits(row.failedCalls)}</td>
                            <td style={opsTd}>{formatUnits(row.cacheHits)}</td>
                            <td style={opsTd}>{formatUnits(row.units)}</td>
                            <td style={opsTd}>{formatUnits(row.unitsOut)}</td>
                            <td style={opsTd}>{formatCost(row.costUsd)}</td>
                          </tr>
                        ))}
                      </OpsTable>
                    </div>
                  )}
                  {(usage.byOperation || []).length > 0 && (
                    <div>
                      <h3 style={subheadingStyle}>By operation</h3>
                      <OpsTable headers={['Meter', 'Operation', 'Calls', 'Failed', 'Cache hits', 'Units', 'Units out', 'Cost (USD)']}>
                        {(usage.byOperation || []).map((row, i) => (
                          <tr key={`${row.meter}-${row.operation}-${i}`}>
                            <td style={opsTd}>{row.meter}</td>
                            <td style={opsTd}>{row.operation}</td>
                            <td style={opsTd}>{formatUnits(row.calls)}</td>
                            <td style={opsTd}>{formatUnits(row.failedCalls)}</td>
                            <td style={opsTd}>{formatUnits(row.cacheHits)}</td>
                            <td style={opsTd}>{formatUnits(row.units)}</td>
                            <td style={opsTd}>{formatUnits(row.unitsOut)}</td>
                            <td style={opsTd}>{formatCost(row.costUsd)}</td>
                          </tr>
                        ))}
                      </OpsTable>
                    </div>
                  )}
                  {(usage.byLocale || []).length > 0 && (
                    <div>
                      <h3 style={subheadingStyle}>By locale</h3>
                      <OpsTable headers={['Meter', 'Locale', 'Calls', 'Units', 'Units out', 'Cost (USD)']}>
                        {(usage.byLocale || []).map((row, i) => (
                          <tr key={`${row.meter}-${row.localeCode}-${i}`}>
                            <td style={opsTd}>{row.meter}</td>
                            <td style={opsTd}>{row.localeCode}</td>
                            <td style={opsTd}>{formatUnits(row.calls)}</td>
                            <td style={opsTd}>{formatUnits(row.units)}</td>
                            <td style={opsTd}>{formatUnits(row.unitsOut)}</td>
                            <td style={opsTd}>{formatCost(row.costUsd)}</td>
                          </tr>
                        ))}
                      </OpsTable>
                    </div>
                  )}
                  {Object.keys(byDayByMeter).length > 0 && (
                    <div>
                      <h3 style={subheadingStyle}>Daily units</h3>
                      {Object.keys(byDayByMeter).sort().map((meter) => (
                        <DailyChart key={meter} meter={meter} days={byDayByMeter[meter]} />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Section>

            <Section title="Rates">
              {ratesLoading ? (
                <LoadingState message="Loading rates..." />
              ) : ratesError ? (
                <ErrorState error={ratesError} onRetry={fetchRates} title="Unable to Load Rates" />
              ) : (
                <div>
                  {(rates || []).length === 0 ? (
                    <EmptyState message="No rates set." icon="💲" />
                  ) : (
                    <OpsTable headers={['Meter', 'Unit kind', 'USD per million', 'Valid from']}>
                      {(rates || []).map((rate) => (
                        <tr key={rate.id}>
                          <td style={opsTd}>{rate.meter}</td>
                          <td style={opsTd}>{rate.unitKind}</td>
                          <td style={opsTd}>{rate.usdPerMillion}</td>
                          <td style={opsTd}>{formatDate(rate.validFrom)}</td>
                        </tr>
                      ))}
                    </OpsTable>
                  )}
                  <h3 style={subheadingStyle}>Add rate</h3>
                  <form onSubmit={handleAddRate} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                    <div>
                      <label htmlFor="ops-rate-meter" style={labelStyle}>Meter</label>
                      <select
                        id="ops-rate-meter"
                        value={rateForm.meter}
                        onChange={(e) => setRateForm((prev) => ({ ...prev, meter: e.target.value }))}
                        style={inputStyle}
                      >
                        {USAGE_METERS.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="ops-rate-unit-kind" style={labelStyle}>Unit kind</label>
                      <select
                        id="ops-rate-unit-kind"
                        value={rateForm.unitKind}
                        onChange={(e) => setRateForm((prev) => ({ ...prev, unitKind: e.target.value }))}
                        style={inputStyle}
                      >
                        {UNIT_KINDS.map((u) => (
                          <option key={u} value={u}>{u}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="ops-rate-price" style={labelStyle}>Price per million (USD)</label>
                      <input
                        id="ops-rate-price"
                        type="number"
                        min="0"
                        step="any"
                        required
                        value={rateForm.usdPerMillion}
                        onChange={(e) => setRateForm((prev) => ({ ...prev, usdPerMillion: e.target.value }))}
                        style={{ ...inputStyle, minWidth: '160px' }}
                      />
                    </div>
                    <div>
                      <label htmlFor="ops-rate-valid-from" style={labelStyle}>Valid from (optional)</label>
                      <input
                        id="ops-rate-valid-from"
                        type="date"
                        value={rateForm.validFrom}
                        onChange={(e) => setRateForm((prev) => ({ ...prev, validFrom: e.target.value }))}
                        style={inputStyle}
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={addingRate}
                      style={{
                        padding: '0.55rem 1.25rem',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: 'var(--color-sage, #2C5E55)',
                        color: '#FFFFFF',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        cursor: addingRate ? 'wait' : 'pointer'
                      }}
                    >
                      {addingRate ? 'Adding…' : 'Add rate'}
                    </button>
                  </form>
                  {rateFormError && (
                    <div style={{ marginTop: '1rem', padding: '0.6rem 0.85rem', backgroundColor: '#FEF2F2', border: '1px solid #F87171', borderRadius: '6px', color: '#991B1B', fontSize: '0.85rem' }}>
                      {rateFormError}
                    </div>
                  )}
                  {rateSaved && !rateFormError && (
                    <div style={{ marginTop: '1rem', padding: '0.6rem 0.85rem', backgroundColor: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: '6px', color: '#166534', fontSize: '0.85rem' }}>
                      Rate added.
                    </div>
                  )}
                </div>
              )}
            </Section>

            <Section title="Teams">
              {teamsLoading ? (
                <LoadingState message="Loading vendor teams..." />
              ) : teamsError ? (
                <ErrorState error={teamsError} onRetry={fetchTeams} title="Unable to Load Teams" />
              ) : teams.length === 0 ? (
                <EmptyState message="No vendor teams found." icon="👥" />
              ) : (
                <OpsTable headers={['Alias', 'Real name', 'Languages']}>
                  {teams.map((team) => (
                    <tr key={team.id}>
                      <td style={opsTd}>{team.alias}</td>
                      <td style={opsTd}>{team.realName}</td>
                      <td style={opsTd}>{team.languages}</td>
                    </tr>
                  ))}
                </OpsTable>
              )}
            </Section>

            {selectedProject && (
              <Section title="Service agreement">
                {agreementLoading ? (
                  <LoadingState message="Loading service agreement..." />
                ) : agreementError ? (
                  <ErrorState error={agreementError} onRetry={fetchAgreement} title="Unable to Load Agreement" />
                ) : (
                  <div>
                    {agreement ? (
                      <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: 'var(--color-ink, #1F2937)' }}>
                        Current: {agreement.tier} • {agreement.clientAlias} • Valid {formatDate(agreement.validFrom)} – {formatDate(agreement.validTo)}
                      </p>
                    ) : (
                      <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                        No agreement yet — fill in the form to create one.
                      </p>
                    )}
                    {agreementFormError && (
                      <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#FEF2F2', border: '1px solid #F87171', borderRadius: '6px', color: '#991B1B', fontSize: '0.85rem', marginBottom: '1rem' }}>
                        {agreementFormError}
                      </div>
                    )}
                    {agreementSaved && !agreementFormError && (
                      <div style={{ padding: '0.6rem 0.85rem', backgroundColor: '#F0FDF4', border: '1px solid #86EFAC', borderRadius: '6px', color: '#166534', fontSize: '0.85rem', marginBottom: '1rem' }}>
                        Agreement saved.
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                      <div>
                        <label htmlFor="ops-agreement-tier" style={labelStyle}>Tier</label>
                        <select
                          id="ops-agreement-tier"
                          value={agreementForm.tier}
                          onChange={(e) => setAgreementForm((prev) => ({ ...prev, tier: e.target.value }))}
                          style={inputStyle}
                        >
                          {TIERS.map((t) => (
                            <option key={t} value={t}>{t}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label htmlFor="ops-agreement-valid-from" style={labelStyle}>Valid from</label>
                        <input
                          id="ops-agreement-valid-from"
                          type="date"
                          value={agreementForm.validFrom}
                          onChange={(e) => setAgreementForm((prev) => ({ ...prev, validFrom: e.target.value }))}
                          style={inputStyle}
                        />
                      </div>
                    </div>
                    {agreementLocales.length === 0 ? (
                      <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                        This project has no locales to assign teams to.
                      </p>
                    ) : (
                      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                        {agreementLocales.map((localeCode) => (
                          <div key={localeCode}>
                            <label htmlFor={`ops-agreement-team-${localeCode}`} style={labelStyle}>{localeCode}</label>
                            <select
                              id={`ops-agreement-team-${localeCode}`}
                              value={agreementForm.teamByLocale[localeCode] || ''}
                              onChange={(e) => setAgreementForm((prev) => ({
                                ...prev,
                                teamByLocale: { ...prev.teamByLocale, [localeCode]: e.target.value }
                              }))}
                              style={{ ...inputStyle, minWidth: '220px' }}
                            >
                              <option value="">No team</option>
                              {teams.map((team) => (
                                <option key={team.id} value={team.id}>{team.alias} ({team.realName})</option>
                              ))}
                            </select>
                          </div>
                        ))}
                      </div>
                    )}
                    <button
                      type="button"
                      disabled={savingAgreement}
                      onClick={handleSaveAgreement}
                      style={{
                        padding: '0.55rem 1.25rem',
                        borderRadius: '6px',
                        border: 'none',
                        backgroundColor: 'var(--color-sage, #2C5E55)',
                        color: '#FFFFFF',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        cursor: savingAgreement ? 'wait' : 'pointer'
                      }}
                    >
                      {savingAgreement ? 'Saving…' : 'Save agreement'}
                    </button>
                  </div>
                )}
              </Section>
            )}

            <Section title="Recent events">
              {eventsLoading ? (
                <LoadingState message="Loading usage events..." />
              ) : eventsError ? (
                <ErrorState error={eventsError} onRetry={fetchEvents} title="Unable to Load Events" />
              ) : events.length === 0 ? (
                <EmptyState message="No usage events for this selection." icon="📋" />
              ) : (
                <OpsTable headers={['Time', 'Project', 'Meter', 'Operation', 'Locale', 'Units', 'Units out', 'Cost (USD)', 'Result']}>
                  {events.map((ev) => (
                    <tr key={ev.id}>
                      <td style={opsTd}>{formatDateTime(ev.occurredAt)}</td>
                      <td style={opsTd}>{ev.projectSlug}</td>
                      <td style={opsTd}>{ev.meter}</td>
                      <td style={opsTd}>{ev.operation}</td>
                      <td style={opsTd}>{ev.localeCode || '—'}</td>
                      <td style={opsTd}>{formatUnits(ev.units)}</td>
                      <td style={opsTd}>{formatUnits(ev.unitsOut)}</td>
                      <td style={opsTd}>{formatCost(ev.costUsd)}</td>
                      <td style={opsTd}>{ev.cacheHit ? 'Cache hit' : ev.succeeded ? 'OK' : 'Failed'}</td>
                    </tr>
                  ))}
                </OpsTable>
              )}
            </Section>
          </>
        )}
      </div>
    </div>
  );
}
