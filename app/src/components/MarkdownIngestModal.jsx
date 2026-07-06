import { useState, useEffect, useMemo } from 'react';
import { UploadCloud, X, FileText, CheckCircle, AlertCircle, Layers, PlusCircle, RefreshCw } from 'lucide-react';

export default function MarkdownIngestModal({ isOpen, onClose, onSuccess, verticals = [] }) {
  const [markdownContent, setMarkdownContent] = useState('');
  const [targetMode, setTargetMode] = useState('existing'); // 'existing' | 'new'
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

  // Client-side parser for live preview
  const parsedPreview = useMemo(() => {
    if (!markdownContent.trim()) return { modules: [], totalTasks: 0, totalCompleted: 0 };

    const lines = markdownContent.split(/\r?\n/);
    let currentModule = 'General';
    const moduleMap = {};
    let totalTasks = 0;
    let totalCompleted = 0;

    for (const rawLine of lines) {
      const line = rawLine.trim();
      const headerMatch = line.match(/^##\s+(.+)$/);
      if (headerMatch) {
        currentModule = headerMatch[1].trim();
        if (!moduleMap[currentModule]) {
          moduleMap[currentModule] = { count: 0, completed: 0 };
        }
        continue;
      }

      const taskMatch = line.match(/^- \[([ xX])\]\s+(.+)$/);
      if (taskMatch) {
        if (!moduleMap[currentModule]) {
          moduleMap[currentModule] = { count: 0, completed: 0 };
        }
        const isCompleted = taskMatch[1].toLowerCase() === 'x';
        moduleMap[currentModule].count += 1;
        totalTasks += 1;
        if (isCompleted) {
          moduleMap[currentModule].completed += 1;
          totalCompleted += 1;
        }
      }
    }

    const modules = Object.entries(moduleMap).map(([name, data]) => ({
      name,
      count: data.count,
      completed: data.completed
    }));

    return { modules, totalTasks, totalCompleted };
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

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(5, 5, 10, 0.85)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        zIndex: 2000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-md)',
        overflowY: 'auto'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '750px',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: 'var(--space-xl)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--accent-cyan)',
          boxShadow: 'var(--shadow-glow-cyan)',
          position: 'relative'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <UploadCloud size={22} style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <div>
              <h2 className="gradient-text" style={{ fontSize: '1.4rem', margin: 0 }}>
                Ingest Markdown Curriculum
              </h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>
                Upload or paste markdown to parse modules and import into SQL Server
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: 'var(--space-xs)'
            }}
          >
            <X size={24} />
          </button>
        </div>

        {errorMsg && (
          <div
            style={{
              padding: 'var(--space-md)',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 45, 117, 0.1)',
              border: '1px solid var(--accent-pink)',
              color: '#ff6b9d',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-sm)',
              marginBottom: 'var(--space-lg)'
            }}
          >
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {/* Target Selection */}
          <div
            style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-md)'
            }}
          >
            <label style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 'var(--space-sm)', display: 'block' }}>
              Target Database Destination
            </label>
            <div style={{ display: 'flex', gap: 'var(--space-lg)', marginBottom: 'var(--space-md)' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', cursor: 'pointer', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                <input
                  type="radio"
                  name="targetMode"
                  value="existing"
                  checked={targetMode === 'existing'}
                  onChange={() => setTargetMode('existing')}
                />
                <Layers size={16} style={{ color: 'var(--accent-cyan)' }} />
                <span>Update Existing Vertical</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', cursor: 'pointer', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                <input
                  type="radio"
                  name="targetMode"
                  value="new"
                  checked={targetMode === 'new'}
                  onChange={() => setTargetMode('new')}
                />
                <PlusCircle size={16} style={{ color: 'var(--accent-emerald)' }} />
                <span>Create New Vertical</span>
              </label>
            </div>

            {targetMode === 'existing' ? (
              <div>
                <select
                  value={selectedVerticalId}
                  onChange={(e) => setSelectedVerticalId(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem var(--space-md)',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-accent)',
                    color: 'var(--text-primary)',
                    fontFamily: 'Outfit, sans-serif',
                    fontSize: '0.95rem'
                  }}
                >
                  {verticals.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} ({v.tasks?.length || 0} tasks)
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                <input
                  type="text"
                  placeholder="Vertical Name (e.g. System Design Track)"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem var(--space-md)',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-accent)',
                    color: 'var(--text-primary)',
                    fontFamily: 'Outfit, sans-serif',
                    fontSize: '0.95rem'
                  }}
                />
                <input
                  type="text"
                  placeholder="Short Description (optional)"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem var(--space-md)',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-primary)',
                    fontFamily: 'Outfit, sans-serif',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            )}
          </div>

          {/* File Dropzone & Textarea */}
          <div>
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              style={{
                border: `2px dashed ${dragActive ? 'var(--accent-cyan)' : 'var(--border-accent)'}`,
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-lg)',
                textAlign: 'center',
                background: dragActive ? 'rgba(0, 240, 255, 0.05)' : 'rgba(255, 255, 255, 0.01)',
                transition: 'all var(--transition-fast)',
                cursor: 'pointer',
                marginBottom: 'var(--space-md)'
              }}
              onClick={() => document.getElementById('file-input-md')?.click()}
            >
              <input
                id="file-input-md"
                type="file"
                accept=".md,.markdown"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files?.[0] && handleFileRead(e.target.files[0])}
              />
              <FileText size={32} style={{ color: 'var(--accent-cyan)', marginBottom: 'var(--space-xs)' }} />
              <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.95rem' }}>
                Drag & drop a .md file here, or click to browse
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Supports standard markdown formatting with <code style={{ color: 'var(--accent-cyan)' }}>## Module</code> headers and <code style={{ color: 'var(--accent-cyan)' }}>- [ ]</code> checkboxes
              </div>
            </div>

            {/* Markdown Textarea */}
            <textarea
              rows={6}
              placeholder="Or paste Markdown curriculum here...&#10;&#10;## Module 1: Foundations&#10;- [ ] Task 1&#10;- [x] Completed Task 2"
              value={markdownContent}
              onChange={(e) => setMarkdownContent(e.target.value)}
              style={{
                width: '100%',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-primary)',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                lineHeight: 1.5,
                resize: 'vertical'
              }}
            />
          </div>

          {/* Real-time Parsed Preview Box */}
          <div
            style={{
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-md)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                LIVE PARSER PREVIEW
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {parsedPreview.modules.length} Modules | {parsedPreview.totalTasks} Tasks ({parsedPreview.totalCompleted} Completed)
              </span>
            </div>

            {parsedPreview.modules.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0, fontStyle: 'italic' }}>
                No modules or tasks detected yet. Add markdown with headers (##) and task checkboxes (- [ ]).
              </p>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-xs)', marginTop: 'var(--space-xs)' }}>
                {parsedPreview.modules.map((mod, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '0.25rem 0.6rem',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid var(--border-subtle)',
                      fontSize: '0.75rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--space-xs)'
                    }}
                  >
                    <CheckCircle size={12} style={{ color: 'var(--accent-emerald)' }} />
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{mod.name}:</span>
                    <span style={{ color: 'var(--accent-cyan)' }}>{mod.count} tasks</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-md)' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <RefreshCw size={18} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
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
