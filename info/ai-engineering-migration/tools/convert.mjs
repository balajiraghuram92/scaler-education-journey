// Converts one github.io lesson page into an intermediate JSON:
// { title, sections: [{ title, md }], diagrams: [{ key, title, caption, svg, alt }], mcqs: [...], skipped: [...] }
// Usage: node convert.mjs <siteRoot> <relPage> <keyPrefix> <outJson>
import * as cheerio from 'cheerio';
import postcss from 'postcss';
import fs from 'fs';
import path from 'path';

const [siteRoot, relPage, keyPrefix, outJson] = process.argv.slice(2);
const pagePath = path.join(siteRoot, relPage);
const html = fs.readFileSync(pagePath, 'utf8');
const $ = cheerio.load(html, { decodeEntities: true });

// ---------- CSS collection (for diagram style inlining) ----------
let cssText = '';
$('link[rel=stylesheet]').each((_, l) => {
  const href = $(l).attr('href');
  if (!href || /^https?:/.test(href)) return;
  const p = path.join(path.dirname(pagePath), href);
  if (fs.existsSync(p)) cssText += '\n' + fs.readFileSync(p, 'utf8');
});
$('style').each((_, s) => { cssText += '\n' + $(s).html(); });
const rootVars = {};
const styleRules = [];
try {
  const ast = postcss.parse(cssText);
  ast.walkRules((rule) => {
    const parent = rule.parent;
    if (parent && parent.type === 'atrule') {
      // keep plain (non-dark, non-print) media rules out; screen-size rules are skipped too
      return;
    }
    const decls = [];
    rule.walkDecls((d) => decls.push([d.prop, d.value]));
    for (const sel of rule.selectors) {
      if (/^(:root|html|body)$/.test(sel.trim()) || /^:root/.test(sel.trim())) {
        for (const [p, v] of decls) if (p.startsWith('--') && !(p in rootVars)) rootVars[p] = v;
        // later :root definitions (theme overrides under [data-theme]) are ignored by the guard above
        continue;
      }
      if (/\[data-theme|\.dark|prefers-color/.test(sel)) continue;
      if (/:(hover|focus|active|focus-visible|focus-within|checked|disabled)|::|:not\(|:has\(|\.(on|active|sel|lit|dim|show|open)(?![\w-])|\.is-/.test(sel)) continue;
      styleRules.push({ sel: sel.trim(), decls });
    }
  });
} catch (e) { console.error('CSS parse failed', e.message); }

function resolveVars(value, depth = 0) {
  if (depth > 8) return value;
  return value.replace(/var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)/g, (m, name, fb) => {
    const v = rootVars[name] ?? fb;
    return v ? resolveVars(v, depth + 1) : m;
  });
}

const SVG_CASE = ['viewBox', 'refX', 'refY', 'markerWidth', 'markerHeight', 'markerUnits', 'preserveAspectRatio', 'gradientUnits', 'gradientTransform', 'patternUnits', 'textLength', 'lengthAdjust', 'stdDeviation'];
const SVG_PROPS =new Set(['fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin', 'opacity', 'fill-opacity', 'stroke-opacity', 'font-size', 'font-weight', 'font-family', 'font-style', 'letter-spacing', 'text-anchor', 'dominant-baseline', 'paint-order', 'text-transform', 'marker-end', 'marker-start']);

function fontMap(v) {
  if (/mono|code|courier/i.test(v)) return "'JetBrains Mono', monospace";
  if (/serif/i.test(v) && !/sans/i.test(v)) return "'Newsreader', Georgia, serif";
  return "'Plus Jakarta Sans', sans-serif";
}

// ---------- diagrams ----------
const diagrams = [];
const usedKeys = new Set();
function diagramKey(base) {
  let k = `${keyPrefix}-${base}`.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
  let i = 2, key = k;
  while (usedKeys.has(key)) key = `${k}-${i++}`;
  usedKeys.add(key);
  return key;
}

function serializeDiagram(svgEl) {
  // inline computed styles from page CSS (source order, element style wins)
  const styleMap = new Map();
  for (const { sel, decls } of styleRules) {
    let matched;
    try { matched = $(sel); } catch { continue; }
    matched.each((_, el) => {
      if (el !== svgEl && !$(svgEl).find(el).length) return;
      const m = styleMap.get(el) || {};
      for (const [p, v] of decls) if (SVG_PROPS.has(p) || p === 'display' || p === 'visibility') m[p] = v;
      styleMap.set(el, m);
    });
  }
  const clone = $(svgEl).clone();
  // map styles onto clone by walking both trees in parallel
  const orig = [svgEl, ...$(svgEl).find('*').get()];
  const copy = [clone.get(0), ...clone.find('*').get()];
  orig.forEach((o, i) => {
    const c = copy[i];
    const computed = styleMap.get(o) || {};
    const own = ($(o).attr('style') || '').split(';').map((s) => s.trim()).filter(Boolean)
      .map((s) => [s.slice(0, s.indexOf(':')).trim(), s.slice(s.indexOf(':') + 1).trim()]);
    const merged = { ...computed };
    for (const [p, v] of own) merged[p] = v;
    for (const attr of ['fill', 'stroke', 'font-family']) {
      const a = $(c).attr(attr);
      if (a && /var\(/.test(a)) $(c).attr(attr, resolveVars(a));
    }
    const decl = Object.entries(merged)
      .map(([p, v]) => [p, p === 'font-family' ? fontMap(resolveVars(v)) : resolveVars(v)])
      .filter(([, v]) => !/var\(/.test(v))
      .map(([p, v]) => `${p}:${v}`).join(';');
    if (decl) $(c).attr('style', decl); else $(c).removeAttr('style');
    $(c).removeAttr('tabindex').removeAttr('role').removeAttr('data-stage');
  });
  // bring in referenced markers / gradients / symbols from elsewhere in the page
  const serialized0 = $.html(clone);
  const refs = new Set([...serialized0.matchAll(/url\(#([\w-]+)\)|href="#([\w-]+)"/g)].map((m) => m[1] || m[2]));
  const extra = [];
  for (const id of refs) {
    if (clone.find(`[id="${id}"]`).length) continue;
    const def = $(`[id="${id}"]`).first();
    if (!def.length) continue;
    const dc = def.clone();
    dc.find('*').addBack().each((_, el) => {
      for (const attr of ['fill', 'stroke']) { const a = $(el).attr(attr); if (a && /var\(/.test(a)) $(el).attr(attr, resolveVars(a)); }
      const st = $(el).attr('style'); if (st) $(el).attr('style', resolveVars(st));
      // marker paths often take their colour from a class
      const m = {}; for (const { sel, decls } of styleRules) { try { if ($(el).is(sel)) for (const [p, v] of decls) if (SVG_PROPS.has(p)) m[p] = resolveVars(v); } catch {} }
      const d = Object.entries(m).map(([p, v]) => `${p}:${v}`).join(';'); if (d && !$(el).attr('style')) $(el).attr('style', d);
    });
    extra.push($.html(dc));
  }
  if (extra.length) {
    let defs = clone.children('defs').first();
    if (!defs.length) { clone.prepend('<defs></defs>'); defs = clone.children('defs').first(); }
    defs.append(extra.join(''));
  }
  clone.removeAttr('id').removeAttr('width').removeAttr('height');
  clone.attr('xmlns', 'http://www.w3.org/2000/svg');
  clone.attr('style', 'max-width:100%;height:auto' + (clone.attr('style') ? ';' + clone.attr('style') : ''));
  let out = $.html(clone).replace(/\s+\n/g, '\n');
  for (const a of SVG_CASE) out = out.replace(new RegExp(` ${a.toLowerCase()}=`, 'g'), ` ${a}=`);
  return out;
}

function svgText(svgEl) {
  const parts = [];
  $(svgEl).find('text').each((_, t) => { const s = $(t).text().replace(/\s+/g, ' ').trim(); if (s) parts.push(s); });
  return parts;
}

function addDiagram(svgEl, caption, titleHint) {
  const aria = ($(svgEl).attr('aria-label') || $(svgEl).find('title').first().text() || '').replace(/\s+/g, ' ').trim();
  const title = (titleHint || aria || caption || 'Diagram').replace(/\s+/g, ' ').trim();
  const key = diagramKey((titleHint || aria || 'diagram').split(/[.:,]/)[0].split(' ').slice(0, 6).join(' '));
  diagrams.push({
    key,
    title: title.length > 190 ? title.slice(0, 187) + '...' : title,
    caption: caption || '',
    alt: aria,
    labels: svgText(svgEl),
    svg: serializeDiagram(svgEl)
  });
  return key;
}

// ---------- MCQs ----------
const mcqs = [];
function inlineHtmlToMd(el) { return inline(el).replace(/\s+/g, ' ').trim(); }
function convertQuiz(quiz) {
  $(quiz).find('.lk-q').each((qi, q) => {
    const stem = inlineHtmlToMd($(q).find('.lk-stem').first());
    const opts = [];
    let why = [];
    $(q).find('.lk-opts > li').each((oi, li) => {
      const w = $(li).find('.lk-why').first();
      const whyText = w.length ? inlineHtmlToMd(w) : '';
      const liClone = $(li).clone(); liClone.find('.lk-why').remove();
      const key = String.fromCharCode(97 + oi);
      opts.push({ optionKey: key, optionText: inlineHtmlToMd(liClone), isCorrect: $(li).is('[data-correct]') });
      if (whyText) why.push({ key, correct: $(li).is('[data-correct]'), text: whyText });
    });
    // Explanation: the correct option's reasoning first, then why each other option is wrong.
    const correct = why.filter((w) => w.correct).map((w) => w.text);
    const others = why.filter((w) => !w.correct).map((w) => `(${w.key.toUpperCase()}) ${w.text}`);
    mcqs.push({ questionText: stem, explanation: [...correct, ...others].join('\n\n'), options: opts });
  });
}

// ---------- inline conversion ----------
const SKIP_INLINE = new Set(['script', 'style', 'noscript', 'template']);
function linkFor(href) {
  if (!href) return null;
  if (/^(https?:|mailto:)/.test(href)) return href;
  if (href.startsWith('#')) return null;
  const abs = path.posix.normalize(path.posix.join(path.posix.dirname(relPage.replace(/\\/g, '/')), href.split('#')[0]));
  const k = abs.replace(/\/?index\.html$/, '').replace(/\/$/, '');
  if (/\.zip$/.test(k)) return '/downloads/ai-engineering/' + path.posix.basename(k);
  return `@@page:${k}${href.includes('#') ? '#' + href.split('#')[1] : ''}@@`;
}
function escInline(s) { return s.replace(/\r?\n/g, ' '); }
function inline(el) {
  let out = '';
  let prevTag = false;
  $(el).contents().each((_, n) => {
    const piece = inlineNode(n);
    // Elements laid out as separate boxes by CSS (a number badge and its label, a term
    // and its definition) have no whitespace between them in the source.
    if (piece && out && (prevTag || n.type === 'tag') && /[\w*`)]$/.test(out) && /^[\w*`(“]/.test(piece)) out += ' ';
    out += piece;
    if (n.type === 'tag' || (n.type === 'text' && n.data.trim())) prevTag = n.type === 'tag';
  });
  return out;
}
const DROP_CLASSES = /\b(scroll-hint|sec-num|sr-only|visually-hidden|lk-hide|lk-show)\b/;
function inlineNode(n) {
  if (n.type === 'text') return escInline(n.data);
  if (n.type !== 'tag') return '';
  const tag = n.tagName; const $n = $(n); const cls = $n.attr('class') || '';
  if (SKIP_INLINE.has(tag) || DROP_CLASSES.test(cls)) return '';
  if (tag === 'br') return ' ';
  if (tag === 'svg') return ''; // icons; real diagrams are handled at block level
  if (tag === 'button' && /\b(copy|copybtn|icon-btn)\b/.test(cls)) return '';
  if (tag === 'input' || tag === 'textarea') { const v = $n.attr('value') || $n.attr('placeholder'); return v ? ` ${v} ` : ''; }
  if (tag === 'select') { const o = $n.find('option').map((_, x) => $(x).text().trim()).get(); return o.length ? ` (${o.join(' / ')}) ` : ''; }
  const inner = inline(n);
  const t = inner.replace(/\s+/g, ' ');
  if (!t.trim()) return t;
  if (tag === 'code' || tag === 'kbd' || tag === 'samp') {
    const raw = $n.text().replace(/\s+/g, ' ');
    return raw.includes('`') ? '`` ' + raw + ' ``' : '`' + raw + '`';
  }
  if (tag === 'b' || tag === 'strong' || (tag === 'button' && /\bkw\b/.test(cls))) return wrap(t, '**');
  if (tag === 'em' || tag === 'i' || tag === 'cite') return wrap(t, '*');
  if (tag === 'a') { const href = linkFor($n.attr('href')); return href ? `[${t.trim()}](${href})` : t; }
  if (tag === 'q') return `“${t}”`;
  if (/^h[1-6]$/.test(tag)) return ` ${wrap(t, '**')} `;
  return inner;
}
function wrap(t, m) {
  const lead = t.match(/^\s*/)[0], trail = t.match(/\s*$/)[0], core = t.trim();
  if (!core) return t;
  if (core.includes(m)) return t;
  return `${lead}${m}${core}${m}${trail}`;
}

// ---------- block conversion ----------
const BLOCK_TAGS = new Set(['p', 'div', 'section', 'article', 'main', 'header', 'footer', 'aside', 'nav', 'ul', 'ol', 'li', 'table', 'pre', 'figure', 'figcaption', 'details', 'summary', 'dl', 'dt', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'hr', 'svg', 'form', 'fieldset', 'label', 'thead', 'tbody', 'tr', 'td', 'th']);
const skipped = [];

function hasBlockChild(el) {
  return $(el).children().toArray().some((c) => BLOCK_TAGS.has(c.tagName) && !(c.tagName === 'svg' && isIcon(c)));
}
function isIcon(svg) {
  const vb = ($(svg).attr('viewBox') || '').split(/\s+/).map(Number);
  const w = vb[2] || Number($(svg).attr('width')) || 0;
  return w > 0 && w <= 64 || $(svg).attr('aria-hidden') === 'true' && $(svg).find('text').length === 0;
}
function para(text) { const t = text.replace(/[ \t]+/g, ' ').trim(); return t ? [t] : []; }
function fence(lang, text, attrs = '') {
  const body = text.replace(/^\n+|\s+$/g, '');
  const ticks = body.includes('```') ? '````' : '```';
  return `${ticks}${lang}${attrs ? ' ' + attrs : ''}\n${body}\n${ticks}`;
}
function langOf(el) {
  const c = ($(el).attr('class') || '') + ' ' + ($(el).find('code').attr('class') || '');
  const m = c.match(/(?:lang|language)-([\w+-]+)/);
  if (!m) return '';
  return { py: 'python', sh: 'bash', shell: 'bash', js: 'javascript', yml: 'yaml', none: 'text' }[m[1]] || m[1];
}
function quoteAttr(s) { return '"' + s.replace(/"/g, "'").replace(/\s+/g, ' ').trim() + '"'; }

function headingLevel(tag) { return Number(tag.slice(1)); }

// Section tracking: h2 starts a new section; content before the first h2 is "Overview".
const sections = [{ title: '', md: [] }];
function emit(blocks) { sections[sections.length - 1].md.push(...blocks); }

function codeBox(el, titleOverride) {
  // div.code / div.codeblock / div.file: a bar with a filename, then a pre
  const pre = $(el).find('pre').first();
  if (!pre.length) return null;
  const title = titleOverride || $(el).find('.file, .file-bar, .cb-head, .code-bar, .bar, .head').first().clone().find('button').remove().end().text().replace(/\s+/g, ' ').trim();
  return fence(langOf(pre) || 'text', pre.text(), title ? `title=${quoteAttr(title)}` : '');
}

function blocks(el) {
  const out = [];
  let run = '';
  const flush = () => { if (run.trim()) out.push(...para(run)); run = ''; };
  $(el).contents().each((_, n) => {
    if (n.type === 'text') {
      const t = escInline(n.data);
      // "<b>Ticker</b>A stock's short code": the term and its text are separate boxes
      if (/\*\*$/.test(run) && /^[\w(“]/.test(t)) run += ' ';
      run += t;
      return;
    }
    if (n.type !== 'tag') return;
    const tag = n.tagName; const $n = $(n); const cls = $n.attr('class') || '';
    if (SKIP_INLINE.has(tag)) return;
    if (tag === 'svg') {
      if (isIcon(n) || $n.attr('width') === '0') return;
      flush();
      const key = addDiagram(n, '', '');
      out.push(`{{diagram:${key}}}`);
      return;
    }
    if (!BLOCK_TAGS.has(tag) && !hasBlockChild(n)) {
      if (tag === 'button' && !/\bkw\b/.test(cls)) {
        const t = $n.text().replace(/\s+/g, ' ').trim();
        // Buttons that carry real content (flashcards, answer cards, long choices) are kept
        // as their own paragraph; short control labels are dropped.
        if (t.split(' ').length >= 5) {
          flush();
          out.push(...para(inline(n)));
          return;
        }
        if (t && !/^(copy|copied|view code|hide code|try again|reset|run|play|next|prev|previous|back|close|×|✕)$/i.test(t)) skipped.push(`button: ${t}`);
        return;
      }
      const piece = inlineNode(n);
      if (piece && /[\w*`)]$/.test(run) && /^[\w*`(“]/.test(piece)) run += ' ';
      run += piece;
      return;
    }
    flush();
    out.push(...blockEl(n));
  });
  flush();
  return out;
}

function blockEl(n) {
  const tag = n.tagName; const $n = $(n); const cls = $n.attr('class') || '';
  if ($n.attr('hidden') !== undefined && !/lk-/.test(cls)) { /* hidden panels still carry text */ }
  if (DROP_CLASSES.test(cls)) return [];
  // Lesson navigation bars: the reader has its own navigation, so keep only their
  // recordings and project files (from the top bar; the bottom bar repeats it).
  if (/\b(awsq|aiseq|aq)\b/.test(cls) || $n.is('nav.awsq, div.aiseq, nav.aq')) {
    if (/bottom/.test(cls)) return [];
    const recs = $n.find('a[class$="-rec"]').map((_, a) => `- [${inline($(a).clone().find('small').remove().end()).replace(/\s+/g, ' ').replace(/^\*▶\*\s*/, '').trim()}](${$(a).attr('href')})`).get();
    const files = $n.find('[class$="-fb"]').map((_, a) => {
      const label = $(a).clone().find('small').remove().end().text().replace(/\s+/g, ' ').trim();
      const href = $(a).attr('href');
      return href ? `- [${label}](${linkFor(href)})` : `- ${label} (${$(a).find('small').text().trim()})`;
    }).get();
    const cap = $n.find('[class$="-cap"]').first().text().replace(/\s+/g, ' ').trim();
    const lines = [`**Lesson resources${cap ? ' · ' + cap : ''}:**`, ...recs, ...files];
    return [lines.map((l) => `> ${l}`).join('\n')];
  }
  if (tag === 'nav') {
    // tables of contents and site bars duplicate the reader's own navigation
    skipped.push(`nav: ${$n.text().replace(/\s+/g, ' ').trim().slice(0, 120)}`);
    return [];
  }
  if (/^h[1-6]$/.test(tag)) {
    const text = inline(n).replace(/\s+/g, ' ').trim();
    if (!text) return [];
    const lvl = headingLevel(tag);
    if (lvl === 1) { pageTitleCandidates.push(text); return [`#### ${text}`]; }
    if (lvl === 2) {
      const num = $n.closest('section').find('.sec-num').first().text().trim();
      return [`@@SECTION:${num && !text.startsWith(num) ? `${num} ${text}` : text}`];
    }
    return [`${'#'.repeat(Math.min(lvl + 1, 5))} ${text}`];
  }
  if (tag === 'hr') return ['---'];
  if (tag === 'pre') return [fence(langOf(n) || 'text', $n.text())];
  if (tag === 'table') return table(n);
  if (tag === 'ul' || tag === 'ol') return list(n, tag === 'ol');
  if (tag === 'dl') {
    const items = [];
    $n.children('dt').each((_, dt) => {
      const dd = $(dt).nextUntil('dt', 'dd').map((_, d) => inline(d).replace(/\s+/g, ' ').trim()).get().join(' ');
      items.push(`- **${inline(dt).replace(/\s+/g, ' ').trim()}**${dd ? ' — ' + dd : ''}`);
    });
    return [items.join('\n')];
  }
  if (/\blk-quiz\b/.test(cls)) {
    // the marker records where the quiz sat, so its questions follow the right chapter
    const first = mcqs.length; convertQuiz(n);
    return mcqs.length > first ? [`@@QUIZ:${first}-${mcqs.length}@@`] : [];
  }
  if (/\blk-code\b/.test(cls)) return lkCode(n);
  if (tag === 'div' && /\b(code|codeblock|file)\b/.test(cls) && $n.children('pre').length + $n.find('> div > pre').length > 0 && !$n.find('.lk-code').length) {
    const c = codeBox(n); return c ? [c] : [];
  }
  if (tag === 'figure') {
    const svgs = $n.find('svg').toArray().filter((s) => !isIcon(s));
    const cap = $n.find('figcaption').first();
    const capText = cap.length ? inline(cap).replace(/\s+/g, ' ').trim() : '';
    if (svgs.length) {
      const out = [];
      svgs.forEach((s, i) => out.push(`{{diagram:${addDiagram(s, i === svgs.length - 1 ? capText : '', capText.split(/[.:]/)[0])}}}`));
      // anything else inside the figure (legends, notes) is kept as text
      const rest = $n.clone(); rest.find('svg, figcaption, .scroll-hint').remove();
      const restBlocks = blocks(rest.get(0));
      if (capText) out.push(`*${capText.replace(/\*/g, '')}*`);
      return [...out, ...restBlocks];
    }
    const out = blocks(n);
    return out;
  }
  if (tag === 'details') {
    const sum = $n.children('summary').first();
    const sumText = sum.length ? inline(sum).replace(/\s+/g, ' ').trim() : '';
    const body = $n.clone(); body.children('summary').remove();
    return [...(sumText ? [`#### ${sumText}`] : []), ...blocks(body.get(0))];
  }
  if (tag === 'blockquote' || /\b(callout|note|analogy|tip|warn|warning|aside-note|insight|pill-note|key|takeaway)\b/.test(cls) && tag !== 'span') {
    const head = $n.children('h4,h5,h6,.callout-title,.label').first();
    let label = head.length ? head.clone().find('.ico').remove().end().text().replace(/[✦★•]/g, '').replace(/\s+/g, ' ').trim() : '';
    const body = $n.clone(); if (head.length) body.children().first().filter((_, x) => x === body.children('h4,h5,h6,.callout-title,.label').get(0)).remove();
    body.children('h4,h5,h6,.callout-title,.label').first().remove();
    const inner = blocks(body.get(0));
    if (!inner.length && !label) return [];
    // a short first line ("🧠 Analogy — the report-card meeting") is the callout's own title
    if (!label && inner.length > 1 && inner[0].length < 90 && !/[.!?:]$/.test(inner[0].replace(/\*+$/, '')) && !/^[>#|`{-]/.test(inner[0])) {
      label = inner.shift().replace(/\*\*/g, '').trim();
    }
    if (!label) label = /analogy/.test(cls) ? 'Analogy' : /warn/.test(cls) ? 'Watch out' : 'Note';
    const lines = [`**${label}:**`, ...inner.flatMap((b, i) => (i ? ['', ...b.split('\n')] : b.split('\n')))];
    return [lines.map((l) => (l ? `> ${l}` : '>')).join('\n')];
  }
  return blocks(n);
}

const pageTitleCandidates = [];

function table(n) {
  const rows = [];
  $(n).find('tr').each((_, tr) => {
    const cells = $(tr).children('th,td').map((_, c) => {
      const t = blockishInline(c).replace(/\|/g, '\\|');
      const span = Number($(c).attr('colspan') || 1);
      return Array(span).fill(0).map((__, i) => (i ? '' : t));
    }).get().flat();
    rows.push(cells);
  });
  if (!rows.length) return [];
  const width = Math.max(...rows.map((r) => r.length));
  rows.forEach((r) => { while (r.length < width) r.push(''); });
  const hasHead = $(n).find('thead').length || $(n).find('tr').first().children('th').length === $(n).find('tr').first().children().length;
  const head = hasHead ? rows.shift() : Array(width).fill('');
  const cap = $(n).find('caption').first();
  const lines = [`| ${head.join(' | ')} |`, `| ${head.map(() => '---').join(' | ')} |`, ...rows.map((r) => `| ${r.join(' | ')} |`)];
  return [...(cap.length ? [`**${inline(cap).trim()}**`] : []), lines.join('\n')];
}

// Inline rendering of an element that may contain blocks (table cells, list items)
function blockishInline(el) {
  const parts = [];
  const $e = $(el);
  if (!hasBlockChild(el)) return inline(el).replace(/\s+/g, ' ').trim();
  $e.contents().each((_, n) => {
    if (n.type === 'text') { parts.push(n.data); return; }
    if (n.type !== 'tag') return;
    if (n.tagName === 'pre') { parts.push('`' + $(n).text().replace(/\s+/g, ' ').trim() + '`'); return; }
    if (n.tagName === 'ul' || n.tagName === 'ol') { parts.push($(n).children('li').map((i, li) => (n.tagName === 'ol' ? `(${i + 1}) ` : '• ') + blockishInline(li)).get().join(' ')); return; }
    parts.push(BLOCK_TAGS.has(n.tagName) || hasBlockChild(n) ? ' ' + blockishInline(n) + ' ' : inline(n));
  });
  return parts.join('').replace(/\s+/g, ' ').trim();
}

function list(n, ordered) {
  const items = [];
  const extras = [];
  $(n).children('li').each((i, li) => {
    const $li = $(li);
    // code blocks / diagrams / tables inside list items are lifted out after the item
    const clone = $li.clone();
    const nested = [];
    clone.children('ul,ol').each((_, sub) => { nested.push(sub); });
    clone.children('ul,ol').remove();
    const heavy = clone.find('pre, table, .lk-code, figure').toArray();
    const lifted = [];
    heavy.forEach((h) => { lifted.push(...blockEl(h)); $(h).remove(); });
    const text = blockishInline(clone.get(0));
    const bullet = ordered ? `${i + 1}. ` : '- ';
    if (text) items.push(bullet + text);
    nested.forEach((sub) => {
      $(sub).children('li').each((j, sli) => {
        const st = blockishInline(sli);
        if (st) items.push(`${ordered ? `${i + 1}.${j + 1}` : '-'}${ordered ? '. ' : ' '}↳ ${st}`.replace(/^(\d+\.\d+)\. /, '- $1 '));
      });
    });
    if (lifted.length) { if (items.length) { extras.push(items.splice(0).join('\n')); } extras.push(...lifted); }
  });
  if (items.length) extras.push(items.join('\n'));
  return extras;
}

function lkCode(n) {
  const out = [];
  const $n = $(n);
  $n.children().each((_, c) => {
    const $c = $(c); const cls = $c.attr('class') || '';
    if (/lk-pseudo/.test(cls)) {
      const label = $c.find('.lk-label').first().text().replace(/\s+/g, ' ').trim();
      const title = label.replace(/^Pseudo code\s*·?\s*/i, '');
      out.push(fence('pseudo', $c.find('pre').first().text(), title ? `title=${quoteAttr(title)}` : ''));
    } else if (/lk-imports/.test(cls)) {
      const items = $c.find('li').map((_, li) => '- ' + inline(li).replace(/\s+/g, ' ').trim()).get();
      out.push(['**Imported:**', ...items].map((l) => `> ${l}`).join('\n'));
    } else if (c.tagName === 'details') {
      const box = $c.find('.code, .codeblock, .file').first();
      const pre = $c.find('pre').first();
      if (!pre.length) { out.push(...blocks(c)); return; }
      const title = box.length ? box.find('.file, .file-bar, .bar, .cb-head, .code-bar, .head').first().clone().find('button').remove().end().text().replace(/\s+/g, ' ').trim() : '';
      out.push(fence(langOf(pre) || 'python', pre.text(), `reveal${title ? ` title=${quoteAttr(title)}` : ''}`));
      // anything after the code inside the details
      const rest = $c.clone(); rest.children('summary').remove(); rest.find('.code, .codeblock, .file, pre').remove();
      out.push(...blocks(rest.get(0)));
    } else {
      out.push(...blockEl(c));
    }
  });
  return out;
}

// ---------- run ----------
const body = $('body');
// the leading hidden sprite svg holds shared markers; keep it in the DOM for lookups but never emit it
body.children('svg').each((_, s) => { if (/position:\s*absolute|width="0"/.test($.html(s).slice(0, 200))) $(s).attr('width', '0'); });
for (const b of blocks(body.get(0))) {
  const m = b.match(/^@@SECTION:(.*)$/);
  if (m) sections.push({ title: m[1], md: [] }); else emit([b]);
}

const title = $('title').text().replace(/\s+/g, ' ').trim();
const result = {
  page: relPage,
  title,
  // section titles render as plain text in the reader, so emphasis markers are dropped
  sections: sections.map((s) => ({ title: s.title.replace(/\*\*?|`/g, '').replace(/\s+/g, ' ').trim(), md: s.md.join('\n\n') })).filter((s) => s.md.trim() || s.title),
  diagrams,
  mcqs,
  skipped
};
fs.writeFileSync(outJson, JSON.stringify(result, null, 2));
const words = result.sections.reduce((a, s) => a + s.md.split(/\s+/).length, 0);
console.log(`${relPage}: ${result.sections.length} sections, ${words} words, ${diagrams.length} diagrams, ${mcqs.length} mcqs, ${skipped.length} skipped buttons`);
