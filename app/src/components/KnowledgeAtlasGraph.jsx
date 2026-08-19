import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import ConceptDetailPopover from './ConceptDetailPopover';
import './KnowledgeAtlasGraph.css';

// Short domain names matching Home-page.png
const DOMAIN_DISPLAY_MAP = {
  'agentic-ai': 'Agentic AI',
  'foundations': 'Foundations',
  'backend': 'Backend',
  'full-stack': 'Full Stack',
  'cloud': 'Cloud',
  'enterprise': 'Enterprise',
  'agent-systems': 'Agent Systems',
  'reliability': 'Reliability'
};

// 8 Canonical Domains in exact order
export const CANONICAL_DOMAINS = [
  { id: 'agentic-ai', label: 'Agentic AI' },
  { id: 'foundations', label: 'Foundations' },
  { id: 'backend', label: 'Backend' },
  { id: 'full-stack', label: 'Full Stack' },
  { id: 'cloud', label: 'Cloud' },
  { id: 'enterprise', label: 'Enterprise' },
  { id: 'agent-systems', label: 'Agent Systems' },
  { id: 'reliability', label: 'Reliability' }
];
export const DEFAULT_DOMAINS = CANONICAL_DOMAINS;

// 8 Canonical Concepts matching Home-page.png exactly
export const CANONICAL_CONCEPTS = [
  {
    id: 'rag',
    title: 'RAG',
    subLabel: 'RAG\nFoundation',
    popoverTitle: 'Retrieval-Augmented Generation (RAG)',
    connectedDomains: ['agentic-ai', 'foundations', 'agent-systems', 'enterprise'],
    prerequisites: [
      { name: 'Vector Embeddings', status: 'included' },
      { name: 'Chunking Strategies', status: 'included' }
    ],
    relatedLessons: ['Hybrid Search & BM25', 'RAGAS Evaluation Framework'],
    nextLessons: ['Production Vector DBs', 'Model Routing & Caching']
  },
  {
    id: 'apis',
    title: 'APIs',
    subLabel: 'APIs\nDatabases\nConcurreum',
    popoverTitle: 'API Design & Protocols',
    connectedDomains: ['backend', 'full-stack', 'enterprise', 'agent-systems'],
    prerequisites: [
      { name: 'HTTP & REST Protocols', status: 'included' },
      { name: 'FastAPI / ASP.NET', status: 'included' }
    ],
    relatedLessons: ['Streaming SSE & WebSockets', 'Idempotency & Rate Limiting'],
    nextLessons: ['API Gateway Architecture', 'Model Context Protocol (MCP)']
  },
  {
    id: 'databases',
    title: 'Databases',
    subLabel: 'Databases,\nConcurrency',
    popoverTitle: 'Advanced Databases & Storage',
    connectedDomains: ['foundations', 'backend', 'enterprise', 'reliability'],
    prerequisites: [
      { name: 'Relational Schema & ACID', status: 'included' },
      { name: 'PostgreSQL Internals', status: 'included' }
    ],
    relatedLessons: ['EXPLAIN ANALYZE & Indexing', 'pgvector HNSW Search'],
    nextLessons: ['PostgreSQL RLS Multi-Tenancy', 'Database Partitioning']
  },
  {
    id: 'concurrency',
    title: 'Concurrency',
    subLabel: 'Java Concurrency',
    popoverTitle: 'Java Concurrency',
    connectedDomains: ['foundations', 'backend', 'reliability'],
    prerequisites: [
      { name: 'Java Concurrency', status: 'included' }
    ],
    relatedLessons: [
      'Java Concurrency',
      'Structured Concurrency'
    ],
    nextLessons: [
      'Java Concurrency',
      'Next Security'
    ]
  },
  {
    id: 'networking',
    title: 'Networking',
    subLabel: '',
    popoverTitle: 'Cloud & Container Networking',
    connectedDomains: ['foundations', 'cloud', 'reliability'],
    prerequisites: [
      { name: 'TCP/IP & OSI Stack', status: 'included' },
      { name: 'DNS & TLS Termination', status: 'included' }
    ],
    relatedLessons: ['AWS VPC & NAT Gateways', 'Kubernetes Ingress Controllers'],
    nextLessons: ['Service Mesh Architecture', 'Zero Trust Network Overlays']
  },
  {
    id: 'caching',
    title: 'Caching',
    subLabel: 'Anching\nProcessing',
    popoverTitle: 'Distributed Caching & Streams',
    connectedDomains: ['backend', 'full-stack', 'enterprise'],
    prerequisites: [
      { name: 'In-Memory Key-Value Stores', status: 'included' },
      { name: 'Redis Core Structures', status: 'included' }
    ],
    relatedLessons: ['Cache Invalidation Strategies', 'Redis Streams & Pub/Sub'],
    nextLessons: ['Semantic Prompt Caching', 'Distributed Lock Mitigation']
  },
  {
    id: 'observability',
    title: 'Observability',
    subLabel: 'Observability',
    popoverTitle: 'Telemetry & Distributed Tracing',
    connectedDomains: ['cloud', 'enterprise', 'reliability'],
    prerequisites: [
      { name: 'Structured JSON Logging', status: 'included' },
      { name: 'Prometheus Metric Types', status: 'included' }
    ],
    relatedLessons: ['OpenTelemetry Instrumentation', 'Grafana SRE Dashboards'],
    nextLessons: ['W3C Trace Context', 'SLO & Error Budget Alerting']
  },
  {
    id: 'security',
    title: 'Security',
    subLabel: 'Security',
    popoverTitle: 'Enterprise Security & Compliance',
    connectedDomains: ['backend', 'cloud', 'enterprise', 'reliability'],
    prerequisites: [
      { name: 'OAuth2 & JWT Signing', status: 'included' },
      { name: 'PKI & Secrets Management', status: 'included' }
    ],
    relatedLessons: ['Fail-Closed API Security', 'AWS KMS Encryption'],
    nextLessons: ['Prompt Injection Defense', 'SOC2 / GDPR Controls']
  }
];

