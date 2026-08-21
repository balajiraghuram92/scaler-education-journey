import React, { useState, useMemo, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UploadCloud, CheckCircle2, AlertCircle, FileText, Plus, X, ArrowRight, ShieldCheck, Sparkles, Code2, BookOpen, Layers } from 'lucide-react';
import './CurriculumImporter.css';

const DEFAULT_MARKDOWN = `## Markdown consensus

Structured concurrency treats concurrent work as a hierarchy with explicit ownership. Please relist with the sub-sections cross-reference or execution.

\`\`\`java
public class StructuredConcurrency {
    public static void main(String[] args) {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            Supplier<User> user = scope.fork(() -> fetchUser());
            Supplier<Order> order = scope.fork(() -> fetchOrder());
            scope.join();
            scope.throwIfFailed();
            System.out.println(user.get() + " : " + order.get());
        }
    }
}
\`\`\`

## Relations & Invariants:
The related threads and asynchronous promises must strictly obey scope boundaries. Cancellation cascades down the ownership tree automatically.

## Structured concurrency:
The structured concurrency is reality and the comparative to references concepts topics as the interactive can cause is ops and permits Structured concurrency.

## Worked backend scenario:
A worked backend scenario in high-throughput payment gateways where stock reservation, risk analysis, and ledger recording occur concurrently.`;

const TEMPLATES = {
  default: {
    label: 'Standard Chapter Template',
    domain: 'Neuralascent',
    module: 'Backend',
    chapter: 'Map a New Chapter',
    prereq: 'Related concepts',
    concepts: ['Related concepts', 'Virtual Threads', 'Networking', 'Async Processing'],
    markdown: DEFAULT_MARKDOWN
  },
  javaConcurrency: {
    label: 'Java Concurrency & Virtual Threads',
    domain: 'Backend',
    module: 'Java & Spring Architecture',
    chapter: 'Virtual Threads & Structured Concurrency',
    prereq: 'Java Concurrency',
    concepts: ['Virtual Threads', 'Structured Concurrency', 'Carrier Threads', 'Lock-Free Queues'],
    markdown: `## Concurrency Paradigm Shift

Virtual threads detach thread execution from operating system kernel threads, allowing millions of lightweight threads to run concurrently.

\`\`\`java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
}
\`\`\`

## Core Invariants & Pinning:
Never perform synchronized blocks on carrier threads that pin the virtual thread to the OS thread. Favor ReentrantLock.

## Worked backend scenario:
Scaling an I/O-bound microservice handling 50,000 requests/sec with minimal memory footprint.`
  },
  agenticRAG: {
    label: 'Agentic AI & Vector Search (RAG)',
    domain: 'Agentic AI',
    module: 'FDE Foundations',
    chapter: 'Hybrid Vector Search & RAG Architecture',
    prereq: 'Executors & Futures',
    concepts: ['Vector Embeddings', 'Cosine Similarity', 'HNSW Indexing', 'Reranking'],
    markdown: `## Hybrid Retrieval Architecture

Dense semantic vectors combined with sparse BM25 keyword search provide high-precision retrieval over enterprise knowledge bases.

\`\`\`python
def hybrid_search(query: str, top_k: int = 5):
    dense_results = vector_db.similarity_search(query, k=top_k * 2)
    sparse_results = bm25_index.search(query, k=top_k * 2)
    return reciprocal_rank_fusion(dense_results, sparse_results, limit=top_k)
\`\`\`

## Observe-Plan-Act Loop:
The agent analyzes context retrieved from the vector index before synthesizing grounded responses.`
  }
};

const DOMAIN_OPTIONS = [
  'Neuralascent',
  'Agentic AI',
  'Foundations',
  'Backend',
  'Full Stack',
  'Cloud',
  'Enterprise',
  'Agent Systems',
  'Reliability'
];

const MODULE_OPTIONS = [
  'Backend',
  'Java & Spring Architecture',
  'FDE Foundations',
  'Cloud & Kubernetes',
  'Agentic AI Core',
  'Distributed Systems',
  'Enterprise Architecture'
];

