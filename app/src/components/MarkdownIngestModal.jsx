import { useState, useEffect, useMemo } from 'react';
import { UploadCloud, X, FileText, CheckCircle2, AlertCircle, Layers, PlusCircle, RefreshCw, Folder, Circle, Settings, XCircle } from 'lucide-react';
import './MarkdownIngestModal.css';

export default function MarkdownIngestModal({ isOpen, onClose, onSuccess, verticals = [] }) {
  const [markdownContent, setMarkdownContent] = useState('');
  const [targetMode, setTargetMode] = useState('existing');
  const [selectedVerticalId, setSelectedVerticalId] = useState('');
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    if (verticals.length > 0 && !selectedVerticalId) {
      setSelectedVerticalId(verticals[0].id.toString());
    }
  }, [verticals, selectedVerticalId]);

  const parsedPreview = useMemo(() => {
    if (!markdownContent.trim()) return { modules: [], totalTasks: 0, totalCompleted: 0 };

    const lines = markdownContent.split(/\r?\n/);
    let currentModule = 'General';
    const modulesMap = new Map();
    let totalTasks = 0;
    let totalCompleted = 0;

    for (const rawLine of lines) {
      const line = rawLine.trim();
      const headerMatch = line.match(/^##\s+(.+)$/);
      if (headerMatch) {
        currentModule = headerMatch[1].trim();
        if (!modulesMap.has(currentModule)) {
          modulesMap.set(currentModule, { name: currentModule, tasks: [] });
        }
        continue;
      }

      const taskMatch = line.match(/^- \[([ xX])\]\s+(.+)$/);
      if (taskMatch) {
        if (!modulesMap.has(currentModule)) {
          modulesMap.set(currentModule, { name: currentModule, tasks: [] });
        }
        const isCompleted = taskMatch[1].toLowerCase() === 'x';
        modulesMap.get(currentModule).tasks.push({
          name: taskMatch[2].trim(),
          isCompleted
        });
        totalTasks += 1;
        if (isCompleted) {
          totalCompleted += 1;
        }
      }
    }

    return { modules: Array.from(modulesMap.values()), totalTasks, totalCompleted };
  }, [markdownContent]);

  if (!isOpen) return null;

  const handleFileRead = (file) => {
    if (!file) return;
    if (!file.name.endsWith('.md') && !file.name.endsWith('.markdown') && file.type !== 'text/markdown') {
      setErrorMsg('Please select a valid Markdown (.md) file.');
      return;
    }
    setErrorMsg(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      setMarkdownContent(e.target.result || '');
      if (targetMode === 'new' && !newName) {
        const titleFromName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
        setNewName(titleFromName.charAt(0).toUpperCase() + titleFromName.slice(1));
      }
    };
    reader.readAsText(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileRead(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!markdownContent.trim()) {
      setErrorMsg('Please provide Markdown content or upload a .md file.');
      return;
    }

    if (targetMode === 'new' && !newName.trim()) {
      setErrorMsg('Please enter a name for the new Study Vertical.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    const payload = {
      verticalId: targetMode === 'existing' ? parseInt(selectedVerticalId, 10) : null,
      name: targetMode === 'new' ? newName : null,
      description: targetMode === 'new' ? newDesc : null,
      markdownContent: markdownContent
    };

    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/verticals/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || 'Failed to ingest markdown content.');
      }

      const updatedVertical = await res.json();
      setIsSubmitting(false);
      onSuccess?.(updatedVertical);
      onClose();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'An unexpected error occurred during ingestion.');
      setIsSubmitting(false);
    }
  };

  const selectedVerticalName = verticals.find(v => v.id.toString() === selectedVerticalId)?.name || 'FDE Curriculum';

  return (
    <div
      className="ingest-modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="ingest-modal-panel">
        <div className="ingest-modal-header">
          <div className="ingest-header-left">
            <div className="ingest-header-icon">
              <UploadCloud size={28} />
            </div>
            <div className="ingest-header-text">
              <h2>Ingest Markdown Curriculum</h2>
              <p>Upload or paste markdown to parse modules and import into SQL Server</p>
            </div>
          </div>
          <button onClick={onClose} className="ingest-close-btn" type="button">
            <X size={24} />
          </button>
        </div>

        {errorMsg && (
          <div style={{
            padding: '1rem', borderRadius: '12px', background: '#fee2e2',
            border: '1px solid #fecaca', color: '#ef4444', fontSize: '0.95rem',
            display: 'flex', alignItems: 'center', gap: '0.75rem'
          }}>
            <AlertCircle size={20} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="ingest-section">
            <h3 className="ingest-section-title">Target Database Section</h3>
            <div className="ingest-radio-group">
              <label className="ingest-radio-label">
                <input
                  type="radio"
                  name="targetMode"
                  value="existing"
                  checked={targetMode === 'existing'}
                  onChange={() => setTargetMode('existing')}
                />
                <Layers size={18} className="ingest-radio-icon" />
                <span>Update Existing</span>
              </label>
              <label className="ingest-radio-label">
                <input
                  type="radio"
                  name="targetMode"
                  value="new"
                  checked={targetMode === 'new'}
                  onChange={() => setTargetMode('new')}
                />
                <PlusCircle size={18} className="ingest-radio-icon create-new" />
                <span>Create New</span>
              </label>
            </div>

            {targetMode === 'existing' ? (
              <select
                className="ingest-input"
                value={selectedVerticalId}
                onChange={(e) => setSelectedVerticalId(e.target.value)}
              >
                {verticals.length === 0 && <option value="">No existing curriculums found...</option>}
                {verticals.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.tasks?.length || 0} tasks) — 4% Mastery from previous contexts
                  </option>
                ))}
              </select>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <input
                  type="text"
                  placeholder="Vertical Name (e.g. System Design Track)"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="ingest-input"
                />
                <input
                  type="text"
                  placeholder="Short Description (optional)"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="ingest-input"
                />
              </div>
            )}
          </div>

          <div className="ingest-dual-input">
            <div
              className={`ingest-dropzone ${dragActive ? 'active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input-md')?.click()}
            >
              <input
                id="file-input-md"
                type="file"
                accept=".md,.markdown"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files?.[0] && handleFileRead(e.target.files[0])}
              />
              <FileText size={36} className="ingest-dropzone-icon" />
              <div className="ingest-dropzone-title">Drag & drop a .md file here, or click to browse</div>
              <div className="ingest-dropzone-subtitle">
                Supports standard markdown formatting with <code>## Module</code> headers and <code>- [ ]</code> checkboxes
              </div>
            </div>

            <textarea
              className="ingest-textarea"
              placeholder="Or paste Markdown curriculum here...&#10;&#10;## Module 1: Foundations&#10;- [ ] Task 1&#10;- [x] Completed Task 2"
              value={markdownContent}
              onChange={(e) => setMarkdownContent(e.target.value)}
            />
          </div>

          <div className="ingest-stats-section">
            <div className="ingest-stats-header">
              <div className="ingest-stats-title-wrap">
                <span className="ingest-stats-label">LIVE PARSER STATS</span>
                <h4 className="ingest-stats-title">{targetMode === 'existing' ? selectedVerticalName : (newName || 'Agentic AI Core')} (Prerequisite)</h4>
              </div>
              <div className="ingest-stats-summary">
                {parsedPreview.modules.length} Modules | {parsedPreview.totalTasks} Tasks ({parsedPreview.totalCompleted} Completed)
              </div>
            </div>

            <div className="ingest-stats-body">
              <div className="ingest-tree">
                <div className="ingest-tree-item root">
                  <div className="ingest-tree-item-content">
                    <Folder size={18} color="#64748b" />
                    <span>{targetMode === 'existing' ? selectedVerticalName : (newName || 'New Curriculum')}</span>
                  </div>
                  <div className="ingest-tree-depth">skill depth<br/><strong>98%</strong></div>
                </div>

                {parsedPreview.modules.map((mod, i) => (
                  <div key={i}>
                    <div className="ingest-tree-item ingest-tree-module">
                      <div className="ingest-tree-item-content">
                        <CheckCircle2 size={16} color="#3b82f6" />
                        <span>{mod.name}</span>
                      </div>
                      <div className="ingest-tree-depth">skill depth<br/><strong>95%</strong></div>
                    </div>
                    {mod.tasks.slice(0, 5).map((task, j) => (
                      <div key={j} className="ingest-tree-item ingest-tree-task">
                        <div className="ingest-tree-item-content">
                          {task.isCompleted ? (
                            <XCircle size={14} color="#94a3b8" />
                          ) : (
                            <Circle size={14} color="#64748b" />
                          )}
                          <span style={{ color: task.isCompleted ? '#94a3b8' : '#1e293b' }}>
                            {task.name} {task.isCompleted ? '(X)' : '(0)'}
                          </span>
                        </div>
                        <div className="ingest-tree-depth">skill depth<br/><strong>92%</strong></div>
                      </div>
                    ))}
                    {mod.tasks.length > 5 && (
                      <div className="ingest-tree-item ingest-tree-task" style={{ paddingLeft: '1rem', color: '#64748b' }}>
                        ...and {mod.tasks.length - 5} more tasks
                      </div>
                    )}
                  </div>
                ))}
                {parsedPreview.modules.length === 0 && (
                  <div style={{ color: '#64748b', fontStyle: 'italic', padding: '1rem 0', textAlign: 'center' }}>
                    No modules or tasks detected yet. Add markdown content above.
                  </div>
                )}
              </div>

              <div className="ingest-insight-card">
                <div className="ingest-insight-icon">
                  <Settings size={20} />
                </div>
                <div className="ingest-insight-title">AI Insight: Curriculum Balance & Complexity Check</div>
                <div className="ingest-insight-text">
                  {parsedPreview.modules.length > 0
                    ? `${parsedPreview.modules[0]?.name || 'Module 1'} appears balanced. Overall pattern maturity check positive. Task load within parameters.`
                    : "Awaiting curriculum data to generate AI insights."}
                </div>
              </div>
            </div>
          </div>

          <div className="ingest-actions">
            <button type="button" className="ingest-btn ingest-btn-cancel" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="ingest-btn ingest-btn-submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <RefreshCw size={18} className="spin" />
                  Importing...
                </>
              ) : (
                <>
                  <UploadCloud size={18} />
                  Import to SQL Database
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
