import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import useSelectedVendor from './useSelectedVendor';

export default function VendorPortalShell({ children }) {
  const { roster, vendor, selectVendor, loading } = useSelectedVendor();

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-parchment, #F8F6F0)', display: 'flex', flexDirection: 'column' }}>
      {/* 8. Vendor Portal Header */}
      <header
        style={{
          borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
          backgroundColor: '#FFFFFF',
          padding: '0.75rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 100
        }}
      >
        {/* Left: Brand logo + Wordmark + VENDOR PORTAL tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link
            to="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              textDecoration: 'none',
              color: 'var(--color-ink, #1F2937)',
              fontWeight: '700',
              fontFamily: 'var(--font-serif, "Newsreader", serif)',
              fontSize: '1.1rem'
            }}
          >
            <img src="/favicon.svg" alt="Neuralascent Logo" style={{ width: '22px', height: '22px' }} />
            <span>Neuralascent</span>
          </Link>

          {/* VENDOR PORTAL tag: thin-bordered rectangle, sharp corners, small uppercase text */}
          <span
            style={{
              border: '1px solid var(--color-ink, #1F2937)',
              borderRadius: '0px',
              padding: '2px 8px',
              fontSize: '0.7rem',
              fontWeight: '700',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: 'var(--color-ink, #1F2937)',
              backgroundColor: 'transparent'
            }}
          >
            Vendor Portal
          </span>
        </div>

        {/* Right: Viewing as select + Return link */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label htmlFor="vendor-roster-select" style={{ fontSize: '0.8rem', color: 'var(--color-ink-muted, #6B7280)', fontWeight: '500' }}>
              Viewing as:
            </label>
            <select
              id="vendor-roster-select"
              value={vendor?.id || ''}
              onChange={(e) => {
                const id = parseInt(e.target.value, 10);
                if (!Number.isNaN(id)) selectVendor(id);
              }}
              style={{
                padding: '0.35rem 0.65rem',
                borderRadius: '0px',
                border: '1px solid var(--color-border-subtle, #E2DDD5)',
                backgroundColor: '#FFFFFF',
                color: 'var(--color-ink, #1F2937)',
                fontSize: '0.85rem',
                fontWeight: '600',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              {roster.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.languages}) ★{v.rating}
                </option>
              ))}
              {roster.length === 0 && (
                <option value="" disabled>{loading ? 'Loading…' : 'No vendors'}</option>
              )}
            </select>
          </div>

          <Link
            to="/lab-projects/localization"
            style={{
              fontSize: '0.8rem',
              color: 'var(--color-ink-muted, #6B7280)',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            title="Return to Owner View"
          >
            <ArrowLeft size={14} /> Owner App
          </Link>
        </div>
      </header>

      {/* Main Vendor Content */}
      <main
        style={{
          maxWidth: '1280px',
          width: '100%',
          margin: '0 auto',
          padding: '2rem',
          flex: 1,
          boxSizing: 'border-box'
        }}
      >
        {children}
      </main>
    </div>
  );
}
