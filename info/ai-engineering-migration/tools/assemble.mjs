// Builds api/Data/Content/<folder>/ from converter output + agent supplements.
// Usage: node assemble.mjs <repoContentDir> [--report]
import fs from 'fs';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1'));
const outDir = process.argv[2];
const structure = JSON.parse(fs.readFileSync(path.join(here, 'structure.json'), 'utf8'));
const problems = [];

const TARGET_WORDS = 1800;   // close a chapter once it reaches this
const MAX_WORDS = 4200;      // never grow a chapter past this by adding a section
const TINY_PAGE = 150;       // pages this small merge into the previous chapter

const words = (s) => s.replace(/```[\s\S]*?```/g, ' code ').split(/\s+/).filter(Boolean).length;
const slugify = (s) => s.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70).replace(/-+$/, '');
const cleanTitle = (t) => t.replace(/^[^\p{L}\p{N}]+/u, '').replace(/^(\d+(\.\d+)*|[A-Z]–[A-Z])\s+(?=\S)/, '').trim();

function loadPage(key) {
  const page = JSON.parse(fs.readFileSync(path.join(here, 'out', `${key}.json`), 'utf8'));
  const suppPath = path.join(here, 'supplements', `${key}.json`);
  const supp = fs.existsSync(suppPath) ? JSON.parse(fs.readFileSync(suppPath, 'utf8')) : { inserts: [], glossary: [] };
  // apply inserts in reverse file order per anchor so several inserts after one anchor keep their order
  const allMd = page.sections.map((s) => s.md).join('\n');
  for (const ins of supp.inserts || []) {
    // a bare bold label that the converter now carries as a code block's title is not repeated
    const label = ins.md.trim().match(/^\*\*([^*]+)\*\*$/);
    if (label && allMd.includes(`title="${label[1].replace(/"/g, "'").trim()}"`)) continue;
    const sec = page.sections.find((s) => s.title === ins.section) ?? page.sections.find((s) => s.title.trim() === (ins.section || '').trim());
    if (!sec) { problems.push(`${key}: insert section not found "${ins.section}" — appended to last section`); page.sections[page.sections.length - 1].md += `\n\n${ins.md}`; continue; }
    if (!ins.after) { sec.md += `\n\n${ins.md}`; continue; }
    const lines = sec.md.split('\n');
    let at = lines.findIndex((l) => l === ins.after);
    if (at < 0) at = lines.findIndex((l) => l.trim() === ins.after.trim());
    if (at < 0) { problems.push(`${key}: anchor not found in "${ins.section}": ${ins.after.slice(0, 80)} — appended to section end`); sec.md += `\n\n${ins.md}`; continue; }
    // never split a fenced block or table: move forward to the end of the block the anchor is in
    let end = at;
    const fenceOpen = lines.slice(0, at + 1).filter((l) => /^(```|~~~)/.test(l.trim())).length % 2 === 1;
    if (fenceOpen) { end = lines.findIndex((l, i) => i > at && /^(```|~~~)/.test(l.trim())); if (end < 0) end = lines.length - 1; }
    while (end + 1 < lines.length && lines[end + 1].trim() && (/^\|/.test(lines[end].trim()) || /^>/.test(lines[end].trim()) || /^(\d+\.|-)\s/.test(lines[end].trim())) && lines[end + 1].trim()[0] === lines[end].trim()[0]) end++;
    lines.splice(end + 1, 0, '', ins.md, '');
    sec.md = lines.join('\n');
  }
  if (supp.glossary?.length) {
    const list = supp.glossary.map((g) => `- **${g.term.replace(/\*\*/g, '')}** — ${g.definition}`).join('\n');
    const gsec = page.sections.find((s) => /glossary/i.test(s.title));
    if (gsec) gsec.md = `${gsec.md}\n\n${list}`;
    else page.sections.push({ title: 'Glossary', md: list });
  }
  for (const s of page.sections) s.md = s.md.replace(/\n{3,}/g, '\n\n').trim();
  return page;
}