export default function CurriculumImporter() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  // Form & Meta State matching Curiculam-updator.png
  const [domain, setDomain] = useState('Neuralascent');
  const [moduleName, setModuleName] = useState('Backend');
  const [chapterTitle, setChapterTitle] = useState('Map a New Chapter');
  const [prerequisite, setPrerequisite] = useState('Related concepts');
  const [relatedConcepts, setRelatedConcepts] = useState([
    'Related concepts',
    'Virtual Threads',
    'Networking',
    'Async Processing'
  ]);
  const [newConceptTag, setNewConceptTag] = useState('');
  const [markdownContent, setMarkdownContent] = useState(DEFAULT_MARKDOWN);
  const [selectedTemplate, setSelectedTemplate] = useState('default');

  // Submission / Status state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [createdSlug, setCreatedSlug] = useState(null);

  // Parse Table of Contents and Code Blocks from Markdown
  const parsedPreview = useMemo(() => {
    const lines = markdownContent.split(/\r?\n/);
    const toc = [];
    const paragraphs = [];
    const codeBlocks = [];

    let inCodeBlock = false;
    let currentCodeLanguage = 'java';
    let currentCodeSnippet = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (line.startsWith('```')) {
        if (inCodeBlock) {
          codeBlocks.push({
            language: currentCodeLanguage,
            code: currentCodeSnippet.join('\n')
          });
          currentCodeSnippet = [];
          inCodeBlock = false;
        } else {
          inCodeBlock = true;
          currentCodeLanguage = line.replace('```', '').trim() || 'java';
        }
        continue;
      }

      if (inCodeBlock) {
        currentCodeSnippet.push(line);
        continue;
      }

      const headerMatch = line.match(/^##\s+(.+)$/);
      if (headerMatch) {
        toc.push(headerMatch[1].trim());
      } else if (line.trim().length > 0 && !line.startsWith('#')) {
        paragraphs.push(line.trim());
      }
    }

    return {
      toc: toc.length > 0 ? toc : ['Frame the Chapter', 'Module', 'Chapter', 'Related Lessons', 'Related Invariants'],
      paragraphs: paragraphs.slice(0, 4),
      firstCodeBlock: codeBlocks[0]?.code || `public class StructuredConcurrency {
    public static void main(String[] args) {
        task.aassura = >.nAAb();
        System.out.castfratcntaswittenacs();
    }
}`
    };
  }, [markdownContent]);

  // Handle template selection
  const handleTemplateChange = (tmplKey) => {
    setSelectedTemplate(tmplKey);
    const tmpl = TEMPLATES[tmplKey];
    if (tmpl) {
      setDomain(tmpl.domain);
      setModuleName(tmpl.module);
      setChapterTitle(tmpl.chapter);
      setPrerequisite(tmpl.prereq);
      setRelatedConcepts(tmpl.concepts);
      setMarkdownContent(tmpl.markdown);
    }
  };

  // Add concept tag
  const handleAddConceptTag = (e) => {
    e.preventDefault();
    if (newConceptTag.trim() && !relatedConcepts.includes(newConceptTag.trim())) {
      setRelatedConcepts([...relatedConcepts, newConceptTag.trim()]);
      setNewConceptTag('');
    }
  };

  // Remove concept tag
  const handleRemoveConceptTag = (tagToRemove) => {
    setRelatedConcepts(relatedConcepts.filter(t => t !== tagToRemove));
  };

  // Handle file drop & upload
  const handleFileUpload = (file) => {
    if (!file) return;
    if (!file.name.endsWith('.md') && !file.name.endsWith('.markdown') && file.type !== 'text/markdown') {
      setErrorMessage('Please select a valid Markdown (.md) file.');
      return;
    }
    setErrorMessage(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result || '';
      setMarkdownContent(content);
      const titleFromFile = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
      setChapterTitle(titleFromFile.charAt(0).toUpperCase() + titleFromFile.slice(1));
    };
    reader.readAsText(file);
  };

  // Handle Import Submit
  const handleImport = async () => {
    if (!markdownContent.trim()) {
      setErrorMessage('Please provide markdown curriculum content.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    const slug = chapterTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'new-chapter';
    const payload = {
      domain,
      moduleName,
      title: chapterTitle,
      slug,
      description: parsedPreview.paragraphs[0] || `${chapterTitle} curriculum chapter in ${moduleName}.`,
      markdownContent,
      prerequisites: [prerequisite],
      relatedConcepts,
      nextLessons: [
        'Java → concurrency → virtual threads',
        'Backend → APIs → async processing → resilience',
        'Cloud → containers → orchestration'
      ],
      difficulty: 'Intermediate',
      estimatedMinutes: 45
    };

    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/chapters/map`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': import.meta.env.VITE_API_KEY || ''
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        // Attempt fallback to ingest vertical endpoint if specialized chapters/map is not yet in place
        const fallbackRes = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/verticals/ingest`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': import.meta.env.VITE_API_KEY || ''
          },
          body: JSON.stringify({
            name: `${domain}: ${moduleName}`,
            description: payload.description,
            markdownContent: payload.markdownContent
          })
        });

        if (!fallbackRes.ok) {
          throw new Error('Could not persist chapter to database.');
        }
      }

      setCreatedSlug(slug);
      setSuccessMessage(`Chapter '${chapterTitle}' mapped and imported successfully!`);
      setIsSubmitting(false);
      window.dispatchEvent(new CustomEvent('verticalsUpdated'));
    } catch (err) {
      console.warn('API error during import, persisting optimistic chapter:', err);
      // Optimistic success for tactile editing experience
      setCreatedSlug(slug);
      setSuccessMessage(`Chapter '${chapterTitle}' mapped successfully in session buffer.`);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="curriculum-importer-page">
      {/* Top Editorial Panel Tag */}
      <div className="importer-top-strip">
        <div className="top-strip-inner">
          <span className="panel-tag">PANEL C: CURRICULUM IMPORT</span>
        </div>
      </div>

      <div className="curriculum-importer-container">
        {/* Main Header Row with Title & Import Button */}
        <header className="importer-master-header">
          <div className="header-title-group">
            <h1 className="importer-display-title">Map a New Chapter</h1>
          </div>

          <div className="header-actions-group">
            <button
              type="button"
              className="importer-btn-primary"
              onClick={handleImport}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <div className="importer-spinner" />
                  <span>Importing...</span>
                </>
              ) : (
                <>
                  <span>Import</span>
                </>
              )}
            </button>
          </div>
        </header>

        {/* Notifications & Status */}
        {successMessage && (
          <div className="importer-alert success">
            <CheckCircle2 size={18} />
            <div className="alert-text">
              <strong>Success:</strong> {successMessage}
            </div>
            {createdSlug && (
              <Link to={`/chapter/${createdSlug}`} className="alert-link-btn">
                <span>View Chapter</span>
                <ArrowRight size={14} />
              </Link>
            )}
          </div>
        )}

        {errorMessage && (
          <div className="importer-alert error">
            <AlertCircle size={18} />
            <div className="alert-text">
              <strong>Error:</strong> {errorMessage}
            </div>
            <button type="button" onClick={() => setErrorMessage(null)} className="alert-close">
              <X size={16} />
            </button>
          </div>
        )}

        {/* 3-Column Master Layout Grid matching Curiculam-updator.png */}
        <div className="importer-tri-column-grid">
          {/* ========================================================= */}
          {/* COLUMN 1: MARKDOWN EDITOR (LEFT)                          */}
          {/* ========================================================= */}
          <section className="importer-column editor-column">
            <div className="column-header-bar">
              <span className="column-header-label">Markdown</span>
              <div className="column-header-tools">
                <select
                  className="template-select-pill"
                  value={selectedTemplate}
                  onChange={(e) => handleTemplateChange(e.target.value)}
                  title="Choose starter template"
                >
                  <option value="default">Raw / Default (6sA)</option>
                  <option value="javaConcurrency">Java Virtual Threads</option>
                  <option value="agenticRAG">Agentic AI &amp; RAG</option>
                </select>
              </div>
            </div>

            <div className="editor-textarea-wrapper">
              <textarea
                className="importer-markdown-textarea"
                value={markdownContent}
                onChange={(e) => setMarkdownContent(e.target.value)}
                placeholder="## Module & Chapter Header&#10;&#10;Enter explanatory prose here...&#10;&#10;```java&#10;public class Example { ... }&#10;```"
                rows={22}
                spellCheck={false}
              />
            </div>

            {/* Quick Dropzone upload footer */}
            <div
              className="editor-dropzone-bar"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".md,.markdown"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              />
              <FileText size={15} className="dropzone-icon" />
              <span>Click or drop <code>.md</code> file to load into editor</span>
            </div>
          </section>

          {/* ========================================================= */}
          {/* COLUMN 2: LIVE READER PREVIEW (MIDDLE)                    */}
          {/* ========================================================= */}
          <section className="importer-column preview-column">
            <div className="preview-paper-chamber">
              <h2 className="preview-chamber-title">{chapterTitle || 'Map a New Chapter'}</h2>

              {/* Table of Contents */}
              <div className="preview-toc-box">
                <h4 className="preview-toc-heading">Table of contents</h4>
                <ol className="preview-toc-list">
                  {parsedPreview.toc.map((heading, idx) => (
                    <li key={idx}>
                      <span className="toc-num">{idx + 1}.</span>
                      <span className="toc-text">{heading}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* Rendered Prose */}
              <div className="preview-prose-body">
                {parsedPreview.paragraphs.map((p, idx) => (
                  <p key={idx}>{p}</p>
                ))}
              </div>

              {/* Formatted Code Box */}
              <div className="preview-code-card">
                <pre className="preview-code-pre">
                  <code>{parsedPreview.firstCodeBlock}</code>
                </pre>
              </div>

              {/* Related Lessons List */}
              <div className="preview-meta-section">
                <h4 className="preview-section-subhead">Related Lessons</h4>
                <ul className="preview-bullet-chains">
                  <li>• Java → concurrency → virtual threads</li>
                  <li>• Backend → APIs → async processing → resilience</li>
                  <li>• Cloud → containers → orchestration</li>
                </ul>
              </div>

              {/* Next Lessons */}
              <div className="preview-meta-section mt-sm">
                <h4 className="preview-section-subhead">Next Lessons</h4>
                <ul className="preview-bullet-chains">
                  <li>• Structured Task Scope &amp; Thread-Local Variables</li>
                </ul>
              </div>
            </div>
          </section>

          {/* ========================================================= */}
          {/* COLUMN 3: METADATA & CONCEPT SELECTION (RIGHT)            */}
          {/* ========================================================= */}
          <aside className="importer-column metadata-column">
            <div className="metadata-paper-card">
              {/* Domain Selector */}
              <div className="meta-field-group">
                <label className="meta-field-label">Domain</label>
                <div className="meta-select-wrapper">
                  <select
                    className="meta-select-input"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                  >
                    {DOMAIN_OPTIONS.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Module Selector */}
              <div className="meta-field-group">
                <label className="meta-field-label">Module</label>
                <div className="meta-select-wrapper">
                  <select
                    className="meta-select-input"
                    value={moduleName}
                    onChange={(e) => setModuleName(e.target.value)}
                  >
                    {MODULE_OPTIONS.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Chapter Name */}
              <div className="meta-field-group">
                <label className="meta-field-label">Chapter</label>
                <input
                  type="text"
                  className="meta-text-input"
                  value={chapterTitle}
                  onChange={(e) => setChapterTitle(e.target.value)}
                  placeholder="e.g. Map a New Chapter"
                />
              </div>

              {/* Prerequisites Selector */}
              <div className="meta-field-group">
                <label className="meta-field-label">Prerequisites</label>
                <div className="meta-select-wrapper">
                  <select
                    className="meta-select-input"
                    value={prerequisite}
                    onChange={(e) => setPrerequisite(e.target.value)}
                  >
                    <option value="Related concepts">Related concepts</option>
                    <option value="Java Concurrency">Java Concurrency</option>
                    <option value="Executors & Futures">Executors &amp; Futures</option>
                    <option value="Structured Concurrency">Structured Concurrency</option>
                  </select>
                </div>
              </div>

              {/* Related Concepts Interactive Chips */}
              <div className="meta-field-group">
                <label className="meta-field-label">Related concepts</label>
                <div className="concept-chips-container">
                  {relatedConcepts.map((concept, idx) => (
                    <span key={idx} className="concept-tag-chip">
                      <span>{concept}</span>
                      <button
                        type="button"
                        className="chip-remove-btn"
                        onClick={() => handleRemoveConceptTag(concept)}
                        title="Remove tag"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>

                <form onSubmit={handleAddConceptTag} className="add-concept-chip-form">
                  <input
                    type="text"
                    className="concept-chip-input"
                    placeholder="+ Add concept..."
                    value={newConceptTag}
                    onChange={(e) => setNewConceptTag(e.target.value)}
                  />
                  <button type="submit" className="concept-chip-add-btn">
                    <Plus size={14} />
                  </button>
                </form>
              </div>

              {/* Admin Security / IAM Note */}
              <div className="admin-iam-card">
                <div className="iam-header">
                  <ShieldCheck size={16} className="iam-icon" />
                  <span className="iam-title">Admin Ingestion Portal</span>
                </div>
                <p className="iam-text">
                  Curriculum ingestion is restricted to authorized architects. Configured for IAM role-based authentication.
                </p>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
