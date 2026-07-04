import { User, GitBranch, Award, Terminal, Cpu, ShieldCheck, Zap, Cloud, CheckCircle2, Sparkles } from 'lucide-react';

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

  const azureCertifications = [
    {
      code: 'AI-103',
      title: 'Azure AI Apps and Agents Developer',
      status: 'Target Timeline: 2026',
      badge: 'Agentic AI & OpenAI',
      icon: Sparkles,
      description: 'Specialized credentials for architecting generative AI solutions, autonomous agent orchestration, custom tooling integration, and RAG systems on Microsoft Azure.',
      highlights: [
        'Azure OpenAI Service & Model Routing',
        'Semantic Kernel & AI Agent Workflows',
        'Vector Search & Knowledge Indexing'
      ]
    },
    {
      code: 'AI-200',
      title: 'Azure AI Cloud Developer',
      status: 'Target Timeline: 2026',
      badge: 'Cloud Architecture',
      icon: Cloud,
      description: 'Enterprise credentials focusing on end-to-end cloud-native AI engineering, scalable microservice integration, automated CI/CD pipelines, and secure data processing.',
      highlights: [
        'Azure App Service & Container Apps',
        'Enterprise Security & Guardrails',
        'Scalable API & Microservices'
      ]
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

          <a
            href="#azure-certifications"
            className="btn btn-primary"
            style={{ display: 'inline-flex' }}
          >
            <Award size={18} />
            Azure Certifications
          </a>
        </div>
      </div>

      {/* Azure Certifications Section */}
      <section id="azure-certifications" className="mt-xl">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-lg)' }}>
          <Award size={28} style={{ color: 'var(--accent-cyan)' }} />
          <h2 className="gradient-text" style={{ fontSize: '1.75rem', margin: 0 }}>
            Azure Certifications & Cloud Credentials
          </h2>
        </div>
        <div className="grid grid-2">
          {azureCertifications.map((cert, index) => {
            const CertIcon = cert.icon;
            return (
              <div
                key={index}
                className="glass-panel"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--space-md)',
                  position: 'relative',
                  borderLeft: '4px solid var(--accent-cyan)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <div
                      style={{
                        padding: 'var(--space-xs) var(--space-sm)',
                        borderRadius: 'var(--radius-sm)',
                        background: 'rgba(0, 240, 255, 0.1)',
                        border: '1px solid var(--border-accent)',
                        color: 'var(--accent-cyan)',
                        fontWeight: '700',
                        fontSize: '0.85rem',
                      }}
                    >
                      {cert.code}
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{cert.badge}</span>
                  </div>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      padding: '0.2rem 0.6rem',
                      borderRadius: 'var(--radius-full)',
                      background: 'rgba(123, 47, 247, 0.15)',
                      border: '1px solid rgba(123, 47, 247, 0.4)',
                      color: 'var(--accent-purple)',
                      fontWeight: '600',
                    }}
                  >
                    {cert.status}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center' }}>
                  <div
                    style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: 'var(--radius-md)',
                      background: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-accent)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <CertIcon size={24} style={{ color: 'var(--accent-cyan)' }} />
                  </div>
                  <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', margin: 0, lineHeight: 1.3 }}>
                    {cert.title}
                  </h3>
                </div>

                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: '1.6', flex: 1 }}>
                  {cert.description}
                </p>

                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 'var(--space-sm)', marginTop: 'auto' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 'var(--space-xs)', fontWeight: '600' }}>
                    KEY COMPETENCIES
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {cert.highlights.map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <CheckCircle2 size={14} style={{ color: 'var(--accent-emerald)', flexShrink: 0 }} />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

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