// Rich Synaptic Connection Mesh connecting domains to concepts
export const CANONICAL_CONNECTIONS = [
  // Agentic AI connections
  { from: 'agentic-ai', to: 'rag' },
  { from: 'agentic-ai', to: 'apis' },
  { from: 'agentic-ai', to: 'caching' },
  // Foundations connections
  { from: 'foundations', to: 'rag' },
  { from: 'foundations', to: 'apis' },
  { from: 'foundations', to: 'databases' },
  { from: 'foundations', to: 'concurrency' },
  { from: 'foundations', to: 'networking' },
  // Backend connections
  { from: 'backend', to: 'apis' },
  { from: 'backend', to: 'databases' },
  { from: 'backend', to: 'concurrency' },
  { from: 'backend', to: 'caching' },
  { from: 'backend', to: 'security' },
  // Full Stack connections
  { from: 'full-stack', to: 'apis' },
  { from: 'full-stack', to: 'databases' },
  { from: 'full-stack', to: 'caching' },
  { from: 'full-stack', to: 'observability' },
  // Cloud connections
  { from: 'cloud', to: 'networking' },
  { from: 'cloud', to: 'caching' },
  { from: 'cloud', to: 'observability' },
  { from: 'cloud', to: 'security' },
  // Enterprise connections
  { from: 'enterprise', to: 'rag' },
  { from: 'enterprise', to: 'databases' },
  { from: 'enterprise', to: 'caching' },
  { from: 'enterprise', to: 'observability' },
  { from: 'enterprise', to: 'security' },
  // Agent Systems connections
  { from: 'agent-systems', to: 'rag' },
  { from: 'agent-systems', to: 'apis' },
  { from: 'agent-systems', to: 'concurrency' },
  { from: 'agent-systems', to: 'security' },
  // Reliability connections
  { from: 'reliability', to: 'databases' },
  { from: 'reliability', to: 'concurrency' },
  { from: 'reliability', to: 'networking' },
  { from: 'reliability', to: 'observability' },
  { from: 'reliability', to: 'security' }
];
export const DEFAULT_CONCEPTS = CANONICAL_CONCEPTS;
export const DEFAULT_CONNECTIONS = CANONICAL_CONNECTIONS;

