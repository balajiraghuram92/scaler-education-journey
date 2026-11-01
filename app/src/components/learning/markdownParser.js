/**
 * Small, dependency-free Markdown block parser shared by the chapter reader and the
 * MCQ quiz. It covers the subset the curriculum uses: headings, paragraphs, lists,
 * fenced code (blank lines inside fences are kept), pipe tables, `>` callouts,
 * horizontal rules and `{{diagram:N}}` placeholders. Inline formatting is handled by
 * MarkdownBlock's renderInline.
 *
 * A fence's info string may carry attributes after the language:
 *   ```pseudo title="hello_agent.py"   → pseudo code, keywords highlighted
 *   ```python reveal title="hello_agent.py" → code hidden behind a "View code" toggle
 */

const FENCE_PATTERN = /^(`{3,}|~{3,})\s*([^\s`]*)/;
const FENCE_TITLE_PATTERN = /\btitle="([^"]*)"/;
const DIAGRAM_PATTERN = /^\{\{diagram:(\d+)\}\}$/;
const HEADING_PATTERN = /^(#{1,6})\s+(.*)$/;
const UNORDERED_PATTERN = /^[-*+]\s+(.+)$/;
const ORDERED_PATTERN = /^\d+[.)]\s+(.+)$/;
const RULE_PATTERN = /^(?:-{3,}|\*{3,}|_{3,})$/;
const TABLE_SEPARATOR_CELL = /^:?-{1,}:?$/;
const CALLOUT_LABEL_PATTERN = /^\*\*([^*]+?)\*\*:?\s*(.*)$/;
const GITHUB_ALERT_PATTERN = /^\[!(\w+)\]\s*(.*)$/;

function leadingSpaces(line) {
  return line.length - line.trimStart().length;
}

