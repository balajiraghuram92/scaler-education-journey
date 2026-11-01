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

// Upper-case verbs that pseudo code is written in; highlighted like keywords.
const PSEUDO_KEYWORDS = /\b(SET|LET|IF|ELSE IF|ELSE|THEN|END IF|FOR EACH|FOR|IN|WHILE|REPEAT|UNTIL|END FOR|END WHILE|DEFINE|FUNCTION|CLASS|RETURN|CALL|PRINT|SHOW|READ|LOAD|IMPORT|CREATE|BUILD|SEND|ASK|WAIT|TRY|CATCH|WITH|ON ERROR|RUN|START|STOP|STORE|SAVE|APPEND|ADD|UPDATE|DELETE|AND|OR|NOT|OTHERWISE|INPUT|OUTPUT|END)\b/g;

function renderPseudoLine(line, key) {
  // A comment is "//" at the start of a line or after whitespace, so URLs stay intact.
  const comment = /(^|\s)\/\//.exec(line);
  const codePart = comment ? line.slice(0, comment.index + comment[1].length) : line;
  const commentPart = comment ? line.slice(comment.index + comment[1].length) : '';
  const nodes = [];
  let lastIndex = 0;
  let match;
  const pattern = new RegExp(PSEUDO_KEYWORDS.source, 'g');
  while ((match = pattern.exec(codePart)) !== null) {
    if (match.index > lastIndex) nodes.push(codePart.slice(lastIndex, match.index));
    nodes.push(<b key={`${key}-k${match.index}`} className="md-pseudo__kw">{match[0]}</b>);
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < codePart.length) nodes.push(codePart.slice(lastIndex));
  if (commentPart) nodes.push(<span key={`${key}-c`} className="md-pseudo__comment">{commentPart}</span>);
  return nodes;
}

function CopyButton({ text }) {
  const [copied, setCopied] = React.useState(false);
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  };
  return (
    <button type="button" className="md-code__copy" onClick={handleCopy}>
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

function CodeBlock({ language, text, className, title, reveal }) {
  if (language === 'pseudo') {
    const lines = text.split('\n');
    return (
      <div className="md-code md-code--labelled md-pseudo">
        <span className="md-code__label">Pseudo code{title ? ` · ${title}` : ''}</span>
        <pre className={className}>
          <code>
            {lines.map((line, index) => (
              <React.Fragment key={index}>
                {renderPseudoLine(line, `p${index}`)}
                {index < lines.length - 1 ? '\n' : null}
              </React.Fragment>
            ))}
          </code>
        </pre>
      </div>
    );
  }

  // Titles such as "Python · trip_01.py" already name the language.
  const titleNamesLanguage = title && language && title.toLowerCase().startsWith(language.toLowerCase());
  const label = titleNamesLanguage ? title : [title, language].filter(Boolean).join(' · ');
  const body = (
    <div className={`md-code${label ? ' md-code--labelled' : ''}`}>
      {label && <span className="md-code__label">{label}</span>}
      {(reveal || title) && <CopyButton text={text} />}
      <pre className={className}>
        <code className={language ? `language-${language}` : undefined}>{text}</code>
      </pre>
    </div>
  );

  if (!reveal) return body;
  return (
    <details className="md-reveal">
      <summary>
        <span className="md-reveal__show">View code</span>
        <span className="md-reveal__hide">Hide code</span>
      </summary>
      {body}
    </details>
  );
}

function DiagramBlock({ diagram }) {
  if (!diagram) return null;
  return (
    <figure className="md-diagram">
      <div
        className="md-diagram__canvas"
        role="img"
        aria-label={diagram.title}
        dangerouslySetInnerHTML={{ __html: diagram.svgContent }}
      />
    </figure>
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
 * code style while chapters use the chapter code style. `diagrams` maps a diagram's
 * order index to the lesson diagram that `{{diagram:N}}` places inline.
 */
export function MarkdownBlocks({ blocks, codeBlockClassName = 'chapter-code-block', keyPrefix = 'md', diagrams }) {
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
        return (
          <CodeBlock
            key={key}
            language={block.language}
            text={block.text}
            title={block.title}
            reveal={block.reveal}
            className={codeBlockClassName}
          />
        );
      case 'diagram':
        return <DiagramBlock key={key} diagram={diagrams?.get(block.index)} />;
      case 'table':
        return <TableBlock key={key} block={block} keyPrefix={key} />;
      case 'callout':
        return (
          <aside key={key} className={`md-callout md-callout--${block.tone}`} role="note">
            {block.label && <span className="md-callout__label">{block.label}</span>}
            <MarkdownBlocks blocks={block.blocks} codeBlockClassName={codeBlockClassName} keyPrefix={key} diagrams={diagrams} />
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