export default function KnowledgeAtlasGraph({
  domains = CANONICAL_DOMAINS,
  concepts = CANONICAL_CONCEPTS,
  connections = CANONICAL_CONNECTIONS
}) {
  const containerRef = useRef(null);
  const domainRefs = useRef(new Map());
  const conceptRefs = useRef(new Map());

  // Concurrency is selected by default as in Home-page.png
  const [selectedConceptId, setSelectedConceptId] = useState('concurrency');
  const [selectedDomainId, setSelectedDomainId] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [coords, setCoords] = useState({ domains: {}, concepts: {} });

  // Format domains with concise display labels to prevent overlap
  const formattedDomains = useMemo(() => {
    return CANONICAL_DOMAINS.map(d => {
      const live = domains.find(x => x.id === d.id || x.slug === d.id);
      return {
        id: d.id,
        label: DOMAIN_DISPLAY_MAP[d.id] || live?.label || live?.name || d.label
      };
    });
  }, [domains]);

  // Format concepts merging live data with canonical layout
  const formattedConcepts = useMemo(() => {
    return CANONICAL_CONCEPTS.map(c => {
      const live = concepts.find(x => x.id === c.id || x.slug === c.id);
      return {
        ...c,
        title: live?.title || c.title,
        popoverTitle: live?.title === 'Concurrency' ? 'Java Concurrency' : (live?.title || c.popoverTitle),
        prerequisites: live?.prerequisites?.length > 0 ? live.prerequisites : c.prerequisites,
        relatedLessons: live?.relatedLessons?.length > 0 ? live.relatedLessons : c.relatedLessons,
        nextLessons: live?.nextLessons?.length > 0 ? live.nextLessons : c.nextLessons
      };
    });
  }, [concepts]);

  // Adjacency Lookups
  const adjacency = useMemo(() => {
    const domainToConcepts = new Map();
    const conceptToDomains = new Map();
    const edgeSet = new Set();

    connections.forEach(({ from, to }) => {
      if (!domainToConcepts.has(from)) domainToConcepts.set(from, new Set());
      if (!conceptToDomains.has(to)) conceptToDomains.set(to, new Set());
      domainToConcepts.get(from).add(to);
      conceptToDomains.get(to).add(from);
      edgeSet.add(`${from}->${to}`);
    });

    return { domainToConcepts, conceptToDomains, edgeSet };
  }, [connections]);

  // Accurate coordinate calculation from DOM nodes
  const recalculateCoordinates = useCallback(() => {
    if (!containerRef.current) return;
    const containerRect = containerRef.current.getBoundingClientRect();

    const domainCoords = {};
    formattedDomains.forEach((d) => {
      const el = domainRefs.current.get(d.id);
      if (el) {
        const r = el.getBoundingClientRect();
        domainCoords[d.id] = {
          x: r.left - containerRect.left + r.width / 2,
          y: r.bottom - containerRect.top
        };
      }
    });

    const conceptCoords = {};
    formattedConcepts.forEach((c) => {
      const el = conceptRefs.current.get(c.id);
      if (el) {
        const r = el.getBoundingClientRect();
        conceptCoords[c.id] = {
          x: r.left - containerRect.left + r.width / 2,
          y: r.top - containerRect.top
        };
      }
    });

    setCoords({ domains: domainCoords, concepts: conceptCoords });
  }, [formattedDomains, formattedConcepts]);

  useEffect(() => {
    let animationFrameId;
    const handleResize = () => {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = requestAnimationFrame(recalculateCoordinates);
    };

    const ro = new ResizeObserver(handleResize);
    if (containerRef.current) {
      ro.observe(containerRef.current);
    }
    window.addEventListener('resize', handleResize);

    handleResize();
    const timer1 = setTimeout(handleResize, 50);
    const timer2 = setTimeout(handleResize, 200);

    return () => {
      ro.disconnect();
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [recalculateCoordinates]);

  // Focus hierarchy: Hover > Selected Concept > Selected Domain
  const activeFocus = useMemo(() => {
    if (hoveredNode) {
      return { type: hoveredNode.type, id: hoveredNode.id };
    }
    if (selectedConceptId) {
      return { type: 'concept', id: selectedConceptId };
    }
    if (selectedDomainId) {
      return { type: 'domain', id: selectedDomainId };
    }
    return null;
  }, [hoveredNode, selectedConceptId, selectedDomainId]);

  const isEdgeHighlighted = useCallback(
    (from, to) => {
      if (!activeFocus) return false;
      if (activeFocus.type === 'domain') return activeFocus.id === from;
      if (activeFocus.type === 'concept') return activeFocus.id === to;
      return false;
    },
    [activeFocus]
  );

  const selectedConcept = useMemo(
    () => formattedConcepts.find((c) => c.id === selectedConceptId),
    [formattedConcepts, selectedConceptId]
  );

  return (
    <div className="knowledge-atlas-graph-container" ref={containerRef}>
      {/* Dynamic SVG Synaptic Bezier Mesh */}
      <svg className="atlas-synaptic-svg">
        <defs>
          <linearGradient id="synapse-active-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2C5E55" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#2C5E55" stopOpacity="0.95" />
          </linearGradient>
        </defs>

        {connections.map(({ from, to }) => {
          const p1 = coords.domains[from];
          const p2 = coords.concepts[to];
          if (!p1 || !p2) return null;

          const highlighted = isEdgeHighlighted(from, to);

          // Symmetric Cubic Bezier S-Curve with pure vertical tangents
          const deltaY = p2.y - p1.y;
          const cp1Y = p1.y + deltaY * 0.5;
          const cp2Y = p2.y - deltaY * 0.5;
          const pathD = `M ${p1.x.toFixed(2)} ${p1.y.toFixed(2)} C ${p1.x.toFixed(2)} ${cp1Y.toFixed(2)}, ${p2.x.toFixed(2)} ${cp2Y.toFixed(2)}, ${p2.x.toFixed(2)} ${p2.y.toFixed(2)}`;

          return (
            <path
              key={`${from}->${to}`}
              d={pathD}
              fill="none"
              stroke={highlighted ? '#2C5E55' : '#D6D0C5'}
              strokeWidth={highlighted ? '2' : '1'}
              className={`synapse-line ${highlighted ? 'synapse-line-active' : 'synapse-line-passive'}`}
            />
          );
        })}
      </svg>

      {/* Top Layer: 8 Domain Pills in strict 8-column grid */}
      <div className="atlas-domains-grid">
        {formattedDomains.map((domain) => {
          const isSelected = selectedDomainId === domain.id;

          return (
            <button
              key={domain.id}
              ref={(el) => domainRefs.current.set(domain.id, el)}
              type="button"
              className={`domain-pill-btn ${isSelected ? 'is-selected' : ''}`}
              onClick={() => {
                setSelectedDomainId((prev) => (prev === domain.id ? null : domain.id));
              }}
              onMouseEnter={() => setHoveredNode({ type: 'domain', id: domain.id })}
              onMouseLeave={() => setHoveredNode(null)}
            >
              <span className="domain-pill-text">{domain.label}</span>
            </button>
          );
        })}
      </div>

      {/* Synaptic Gap (where bezier lines mesh across) */}
      <div className="atlas-synaptic-spacer" />

      {/* Bottom Layer: 8 Concept Cards in matching 8-column grid */}
      <div className="atlas-concepts-grid">
        {formattedConcepts.map((concept) => {
          const isSelected = selectedConceptId === concept.id;

          return (
            <div
              key={concept.id}
              ref={(el) => conceptRefs.current.set(concept.id, el)}
              className="concept-column-wrapper"
            >
              <button
                type="button"
                className={`concept-pill-btn ${isSelected ? 'is-selected' : ''}`}
                onClick={() => {
                  setSelectedConceptId((prev) => (prev === concept.id ? null : concept.id));
                }}
                onMouseEnter={() => setHoveredNode({ type: 'concept', id: concept.id })}
                onMouseLeave={() => setHoveredNode(null)}
              >
                <span className="concept-pill-title">{concept.title}</span>
              </button>

              {/* Serif Sub-label */}
              {concept.subLabel ? (
                <div className="concept-sublabel">
                  {concept.subLabel.split('\n').map((line, idx) => (
                    <span key={idx} className="sublabel-line">{line}</span>
                  ))}
                </div>
              ) : (
                <div className="concept-sublabel-empty" />
              )}

              {/* Anchored Popover directly below selected concept */}
              {isSelected && (
                <ConceptDetailPopover
                  concept={selectedConcept}
                  isOpen={isSelected}
                  onClose={() => setSelectedConceptId(null)}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
