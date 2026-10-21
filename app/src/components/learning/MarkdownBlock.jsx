import React from 'react';
import { parseMarkdownBlocks } from './markdownParser';
import './MarkdownBlock.css';

// `code` | **bold** | [text](url) | *italic* | _italic_
const INLINE_SOURCE = /(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)|\*\*([^*]+?)\*\*|\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)|(?<![*\w])\*([^*\s](?:[^*]*[^*\s])?)\*(?![*\w])|(?<![_\w])_([^_\s](?:[^_]*[^_\s])?)_(?![_\w])/.source;
const SAFE_HREF = /^(https?:|mailto:|\/|#|\.{1,2}\/)/i;

/**
 * Renders inline Markdown (code, bold, italics and links) as React nodes.
 * Links open in a new tab with rel="noreferrer"; in-page `#anchor` links do not.
 */
export function renderInline(text, keyPrefix = 'inline') {
  if (text === null || text === undefined) return null;
  const source = String(text);
  const nodes = [];
  let lastIndex = 0;
  let match;
  let tokenIndex = 0;

  // A fresh RegExp per call: recursion (bold/link/italic contents) must not share lastIndex.
  const pattern = new RegExp(INLINE_SOURCE, 'g');
  while ((match = pattern.exec(source)) !== null) {
    if (match.index > lastIndex) nodes.push(source.slice(lastIndex, match.index));
    const key = `${keyPrefix}-${tokenIndex}`;
    tokenIndex += 1;

    if (match[1]) {
      nodes.push(<code key={key}>{match[2]}</code>);
    } else if (match[3] !== undefined) {
      nodes.push(<strong key={key}>{renderInline(match[3], key)}</strong>);
    } else if (match[4] !== undefined) {
      const label = renderInline(match[4], key);
      const href = match[5];
      if (!SAFE_HREF.test(href)) {
        nodes.push(<React.Fragment key={key}>{label}</React.Fragment>);
      } else if (href.startsWith('#')) {
        nodes.push(<a key={key} href={href} className="md-link">{label}</a>);
      } else {
        nodes.push(<a key={key} href={href} className="md-link" target="_blank" rel="noreferrer">{label}</a>);
      }
    } else {
      const italic = match[6] !== undefined ? match[6] : match[7];
      nodes.push(<em key={key}>{renderInline(italic, key)}</em>);
    }
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < source.length) nodes.push(source.slice(lastIndex));
  return nodes;
}

function CodeBlock({ language, text, className }) {
  return (
    <div className={`md-code${language ? ' md-code--labelled' : ''}`}>
      {language && <span className="md-code__label">{language}</span>}
      <pre className={className}>
        <code className={language ? `language-${language}` : undefined}>{text}</code>
      </pre>
    </div>
  );
}

function TableBlock({ block, keyPrefix }) {
  const alignOf = (index) => (block.align[index] ? { textAlign: block.align[index] } : undefined);
  return (
    <div className="md-table-wrap">
      <table className="md-table">
        {block.header && (
          <thead>
            <tr>
              {block.header.map((cell, index) => (
                <th key={`${keyPrefix}-h-${index}`} scope="col" style={alignOf(index)}>{renderInline(cell, `${keyPrefix}-h-${index}`)}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {block.rows.map((row, rowIndex) => (
            <tr key={`${keyPrefix}-r-${rowIndex}`}>
              {row.map((cell, cellIndex) => (
                <td key={`${keyPrefix}-r-${rowIndex}-${cellIndex}`} style={alignOf(cellIndex)}>
                  {renderInline(cell, `${keyPrefix}-r-${rowIndex}-${cellIndex}`)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Renders already-parsed blocks. `codeBlockClassName` lets the quiz keep its compact
 * code style while chapters use the chapter code style.
 */
export function MarkdownBlocks({ blocks, codeBlockClassName = 'chapter-code-block', keyPrefix = 'md' }) {
  return blocks.map((block, index) => {
    const key = `${keyPrefix}-${index}`;
    switch (block.type) {
      case 'heading':
        return block.level >= 4
          ? <h5 key={key} className="chamber-subheading md-minor-heading">{renderInline(block.text, key)}</h5>
          : <h4 key={key} className="chamber-subheading">{renderInline(block.text, key)}</h4>;
      case 'unordered-list':
        return (
          <ul key={key} className="chapter-markdown-list">
            {block.items.map((item, itemIndex) => <li key={`${key}-${itemIndex}`}>{renderInline(item, `${key}-${itemIndex}`)}</li>)}
          </ul>
        );
      case 'ordered-list':
        return (
          <ol key={key} className="chapter-markdown-list chapter-markdown-list--ordered">
            {block.items.map((item, itemIndex) => <li key={`${key}-${itemIndex}`}>{renderInline(item, `${key}-${itemIndex}`)}</li>)}
          </ol>
        );
      case 'code':
        return <CodeBlock key={key} language={block.language} text={block.text} className={codeBlockClassName} />;
      case 'table':
        return <TableBlock key={key} block={block} keyPrefix={key} />;
      case 'callout':
        return (
          <aside key={key} className={`md-callout md-callout--${block.tone}`} role="note">
            {block.label && <span className="md-callout__label">{block.label}</span>}
            <MarkdownBlocks blocks={block.blocks} codeBlockClassName={codeBlockClassName} keyPrefix={key} />
          </aside>
        );
      case 'rule':
        return <hr key={key} className="md-rule" />;
      default:
        return <p key={key}>{renderInline(block.text, key)}</p>;
    }
  });
}

export default function MarkdownBlock({ text, className = '', codeBlockClassName, as: Tag = 'div', ...rest }) {
  if (!text || typeof text !== 'string') return null;
  const blocks = parseMarkdownBlocks(text);
  if (blocks.length === 0) return null;

  return (
    <Tag className={`md-block ${className}`.trim()} {...rest}>
      <MarkdownBlocks blocks={blocks} codeBlockClassName={codeBlockClassName} />
    </Tag>
  );
}
