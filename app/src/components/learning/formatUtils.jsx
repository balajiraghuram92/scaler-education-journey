import React from 'react';

/**
 * Parses inline markdown: bold (**text**) and code (`code`).
 */
export function formatInline(text) {
  if (!text || typeof text !== 'string') return text;
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean).map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={`${part}-${index}`}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={`${part}-${index}`}>{part.slice(1, -1)}</code>;
    }
    return <React.Fragment key={`${part}-${index}`}>{part}</React.Fragment>;
  });
}

/**
 * Formats question/explanation content containing prose, inline code, and multiline code snippets.
 */
export function FormattedContent({ text, className = '' }) {
  if (!text || typeof text !== 'string') return null;

  const rawSegments = text.split('\n\n');

  return (
    <div className={`formatted-content ${className}`.trim()}>
      {rawSegments.map((segment, segIdx) => {
        const trimmed = segment.trim();

        // 1. Explicit Markdown code fence: ```java ... ```
        if (trimmed.startsWith('```') && trimmed.endsWith('```')) {
          const codeBody = trimmed.replace(/^```[a-z]*\n?/, '').replace(/```$/, '');
          return (
            <pre key={segIdx} className="concept-check__code-block">
              <code>{codeBody}</code>
            </pre>
          );
        }

        // 2. Multiline code block heuristic (contains newlines with Java code indicators)
        if (
          segment.includes('\n') &&
          (segment.includes(';') ||
            segment.includes('{') ||
            segment.includes('System.out') ||
            segment.includes(' = ') ||
            segment.includes('public '))
        ) {
          return (
            <pre key={segIdx} className="concept-check__code-block">
              <code>{segment}</code>
            </pre>
          );
        }

        // 3. Regular prose line with inline code and bolding
        return (
          <p key={segIdx} className="concept-check__prose-part">
            {formatInline(segment)}
          </p>
        );
      })}
    </div>
  );
}
