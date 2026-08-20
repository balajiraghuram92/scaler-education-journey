import React from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';
import './ConceptDetailPopover.css';

export default function ConceptDetailPopover({ concept, isOpen, onClose }) {
  if (!isOpen || !concept) return null;

  const displayTitle = concept.popoverTitle || concept.title || 'Concept Overview';

  return (
    <div className="concept-detail-popover" role="dialog" aria-label={displayTitle}>
      {/* Upward-pointing caret pointing to parent concept pill */}
      <div className="popover-caret" />

      {/* Popover Header */}
      <header className="popover-header">
        <h3 className="popover-title">{displayTitle}</h3>
      </header>

      <div className="popover-divider" />

      {/* Popover Content */}
      <div className="popover-content">
        {/* 1. Prerequisites */}
        {concept.prerequisites && concept.prerequisites.length > 0 && (
          <div className="popover-section">
            <h4 className="section-heading">Prerequisites</h4>
            <ul className="section-list">
              {concept.prerequisites.map((p, idx) => (
                <li key={idx} className="list-item">
                  <span className="bullet">•</span>
                  <span className="item-text">{p.name || p}</span>
                  {p.status && (
                    <span className="status-tag">({p.status})</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 2. Related Lessons */}
        {concept.relatedLessons && concept.relatedLessons.length > 0 && (
          <div className="popover-section">
            <h4 className="section-heading">Related Lessons</h4>
            <ul className="section-list">
              {concept.relatedLessons.map((lesson, idx) => {
                const slug = lesson.toLowerCase().includes('agent') ? 'building-an-ai-agent' :
                             lesson.toLowerCase().includes('rag') ? 'rag-retrieval-augmented-generation' :
                             lesson.toLowerCase().includes('oop') ? '03-oop-2-access-modifiers-encapsulation' :
                             'structured-concurrency';
                return (
                  <li key={idx} className="list-item">
                    <span className="bullet">•</span>
                    <Link to={`/chapter/${slug}`} className="item-text" style={{ color: '#2C5E55', textDecoration: 'none' }}>
                      {lesson}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {/* 3. Next Lessons */}
        {concept.nextLessons && concept.nextLessons.length > 0 && (
          <div className="popover-section">
            <h4 className="section-heading">Next Lessons</h4>
            <ul className="section-list">
              {concept.nextLessons.map((lesson, idx) => {
                const slug = lesson.toLowerCase().includes('agent') ? 'building-an-ai-agent' :
                             lesson.toLowerCase().includes('rag') ? 'rag-retrieval-augmented-generation' :
                             lesson.toLowerCase().includes('oop') ? '03-oop-2-access-modifiers-encapsulation' :
                             'structured-concurrency';
                return (
                  <li key={idx} className="list-item">
                    <span className="bullet">•</span>
                    <Link to={`/chapter/${slug}`} className="item-text" style={{ color: '#2C5E55', textDecoration: 'none' }}>
                      {lesson}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

ConceptDetailPopover.propTypes = {
  concept: PropTypes.shape({
    id: PropTypes.string,
    title: PropTypes.string,
    popoverTitle: PropTypes.string,
    prerequisites: PropTypes.arrayOf(
      PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.shape({
          name: PropTypes.string,
          status: PropTypes.string
        })
      ])
    ),
    relatedLessons: PropTypes.arrayOf(PropTypes.string),
    nextLessons: PropTypes.arrayOf(PropTypes.string)
  }),
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func
};
