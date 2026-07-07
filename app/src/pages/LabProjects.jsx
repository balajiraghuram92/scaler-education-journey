import React from 'react';
import { Rocket, Server, Layout as LayoutIcon, Briefcase, ChevronRight, Activity } from 'lucide-react';

export default function LabProjects() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '70vh',
        textAlign: 'center',
        animation: 'fadeIn 0.8s ease-out',
        padding: 'var(--space-xl) var(--space-md)',
      }}
    >
      <div 
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 'var(--space-sm)',
          padding: 'var(--space-sm) var(--space-md)',
          background: 'rgba(56, 189, 248, 0.1)',
          border: '1px solid rgba(56, 189, 248, 0.2)',
          borderRadius: '999px',
          color: 'var(--accent-cyan)',
          fontWeight: 600,
          fontSize: '0.875rem',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          marginBottom: 'var(--space-xl)',
        }}
      >
        <Activity size={16} />
        <span>In Development</span>
      </div>

      <h1 className="gradient-text" style={{ fontSize: '4rem', marginBottom: 'var(--space-md)', lineHeight: 1.1 }}>
        Lab Projects
      </h1>
      
      <p style={{ 
        color: 'var(--text-secondary)', 
        fontSize: '1.25rem', 
        maxWidth: '600px', 
        margin: '0 auto var(--space-2xl)',
        lineHeight: 1.6 
      }}>
        Crafting next-generation applications. A showcase of architectural excellence using <strong style={{ color: 'var(--text-primary)' }}>React Frontend</strong> and <strong style={{ color: 'var(--text-primary)' }}>.NET Backend</strong>.
      </p>

      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 'var(--space-lg)',
          width: '100%',
          maxWidth: '800px',
        }}
      >
        {/* Project 1 Card */}
        <div 
          className="glass-panel"
          style={{
            padding: 'var(--space-xl)',
            textAlign: 'left',
            position: 'relative',
            overflow: 'hidden',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            cursor: 'default'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)';
            e.currentTarget.style.boxShadow = '0 10px 30px -10px rgba(56, 189, 248, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <div style={{
            position: 'absolute',
            top: '-20px',
            right: '-20px',
            opacity: 0.05,
            transform: 'rotate(15deg)'
          }}>
            <Briefcase size={120} />
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
            <div style={{ padding: 'var(--space-xs)', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '8px', color: 'var(--accent-cyan)' }}>
              <Server size={24} />
            </div>
            <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text-primary)' }}>Cloud SaaS Localization</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)', lineHeight: 1.5 }}>
            Automating enterprise translation lifecycles with an event-driven architecture, bridging client-side extraction with a distributed .NET Core backend and a React-powered dashboard.
          </p>
          <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
            <span style={{ fontSize: '0.75rem', padding: '4px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>.NET Core</span>
            <span style={{ fontSize: '0.75rem', padding: '4px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>React</span>
          </div>
        </div>

        {/* Project 2 Card */}
        <div 
          className="glass-panel"
          style={{
            padding: 'var(--space-xl)',
            textAlign: 'left',
            position: 'relative',
            overflow: 'hidden',
            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            cursor: 'default'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-5px)';
            e.currentTarget.style.boxShadow = '0 10px 30px -10px rgba(168, 85, 247, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <div style={{
            position: 'absolute',
            top: '-20px',
            right: '-20px',
            opacity: 0.05,
            transform: 'rotate(-15deg)'
          }}>
            <LayoutIcon size={120} />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
            <div style={{ padding: 'var(--space-xs)', background: 'rgba(168, 85, 247, 0.1)', borderRadius: '8px', color: 'var(--accent-purple)' }}>
              <Rocket size={24} />
            </div>
            <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text-primary)' }}>Smart Factory WMS</h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-lg)', lineHeight: 1.5 }}>
            A real-time WebRTC enabled Warehouse Management System (WMS) with predictive inventory algorithms to track shipments, calculate assembly capacities, and automate restocking.
          </p>
          <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
            <span style={{ fontSize: '0.75rem', padding: '4px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>WebRTC</span>
            <span style={{ fontSize: '0.75rem', padding: '4px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>.NET Core</span>
          </div>
        </div>
      </div>
      
      <div style={{ marginTop: 'var(--space-2xl)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-sm)' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Coming soon to</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', color: 'var(--text-primary)' }}>
          <ChevronRight size={16} /> <span>github.com/raghuram-balaji</span>
        </div>
      </div>
    </div>
  );
}