// A section far over the chapter budget is split at its #### headings into parts.
function splitLarge(sec) {
  if (words(sec.md) <= MAX_WORDS || !sec.title) return [sec];
  const parts = [[]];
  let inFence = false;
  let w = 0;
  for (const l of sec.md.split('\n')) {
    if (/^(```|~~~)/.test(l.trim())) inFence = !inFence;
    if (!inFence && /^#### /.test(l) && w >= TARGET_WORDS) { parts.push([]); w = 0; }
    parts[parts.length - 1].push(l);
    w += l.split(/\s+/).filter(Boolean).length;
  }
  return parts.map((p, i) => ({ title: i ? `${sec.title} (part ${i + 1})` : sec.title, md: p.join('\n').trim() }));
}

function firstParagraph(md) {
  for (const block of md.split(/\n\n/)) {
    const b = block.trim();
    if (!b || /^(#|>|\||```|-|\d+\.|\{\{|@@|\*[^*])/.test(b)) continue;
    const text = b.replace(/\*\*|`|\*/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/\s+/g, ' ');
    if (text.split(' ').length >= 12) return text.length > 280 ? text.slice(0, 277).replace(/\s+\S*$/, '') + '…' : text;
  }
  return '';
}

const pageFirstChapter = {};   // page key → url
const pageRel = {};            // page rel path (no index.html) → page key
for (const f of fs.readdirSync(path.join(here, 'out')).filter((f) => f.endsWith('.json'))) {
  const p = JSON.parse(fs.readFileSync(path.join(here, 'out', f), 'utf8'));
  pageRel[p.page.replace(/\/?index\.html$/, '').replace(/\.html$/, '')] = f.replace(/\.json$/, '');
}

const allChapters = [];
for (const course of structure.courses) {
  const courseDir = path.join(outDir, course.folder);
  for (const sub of ['lessons', 'diagrams', 'mcqs']) fs.rmSync(path.join(courseDir, sub), { recursive: true, force: true });
  for (const sub of ['lessons', 'diagrams', 'mcqs']) fs.mkdirSync(path.join(courseDir, sub), { recursive: true });
  const manifest = {
    slug: course.slug, title: course.title, description: course.description,
    verticalName: structure.verticalName, verticalDescription: structure.verticalDescription,
    orderIndex: course.orderIndex, modules: []
  };

  // lesson files share one folder per course, so slugs must be unique across the course
  const used = new Set();
  for (const mod of course.modules) {
    const chapters = [];
    let moduleLede = '';
    for (const pref of mod.pages) {
      const page = loadPage(pref.key);
      // the old site had these solution zips but still showed "coming soon"; link them now
      if (pref.zip) {
        for (const s of page.sections) s.md = s.md.replace('> - ⬇ Download all (coming soon)', `> - [⬇ Download all](/downloads/ai-engineering/${pref.zip})`);
      }
      page.sections = page.sections.flatMap(splitLarge);
      const pageWords = page.sections.reduce((a, s) => a + words(s.md), 0);
      const merge = (pref.merge || pageWords < TINY_PAGE) && chapters.length > 0;
      let current = merge ? chapters[chapters.length - 1] : null;
      if (!moduleLede) moduleLede = firstParagraph(page.sections[0]?.md || '');
      let firstOfPage = null;
      page.sections.forEach((sec, i) => {
        const w = words(sec.md);
        const isLead = i === 0 && !sec.title;
        const startNew = !current || (!isLead && !merge && current.words >= TARGET_WORDS) || (!isLead && !merge && current.words + w > MAX_WORDS && current.words >= 600);
        if (startNew && !(merge && current)) {
          current = { page: pref.key, sections: [], words: 0, mcqs: [], diagrams: page.diagrams, allMcqs: page.mcqs };
          chapters.push(current);
        }
        if (merge && current.page !== pref.key && !current.extraPages?.includes(pref.key)) {
          (current.extraPages ||= []).push(pref.key);
          current.extraDiagrams = [...(current.extraDiagrams || []), ...page.diagrams];
        }
        current.sections.push({ ...sec, page: pref.key, pageMcqs: page.mcqs });
        current.words += w;
        if (!firstOfPage) firstOfPage = current;
        if (pref.chapterTitle && !current.forcedTitle) current.forcedTitle = pref.chapterTitle;
      });
      firstOfPage && (firstOfPage.firstOf = [...(firstOfPage.firstOf || []), pref.key]);
    }

    const lessons = [];
    chapters.forEach((ch, idx) => {
      const titled = ch.sections.find((s) => s.title);
      let title = ch.forcedTitle || cleanTitle(titled ? titled.title : mod.title);
      if (!ch.forcedTitle && (!titled || (idx === 0 && ch.sections[0] && !ch.sections[0].title && ch.sections.length === 1))) title = idx === 0 ? 'Overview' : title;
      let slug = slugify(title) || `part-${idx + 1}`;
      if (used.has(slug)) slug = `${mod.slug.replace(/^(wd-[a-z]+-d+|lessons?-[d-]+).*$/, '$1')}-${slug}`;
      while (used.has(slug)) slug = `${slug}-${idx + 1}`;
      used.add(slug);
      ch.slug = slug; ch.title = title; ch.course = course.slug; ch.module = mod.slug;
      for (const k of ch.firstOf || []) pageFirstChapter[k] = `/chapter/${course.slug}/${mod.slug}/${slug}`;
      lessons.push(ch);
    });

    for (const ch of lessons) {
      const diagramPool = [...ch.diagrams, ...(ch.extraDiagrams || [])];
      const diagramOrder = [];
      const mcqs = [];
      const parts = [];
      ch.sections.forEach((sec) => {
        let md = sec.md.replace(/\{\{diagram:([\w-]+)\}\}/g, (m, key) => {
          const d = diagramPool.find((x) => x.key === key);
          if (!d) { problems.push(`${ch.page}: diagram ${key} not found`); return ''; }
          diagramOrder.push(d);
          return `{{diagram:${diagramOrder.length}}}`;
        });
        md = md.replace(/^@@QUIZ:(\d+)-(\d+)@@$/gm, (m, a, b) => {
          sec.pageMcqs.slice(Number(a), Number(b)).forEach((q, i) => mcqs.push({ q, n: Number(a) + i + 1, page: sec.page }));
          return '';
        });
        md = md.replace(/\n{3,}/g, '\n\n').trim();
        if (!md) return;
        parts.push(sec.title ? `## ${sec.title}\n\n${md}` : md);
      });
      ch.body = `# ${ch.title}\n\n${parts.join('\n\n')}\n`;
      ch.diagramOrder = diagramOrder;
      ch.mcqList = mcqs;
      // The reader shows the description under the title, so it lists what the chapter
      // covers instead of repeating the opening paragraph.
      const covered = ch.sections.filter((s) => s.title).map((s) => cleanTitle(s.title));
      ch.description = covered.length > 1 ? `${mod.title}: ${covered.join(' · ')}` : `${mod.title}${covered[0] && covered[0] !== ch.title ? `: ${covered[0]}` : ''}`;
    }

    manifest.modules.push({
      slug: mod.slug, title: mod.title, description: moduleLede || mod.description, badge: mod.badge,
      lessons: lessons.map((ch) => ({
        slug: ch.slug, title: ch.title, description: ch.description,
        minutes: Math.max(5, Math.round(words(ch.body) / 180)), difficulty: 'Intermediate'
      }))
    });
    allChapters.push(...lessons.map((ch) => ({ ...ch, courseDir })));
  }
  fs.writeFileSync(path.join(courseDir, 'course.json'), JSON.stringify(manifest, null, 2) + '\n');
}

