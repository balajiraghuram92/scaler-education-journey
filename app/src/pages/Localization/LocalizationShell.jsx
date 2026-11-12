import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import { api } from '../../api/client';
import ProviderHealthPanel from '../../components/Localization/ProviderHealthPanel';
import useLocalizationProject from './useLocalizationProject';
import { useOptionalAuth } from '../../context/AuthContext';

export default function LocalizationShell({ activeTab = 'strings', children }) {
  const navigate = useNavigate();
  // Same role source ProtectedRoute uses (AuthContext isAdmin, i.e. user.role === 'Admin'),
  // via the optional hook since these pages also render for signed-out API-key users.
  const { isAdmin } = useOptionalAuth();
  const { slug: selectedProjectSlug, project, projects, loading: projectsLoading, selectProject } = useLocalizationProject();
  const [healthData, setHealthData] = useState([]);
  const [isHealthPanelOpen, setIsHealthPanelOpen] = useState(false);

  const fetchHealth = useCallback(async () => {
    try {
      const data = await api.localization.getProviderHealth();
      if (Array.isArray(data)) {
        setHealthData(data);
      }
    } catch {
      // Non-blocking telemetry fallback
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  // Determine aggregate health dot color
  const hasOpenCircuit = healthData.some(p => p.circuitState?.toLowerCase() === 'open');
  const hasHalfOpen = healthData.some(p => p.circuitState?.toLowerCase() === 'halfopen');
  const healthDotColor = hasOpenCircuit ? '#DC2626' : hasHalfOpen ? '#A6772C' : 'var(--color-sage, #2C5E55)';
  const healthTooltip = hasOpenCircuit
    ? 'Provider Alert: Downstream circuit open'
    : hasHalfOpen
    ? 'Provider Warning: Circuit degraded'
    : 'All Translation Providers Operational';

  const tabs = [
    { id: 'strings', label: 'Strings', path: '/lab-projects/localization' },
    { id: 'workflow', label: 'Workflow', path: '/lab-projects/localization/workflow' },
    { id: 'snapshots', label: 'Snapshots', path: '/lab-projects/localization/snapshots' },
    { id: 'jobs', label: 'Jobs', path: '/lab-projects/localization/jobs' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 7.1 Dedicated Nav Cluster */}
      <nav
        style={{
          borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
          backgroundColor: 'var(--color-parchment, #F8F6F0)',
          padding: '0.75rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 100
        }}
      >
        {/* Left: Feature label only — global site logo already renders in the page's <Layout> above this bar */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--color-sage, #2C5E55)' }}>
            Localization Engineering Lab
          </span>
        </div>

        {/* Right: Health icon + Project selector + Live indicator + Vendor portal link + Avatar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          {/* (a) Provider Health Indicator Button */}
          <button
            type="button"
            onClick={() => setIsHealthPanelOpen(true)}
            title={healthTooltip}
            style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              backgroundColor: '#FFFFFF',
              border: '1px solid var(--color-border-subtle, #E2DDD5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              padding: 0
            }}
          >
            <span
              style={{
                width: '9px',
                height: '9px',
                borderRadius: '50%',
                backgroundColor: healthDotColor,
                display: 'inline-block'
              }}
            />
          </button>

          {/* (b) Project select dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label htmlFor="project-select" style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)', fontWeight: '500' }}>
              Project:
            </label>
            <select
              id="project-select"
              value={selectedProjectSlug || ''}
              onChange={(e) => selectProject(e.target.value)}
              style={{
                padding: '0.35rem 0.65rem',
                borderRadius: '6px',
                border: '1px solid var(--color-border-subtle, #E2DDD5)',
                backgroundColor: '#FFFFFF',
                color: 'var(--color-ink, #1F2937)',
                fontSize: '0.85rem',
                fontWeight: '600',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {projects.length > 0 ? (
                projects.map((p) => (
                  <option key={p.slug} value={p.slug}>
                    {p.name}
                  </option>
                ))
              ) : (
                <option value="" disabled>{projectsLoading ? 'Loading projects…' : 'No projects'}</option>
              )}
            </select>
          </div>

          {/* (c) Live / Fallback Indicator */}
          <div
            title="Live Cloud Translation Services Active"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.8rem',
              color: 'var(--color-ink, #1F2937)',
              fontWeight: '600',
              backgroundColor: '#FFFFFF',
              border: '1px solid var(--color-border-subtle, #E2DDD5)',
              borderRadius: '20px',
              padding: '0.35rem 0.75rem'
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: 'var(--color-sage, #2C5E55)',
                display: 'inline-block'
              }}
            />
            <span>Live</span>
          </div>

          {/* Direct Vendor Portal shortcut */}
          <Link
            to="/lab-projects/localization/vendor"
            title="Open Standalone Vendor Translation Portal"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.8rem',
              color: 'var(--color-sage, #2C5E55)',
              textDecoration: 'none',
              fontWeight: '600',
              padding: '0.35rem 0.65rem',
              border: '1px dashed var(--color-sage, #2C5E55)',
              borderRadius: '6px'
            }}
          >
            <span>Vendor Portal</span>
            <ExternalLink size={12} />
          </Link>

          {/* Operations shortcut, visible to admins only */}
          {isAdmin && (
            <Link
              to="/lab-projects/localization/ops"
              title="Open Localization Operations (Admin)"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.8rem',
                color: 'var(--color-sage, #2C5E55)',
                textDecoration: 'none',
                fontWeight: '600',
                padding: '0.35rem 0.65rem',
                border: '1px dashed var(--color-sage, #2C5E55)',
                borderRadius: '6px'
              }}
            >
              <span>Operations</span>
              <ExternalLink size={12} />
            </Link>
          )}
        </div>
      </nav>

      {/* Main Page Header & Breadcrumb */}
      <div
        style={{
          padding: '1.5rem 2rem 0.5rem 2rem',
          maxWidth: '1380px',
          width: '100%',
          margin: '0 auto',
          boxSizing: 'border-box'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-sage, #2C5E55)', fontWeight: '700' }}>
              Production Project: {selectedProjectSlug || '…'}
            </div>
            <h1
              style={{
                margin: '0.25rem 0 0 0',
                fontSize: '1.85rem',
                fontFamily: 'var(--font-serif, "Newsreader", serif)',
                color: 'var(--color-ink, #1F2937)',
                letterSpacing: '-0.02em'
              }}
            >
              {project ? project.name : '…'}
            </h1>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.9rem', color: 'var(--color-ink-muted, #6B7280)' }}>
              Source: {project ? project.sourceLocale : '…'} • {project ? `${project.locales.length} Locale${project.locales.length === 1 ? '' : 's'}` : '…'} • Build-Locked Delivery Pipeline
            </p>
          </div>
        </div>

        {/* 7.2 Tab Bar */}
        <div
          style={{
            display: 'flex',
            gap: '2rem',
            borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
            marginBottom: '1.5rem'
          }}
        >
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => navigate(selectedProjectSlug ? `${tab.path}?project=${encodeURIComponent(selectedProjectSlug)}` : tab.path)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: '0.75rem 0',
                  cursor: 'pointer',
                  fontSize: '0.95rem',
                  fontFamily: 'var(--font-serif, "Newsreader", serif)',
                  fontWeight: isActive ? '700' : '500',
                  color: isActive ? 'var(--color-ink, #1F2937)' : 'var(--color-ink-muted, #6B7280)',
                  position: 'relative',
                  display: 'inline-flex',
                  alignItems: 'center'
                }}
              >
                <span
                  style={{
                    display: 'inline-block',
                    borderBottom: isActive ? '2px solid var(--color-sage, #2C5E55)' : '2px solid transparent',
                    paddingBottom: '0.75rem',
                    marginBottom: '-1px'
                  }}
                >
                  {tab.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Content Area */}
      <main
        style={{
          maxWidth: '1380px',
          width: '100%',
          margin: '0 auto',
          padding: '0 2rem 3rem 2rem',
          flex: 1,
          boxSizing: 'border-box'
        }}
      >
        {children}
      </main>

      {/* Provider Health Slide-out Drawer */}
      <ProviderHealthPanel
        isOpen={isHealthPanelOpen}
        onClose={() => setIsHealthPanelOpen(false)}
        healthData={healthData}
        onRefresh={fetchHealth}
      />
    </div>
  );
}
