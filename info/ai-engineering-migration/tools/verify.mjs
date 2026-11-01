// Checks that every piece of learner text in an original page survives in the converted output.
// Usage: node verify.mjs <siteRoot> <relPage> <corpusFile...>  (corpus files: converted json and/or markdown/json files)
// Prints coverage and every missing text run (HTML text nodes and JS string literals).
import * as cheerio from 'cheerio';
import fs from 'fs';
import path from 'path';

const [siteRoot, relPage, ...corpusFiles] = process.argv.slice(2);
const verbose = process.env.VERBOSE === '1';
const $ = cheerio.load(fs.readFileSync(path.join(siteRoot, relPage), 'utf8'));

const norm = (s) => s
  .replace(/&[a-z]+;/g, ' ')
  .replace(/\\[nrt]/g, ' ')
  .replace(/[*_`#>|\\\[\]()“”"'’‘·•↳—–\-…:,.;!?{}]/g, ' ')
  .toLowerCase()
  .replace(/\s+/g, ' ')
  .trim();

// corpus
let corpus = '';
for (const f of corpusFiles) {
  const raw = fs.readFileSync(f, 'utf8');
  if (f.endsWith('.json')) {
    // only SVG markup is stripped of tags: prose and code legitimately contain < and >
    const walk = (v, key) => {
      if (typeof v === 'string') corpus += ' ' + (key === 'svg' || key === 'svgContent' ? v.replace(/<[^>]+>/g, ' ') : v);
      else if (v && typeof v === 'object') Object.entries(v).forEach(([k, x]) => { if (k !== 'skipped') walk(x, k); });
    };
    walk(JSON.parse(raw));
  } else corpus += ' ' + raw;
}
// decode entities that survive inside svg markup
corpus = corpus.replace(/&(amp|lt|gt|quot|#39|apos|nbsp);/g, (m, e) => ({ amp: '&', lt: '<', gt: '>', quot: '"', '#39': "'", apos: "'", nbsp: ' ' }[e]))
  .replace(/&#(\d+);/g, (m, d) => String.fromCodePoint(Number(d)));
const C = ' ' + norm(corpus) + ' ';

// HTML text runs: text of each leaf-ish block (keeps runs short enough to locate)
const runs = [];
$('script, style, noscript').remove();
$('nav, .aiseq, [class*="sitebar"], [aria-hidden="true"]').remove();
// each text node on its own (a node is never split by markup), plus every element's
// full text for short inline elements such as code, bold terms and buttons
$('body *').each((_, el) => {
  $(el).contents().filter((_, n) => n.type === 'text').each((_, n) => {
    const t = n.data.replace(/\s+/g, ' ').trim();
    if (t.split(' ').length >= 3) runs.push({ kind: 'html', text: t });
  });
});
// JS string literals that read like prose
const html2 = fs.readFileSync(path.join(siteRoot, relPage), 'utf8');
const $2 = cheerio.load(html2);
$2('script:not([src])').each((_, s) => {
  const js = $2(s).html();
  const re = /(["'`])((?:\\.|(?!\1)[^\\])*?)\1/gs; let m;
  while ((m = re.exec(js))) {
    const t = m[2];
    if (t.length > 24 && /\s\w+\s\w+/.test(t) && !/^[\s<>=\/.#\w-]*$/.test(t) && !/querySelector|addEventListener|classList|getElementById|innerHTML|function\s*\(|=>/.test(t)) {
      t.split(/<[^>]+>|\$\{[^}]*\}/).map((x) => x.replace(/\\n/g, ' ').trim()).filter((x) => x.split(/\s+/).length >= 4).forEach((x) => runs.push({ kind: 'js', text: x }));
    }
  }
});

let total = 0, missing = 0; const misses = [];
const seen = new Set();
for (const r of runs) {
  const n = norm(r.text);
  if (!n || n.split(' ').length < 3 || seen.has(n)) continue;
  // UI chrome that the reader replaces with its own controls
  if (/^(swipe sideways|check your understanding|scroll sideways)/.test(n) || /^pseudo code\b/.test(n)) continue;
  seen.add(n);
  total += n.length;
  if (C.includes(' ' + n + ' ') || C.includes(n)) continue;
  // tolerate runs split by markup: accept if every 6-word window is present
  const w = n.split(' ');
  let ok = true;
  for (let i = 0; i + 6 <= w.length; i += 3) if (!C.includes(w.slice(i, i + 6).join(' '))) { ok = false; break; }
  if (ok && w.length >= 6) continue;
  missing += n.length; misses.push(`[${r.kind}] ${r.text.slice(0, 220)}`);
}
console.log(`${relPage}: coverage ${(100 * (1 - missing / Math.max(total, 1))).toFixed(1)}%  missing ${misses.length} runs / ${missing} chars`);
if (verbose) misses.forEach((m) => console.log('  - ' + m));
