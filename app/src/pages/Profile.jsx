import { User, GitBranch, Award, Terminal, Cpu, ShieldCheck, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Profile() {
  const highlightSkills = [
    {
      icon: Cpu,
      title: 'Agentic AI & Systems',
      description: 'Structured LLM triage, hybrid model routing, eval pipelines, and multi-agent orchestration.'
    },
    {
      icon: Terminal,
      title: '7+ Years Core Engineering',
      description: 'Deep root-cause analysis, runtime troubleshooting under Unity, and operational excellence.'
    },
    {
      icon: Zap,
      title: 'ML & Computer Vision',
      description: 'Pioneered CNN defect detection pipelines for automated supply-chain video processing in 2018.'
    },
    {
      icon: ShieldCheck,
      title: 'Production Guardrails',
      description: 'Human-in-the-loop validation, strict output constraints, and reliable AI system integration.'
    }
  ];

  return (
    <div className="mt-md" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      {/* Hero Section / Profile Card */}
      <div className="glass-panel text-center" style={{ padding: 'var(--space-3xl)' }}>
        {/* Avatar */}
        <div
          className="glow-effect"
          style={{
            width: '140px',
            height: '140px',
            borderRadius: '50%',
            margin: '0 auto var(--space-xl)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-tertiary)',
            border: '2px solid var(--accent-cyan)',
          }}
        >
          <User size={64} style={{ color: 'var(--accent-cyan)' }} />
        </div>

        {/* Name & Subtitle */}
        <h1 className="gradient-text" style={{ marginBottom: 'var(--space-xs)' }}>
          Raghuram Balaji
        </h1>
        <h3 className="mb-md" style={{ color: 'var(--accent-cyan)' }}>
          AI Architect Candidate
        </h3>

        {/* Professional Summary */}
        <p
          style={{
            fontSize: '1.1rem',
            lineHeight: '1.8',
            color: 'var(--text-secondary)',
            maxWidth: '800px',
            margin: '0 auto var(--space-xl)',
          }}
        >
          I've spent seven years doing root-cause analysis on the runtime under Unity—the operational excellence half of this role is my day job. In 2018 I built ML-based automation before it was fashionable: a video pipeline feeding a CNN for defect detection inside a supply-chain automation platform. This year I rebuilt my two most relevant systems with the 2026 AI layer—structured LLM ticket triage with guardrails, an eval pipeline, human-in-the-loop review, and hybrid local/cloud model routing.
        </p>

        {/* Action Buttons */}
        <div
          style={{
            display: 'flex',
            gap: 'var(--space-lg)',
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
            style={{ display: 'inline-flex' }}
          >
            <GitBranch size={18} />
            View GitHub
          </a>

          <Link
            to="/certifications"
            className="btn btn-primary"
            style={{ display: 'inline-flex' }}
          >
            <Award size={18} />
            View Certifications
          </Link>
        </div>
      </div>

      {/* Technical Highlights Section */}
      <section className="mt-xl">
        <h2 className="mb-lg text-center gradient-text-alt" style={{ fontSize: '1.75rem' }}>
          Core Architectural Pillars
        </h2>
        <div className="grid grid-2">
          {highlightSkills.map((skill, index) => {
            const IconComponent = skill.icon;
            return (
              <div
                key={index}
                className="glass-panel"
                style={{
                  display: 'flex',
                  gap: 'var(--space-md)',
                  alignItems: 'flex-start',
                }}
              >
                <div
                  style={{
                    padding: 'var(--space-md)',
                    borderRadius: 'var(--radius-md)',
                    background: 'rgba(0, 240, 255, 0.05)',
                    border: '1px solid var(--border-accent)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <IconComponent size={28} style={{ color: 'var(--accent-cyan)' }} />
                </div>
                <div>
                  <h4 style={{ marginBottom: 'var(--space-xs)', color: 'var(--text-primary)' }}>
                    {skill.title}
                  </h4>
                  <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                    {skill.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