// second pass: resolve cross-page links now that every page has a chapter url
for (const ch of allChapters) {
  ch.body = ch.body.replace(/@@page:([^@#]*)(#[^@]*)?@@/g, (m, rel) => {
    const key = pageRel[rel.replace(/\/$/, '').replace(/\.html$/, '')];
    if (key && pageFirstChapter[key]) return pageFirstChapter[key];
    problems.push(`${ch.page}: link to unmigrated page "${rel}" kept as github.io link`);
    return `https://balajiraghuram92.github.io/${rel}${rel ? '/' : ''}`;
  });
  fs.writeFileSync(path.join(ch.courseDir, 'lessons', `${ch.slug}.md`), ch.body);
  if (ch.diagramOrder.length) {
    fs.writeFileSync(path.join(ch.courseDir, 'diagrams', `${ch.slug}.json`), JSON.stringify({
      diagrams: ch.diagramOrder.map((d) => ({ title: d.title, caption: d.caption, svg: d.svg }))
    }, null, 2) + '\n');
  }
  if (ch.mcqList.length) {
    fs.writeFileSync(path.join(ch.courseDir, 'mcqs', `${ch.slug}.json`), JSON.stringify({
      questions: ch.mcqList.map(({ q, n, page }) => ({
        legacyKey: `aie-${page}-q${String(n).padStart(2, '0')}`.slice(0, 120),
        questionText: q.questionText, explanation: q.explanation, sourceType: 'FROM_MATERIAL', category: 'Checkpoint',
        options: q.options
      }))
    }, null, 2) + '\n');
  }
}

const summary = allChapters.map((c) => `${c.course}/${c.module}/${c.slug}  ${words(c.body)}w  ${c.diagramOrder.length}d  ${c.mcqList.length}q`);
fs.writeFileSync(path.join(here, 'assembly-report.txt'), [...summary, '', 'PROBLEMS:', ...problems].join('\n'));
console.log(`${allChapters.length} chapters, ${allChapters.reduce((a, c) => a + c.diagramOrder.length, 0)} diagrams, ${allChapters.reduce((a, c) => a + c.mcqList.length, 0)} mcqs, ${problems.length} problems`);
problems.slice(0, 40).forEach((p) => console.log('  ! ' + p));
