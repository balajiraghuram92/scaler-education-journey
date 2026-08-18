import { useState } from 'react';
import { X, Plus, BookOpen } from 'lucide-react';
import './AddLessonModal.css';

export default function AddLessonModal({ isOpen, onClose, onSuccess, modules = [] }) {
  const [moduleId, setModuleId] = useState(modules[0]?.id || 1);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [lectureNumber, setLectureNumber] = useState(1);
  const [horstmannRef, setHorstmannRef] = useState('');
  const [contentBody, setContentBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !slug) {
      setError('Title and Slug are required.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/lessons`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': import.meta.env.VITE_API_KEY || ''
        },
        body: JSON.stringify({
          moduleId: parseInt(moduleId),
          slug: slug.trim().toLowerCase(),
          title: title.trim(),
          description: description.trim(),
          lectureNumber: parseInt(lectureNumber) || 1,
          horstmannRef: horstmannRef.trim(),
          contentBody: contentBody.trim(),
          estimatedMinutes: 60
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || 'Failed to create lesson.');
      }

      setTitle('');
      setSlug('');
      setDescription('');
      setContentBody('');
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen size={20} style={{ color: '#2563eb' }} />
            <h3>Add New Curriculum Lesson</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div style={{ padding: '10px 14px', borderRadius: '8px', background: '#fef2f2', color: '#b91c1c', fontSize: '0.85rem' }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label>Module</label>
              <select className="form-select" value={moduleId} onChange={(e) => setModuleId(e.target.value)}>
                {modules.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.badge ? `${m.badge}: ` : ''}{m.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Lesson Title</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Lesson 4 — OOP-3: Polymorphism & Interfaces"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (!slug) {
                    setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''));
                  }
                }}
                required
              />
            </div>

            <div className="form-group">
              <label>Slug (URL key)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. 04-oop-3-polymorphism-interfaces"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Lecture Number & Reference</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '10px' }}>
                <input
                  type="number"
                  className="form-input"
                  placeholder="Lecture #"
                  value={lectureNumber}
                  onChange={(e) => setLectureNumber(e.target.value)}
                />
                <input
                  type="text"
                  className="form-input"
                  placeholder="Core Java Horstmann Reference"
                  value={horstmannRef}
                  onChange={(e) => setHorstmannRef(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Description</label>
              <input
                type="text"
                className="form-input"
                placeholder="Brief summary of concepts"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Markdown Content Body</label>
              <textarea
                className="form-textarea"
                placeholder="# Lesson Notes..."
                value={contentBody}
                onChange={(e) => setContentBody(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn btn-primary"
              style={{ padding: '8px 16px', fontSize: '0.85rem', background: '#2563eb' }}
            >
              {submitting ? 'Creating...' : 'Create Lesson'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
