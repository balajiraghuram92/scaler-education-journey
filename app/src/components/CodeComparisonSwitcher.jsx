import React, { useState } from 'react';
import './CodeComparisonSwitcher.css';

export default function CodeComparisonSwitcher({ comparisons = [] }) {
  const [activeTabs, setActiveTabs] = useState({}); // comparisonId -> 'before' | 'after'
  const [copiedId, setCopiedId] = useState(null);

  if (!comparisons || comparisons.length === 0) return null;

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="code-comparisons-wrapper">
      {comparisons.map((comp) => {
        const activeTab = activeTabs[comp.id] || 'after'; // default to 'after' (modern/structured)
        const currentCode = activeTab === 'before' ? comp.beforeCode : comp.afterCode;
        const currentLanguage = activeTab === 'before' ? comp.beforeLanguage : comp.afterLanguage;
        const isCopied = copiedId === `${comp.id}-${activeTab}`;

        return (
          <div key={comp.id} className="code-comparison-card">
            {comp.title && (
              <div className="code-comparison-header">
                <h4 className="code-comparison-title">{comp.title}</h4>
                {comp.description && <p className="code-comparison-desc">{comp.description}</p>}
              </div>
            )}

            {/* Interactive Pill Switcher Toggle */}
            <div className="code-switcher-pill-container">
              <button
                type="button"
                className={`code-switcher-pill-btn ${activeTab === 'before' ? 'is-active is-before' : ''}`}
                onClick={() => setActiveTabs({ ...activeTabs, [comp.id]: 'before' })}
              >
                {comp.beforeLabel || 'Unstructured / Legacy'}
              </button>
              <span className="code-switcher-separator">vs</span>
              <button
                type="button"
                className={`code-switcher-pill-btn ${activeTab === 'after' ? 'is-active is-after' : ''}`}
                onClick={() => setActiveTabs({ ...activeTabs, [comp.id]: 'after' })}
              >
                {comp.afterLabel || 'Structured / Target Pattern'}
              </button>
            </div>

            {/* Code Chamber */}
            <div className="code-snippet-box">
              <div className="code-snippet-top-bar">
                <span className="code-lang-tag">{currentLanguage.toUpperCase()}</span>
                <button
                  type="button"
                  className="code-copy-btn"
                  onClick={() => handleCopy(currentCode, `${comp.id}-${activeTab}`)}
                >
                  {isCopied ? '✓ Copied' : 'Copy'}
                </button>
              </div>
              <pre className="code-snippet-content">
                <code>{currentCode}</code>
              </pre>
            </div>

            {comp.explanation && (
              <div className="code-comparison-explanation">
                <span className="explanation-icon">💡</span>
                <p className="explanation-text">{comp.explanation}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