function readFence(lines, startIndex) {
  const openLine = lines[startIndex];
  const [opening, marker, language] = openLine.trim().match(FENCE_PATTERN);
  const info = openLine.trim().slice(opening.length);
  const title = info.match(FENCE_TITLE_PATTERN)?.[1] || '';
  const reveal = /(^|\s)reveal(\s|$)/.test(info.replace(FENCE_TITLE_PATTERN, ''));
  const indent = leadingSpaces(openLine);
  const codeLines = [];
  let index = startIndex + 1;

  while (index < lines.length) {
    const candidate = lines[index].trim();
    if (candidate.startsWith(marker[0].repeat(3)) && candidate.replace(/[`~]/g, '') === '') {
      index += 1;
      break;
    }
    const raw = lines[index];
    // Strip the fence's own indentation (e.g. a fence nested under a list item).
    codeLines.push(leadingSpaces(raw) >= indent ? raw.slice(indent) : raw.trimStart());
    index += 1;
  }

  return {
    block: { type: 'code', language: language || '', text: codeLines.join('\n'), title, reveal },
    nextIndex: index
  };
}

export function splitTableRow(line) {
  let row = line.trim();
  if (row.startsWith('|')) row = row.slice(1);
  if (row.endsWith('|') && !row.endsWith('\\|')) row = row.slice(0, -1);

  const cells = [];
  let current = '';
  let inCode = false;
  for (let i = 0; i < row.length; i += 1) {
    const char = row[i];
    if (char === '\\' && row[i + 1] === '|') {
      current += '|';
      i += 1;
    } else if (char === '`') {
      inCode = !inCode;
      current += char;
    } else if (char === '|' && !inCode) {
      cells.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  cells.push(current.trim());
  return cells;
}

function parseTable(tableLines) {
  const rows = tableLines.map(splitTableRow);
  const hasHeader = rows.length > 1 && rows[1].every((cell) => TABLE_SEPARATOR_CELL.test(cell.replace(/\s+/g, '')));

  if (!hasHeader) {
    return { type: 'table', header: null, align: [], rows };
  }

  const align = rows[1].map((cell) => {
    const compact = cell.replace(/\s+/g, '');
    if (compact.startsWith(':') && compact.endsWith(':')) return 'center';
    if (compact.endsWith(':')) return 'right';
    if (compact.startsWith(':')) return 'left';
    return null;
  });

  return { type: 'table', header: rows[0], align, rows: rows.slice(2) };
}

function calloutTone(label) {
  const value = (label || '').toLowerCase();
  if (/(warn|pitfall|gotcha|caution|danger|avoid|mistake|trap|anti-pattern|important)/.test(value)) return 'caution';
  return 'tip';
}

function parseCallout(quoteLines) {
  const inner = quoteLines.map((line) => line.trim().replace(/^>\s?/, ''));
  let label = null;
  const firstContent = inner.findIndex((line) => line.trim() !== '');

  if (firstContent >= 0) {
    const first = inner[firstContent].trim();
    const alert = first.match(GITHUB_ALERT_PATTERN);
    const bold = first.match(CALLOUT_LABEL_PATTERN);
    if (alert) {
      label = alert[1].charAt(0).toUpperCase() + alert[1].slice(1).toLowerCase();
      inner[firstContent] = alert[2];
    } else if (bold) {
      label = bold[1].replace(/:\s*$/, '').trim();
      inner[firstContent] = bold[2];
    }
  }

  return {
    type: 'callout',
    label,
    tone: calloutTone(label),
    blocks: parseMarkdownBlocks(inner.join('\n'))
  };
}

/**
 * Parses Markdown text into a flat list of blocks:
 * paragraph | heading | unordered-list | ordered-list | code | table | callout | rule | diagram
 */
export function parseMarkdownBlocks(text) {
  const lines = (text || '').replace(/\r\n?/g, '\n').split('\n');
  const blocks = [];
  let paragraph = [];
  let list = null;

  const flushParagraph = () => {
    if (paragraph.length > 0) {
      blocks.push({ type: 'paragraph', text: paragraph.join(' ') });
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list && list.items.length > 0) blocks.push(list);
    list = null;
  };
  const flushAll = () => {
    flushParagraph();
    flushList();
  };

  let index = 0;
  while (index < lines.length) {
    const rawLine = lines[index];
    const line = rawLine.trim();

    if (FENCE_PATTERN.test(line)) {
      flushAll();
      const { block, nextIndex } = readFence(lines, index);
      blocks.push(block);
      index = nextIndex;
      continue;
    }

    if (!line) {
      flushAll();
      index += 1;
      continue;
    }

    if (line.startsWith('|')) {
      flushAll();
      const tableLines = [];
      while (index < lines.length && lines[index].trim().startsWith('|')) {
        tableLines.push(lines[index]);
        index += 1;
      }
      blocks.push(parseTable(tableLines));
      continue;
    }

    if (line.startsWith('>')) {
      flushAll();
      const quoteLines = [];
      while (index < lines.length && lines[index].trim().startsWith('>')) {
        quoteLines.push(lines[index]);
        index += 1;
      }
      blocks.push(parseCallout(quoteLines));
      continue;
    }

    const diagram = line.match(DIAGRAM_PATTERN);
    if (diagram) {
      flushAll();
      blocks.push({ type: 'diagram', index: Number(diagram[1]) });
      index += 1;
      continue;
    }

    const heading = line.match(HEADING_PATTERN);
    if (heading) {
      flushAll();
      blocks.push({ type: 'heading', level: heading[1].length, text: heading[2].trim() });
      index += 1;
      continue;
    }

    if (RULE_PATTERN.test(line)) {
      flushAll();
      blocks.push({ type: 'rule' });
      index += 1;
      continue;
    }

    const unordered = line.match(UNORDERED_PATTERN);
    const ordered = line.match(ORDERED_PATTERN);
    if (unordered || ordered) {
      const nextType = ordered ? 'ordered-list' : 'unordered-list';
      flushParagraph();
      if (list && list.type !== nextType) flushList();
      if (!list) list = { type: nextType, items: [] };
      list.items.push((unordered || ordered)[1]);
      index += 1;
      continue;
    }

    // An indented line directly under a list item continues that item.
    if (list && leadingSpaces(rawLine) > 0 && paragraph.length === 0) {
      list.items[list.items.length - 1] += ` ${line}`;
      index += 1;
      continue;
    }

    flushList();
    paragraph.push(line);
    index += 1;
  }

  flushAll();
  return blocks;
}

export function slugifyHeading(value, usedIds) {
  const base = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'section';
  const count = usedIds.get(base) || 0;
  usedIds.set(base, count + 1);
  return count === 0 ? base : `${base}-${count + 1}`;
}

/**
 * Splits a chapter body into `## ` sections (ids such as `concepts-covered`,
 * `practice-loop`) and parses each section's body into blocks. `# ` titles are
 * dropped because the reader renders the chapter title itself. Headings inside
 * fenced code never start a section.
 */
export function buildContentSections(contentBody) {
  const fallback = 'This chapter is being prepared. Return to the pathway for the latest learning outline.';
  const lines = (contentBody || fallback).replace(/\r\n?/g, '\n').split('\n');
  const usedIds = new Map([['introduction', 1]]);
  const rawSections = [{ id: 'introduction', title: 'Introduction', lines: [] }];
  let current = rawSections[0];
  let openFence = null;

  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    const fence = line.match(FENCE_PATTERN);

    if (openFence) {
      if (line.startsWith(openFence.repeat(3)) && line.replace(/[`~]/g, '') === '') openFence = null;
      current.lines.push(rawLine);
      return;
    }
    if (fence) {
      openFence = fence[1][0];
      current.lines.push(rawLine);
      return;
    }
    if (/^#\s+/.test(line)) return;
    if (/^##\s+/.test(line)) {
      const title = line.replace(/^##\s+/, '').trim();
      current = { id: slugifyHeading(title, usedIds), title, lines: [] };
      rawSections.push(current);
      return;
    }
    current.lines.push(rawLine);
  });

  return rawSections
    .map((section) => ({ id: section.id, title: section.title, blocks: parseMarkdownBlocks(section.lines.join('\n')) }))
    .filter((section) => section.blocks.length > 0);
}
