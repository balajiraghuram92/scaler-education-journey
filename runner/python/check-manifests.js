// Static checks for Python exercise manifests. Usage (from repo root):
//   node runner/python/check-manifests.js [exercise-dir ...]   (default: all under exercises/python)
// Exit code 1 if any problem is found.
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "..", "..");
const pyRoot = path.join(repo, "exercises", "python");
const course = JSON.parse(fs.readFileSync(path.join(repo, "api/Data/Content/python/course.json"), "utf8"));
const lessonModule = {};
for (const m of course.modules) for (const l of m.lessons) lessonModule[l.slug] = m.slug;

const assignmentSlugs = new Map();
const assignmentsDir = path.join(repo, "api/Data/Content/python/assignments");
for (const f of fs.readdirSync(assignmentsDir)) {
  const d = JSON.parse(fs.readFileSync(path.join(assignmentsDir, f), "utf8"));
  for (const a of d.assignments) assignmentSlugs.set(a.slug, d.lessonSlug);
}

const walk = dir => fs.readdirSync(dir, { withFileTypes: true }).flatMap(e =>
  e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]);

const dirs = process.argv.slice(2).length
  ? process.argv.slice(2).map(d => path.resolve(d))
  : fs.existsSync(pyRoot) ? walk(pyRoot).filter(f => path.basename(f) === "exercise.json").map(path.dirname) : [];

let problems = 0;
const ids = new Set();
const report = (dir, msg) => { problems++; console.log(`FAIL ${path.relative(repo, dir)}: ${msg}`); };

for (const dir of dirs) {
  let m;
  try { m = JSON.parse(fs.readFileSync(path.join(dir, "exercise.json"), "utf8")); }
  catch (e) { report(dir, `invalid exercise.json: ${e.message}`); continue; }

  const name = path.basename(dir);
  if (m.id !== name) report(dir, `id "${m.id}" must equal folder name "${name}"`);
  if (ids.has(m.id)) report(dir, `duplicate id ${m.id}`); ids.add(m.id);
  if (!assignmentSlugs.has(m.id)) report(dir, `id must match an assignment slug in api/Data/Content/python/assignments`);
  else if (assignmentSlugs.get(m.id) !== m.lessonSlug) report(dir, `lessonSlug ${m.lessonSlug} != assignment's lesson ${assignmentSlugs.get(m.id)}`);
  if (!lessonModule[m.lessonSlug]) report(dir, `unknown lessonSlug ${m.lessonSlug}`);
  else if (path.basename(path.dirname(dir)) !== lessonModule[m.lessonSlug]) report(dir, `folder must be exercises/python/${lessonModule[m.lessonSlug]}/${name}`);
  if (m.language !== "python") report(dir, `language must be "python"`);
  if (m.runtime?.profile !== "python-pytest") report(dir, `runtime.profile must be "python-pytest"`);
  if (!(m.runtime?.timeoutSeconds > 0 && m.runtime.timeoutSeconds <= 60)) report(dir, `runtime.timeoutSeconds must be 1-60`);
  if (m.testSuite?.path !== "tests") report(dir, `testSuite.path must be "tests"`);
  if (!m.title || !m.instructions) report(dir, `title and instructions are required`);
  if (!["warm-up", "core", "stretch"].includes(m.difficulty)) report(dir, `difficulty must be warm-up|core|stretch`);

  const files = m.files || [];
  if (!files.some(f => f.editable)) report(dir, `needs at least one editable file`);
  for (const f of files) {
    if (!f.id || !f.path || !f.displayName || f.path.includes("..") || f.path.startsWith("/") || f.path.includes("\\")) report(dir, `bad file entry ${JSON.stringify(f)}`);
    if (!f.path.endsWith(".py")) report(dir, `${f.path}: only .py files`);
    if (f.path.startsWith("tests/")) report(dir, `${f.path}: learner files must not live under tests/`);
    if (!fs.existsSync(path.join(dir, "starter", f.path))) report(dir, `starter/${f.path} missing`);
    if (f.editable && !fs.existsSync(path.join(dir, "solution", f.path))) report(dir, `solution/${f.path} missing`);
  }
  const declared = new Set(files.map(f => f.path));
  for (const sub of ["starter", "solution"]) {
    if (!fs.existsSync(path.join(dir, sub))) continue;
    for (const f of walk(path.join(dir, sub))) {
      const rel = path.relative(path.join(dir, sub), f).split(path.sep).join("/");
      if (!declared.has(rel)) report(dir, `${sub}/${rel} is not declared in files[]`);
    }
  }

  const testsDir = path.join(dir, "tests");
  if (!fs.existsSync(testsDir)) { report(dir, "tests/ missing"); continue; }
  const testFiles = walk(testsDir).filter(f => f.endsWith(".py"));
  if (!testFiles.some(f => /^test_.*\.py$/.test(path.basename(f)))) report(dir, `tests/ needs test_*.py files`);
  const testSource = testFiles.map(f => fs.readFileSync(f, "utf8")).join("\n");
  const testFns = new Set([...testSource.matchAll(/^\s*(?:async\s+)?def\s+(test_\w+)\s*\(/gm)].map(x => x[1]));
  const evidence = m.evidence || [];
  const evidenceMethods = new Set();
  for (const e of evidence) {
    if (!e.id || !e.label || !e.testMethod) report(dir, `bad evidence ${JSON.stringify(e)}`);
    if (evidenceMethods.has(e.testMethod)) report(dir, `duplicate evidence testMethod ${e.testMethod}`);
    evidenceMethods.add(e.testMethod);
    if (!testFns.has(e.testMethod)) report(dir, `evidence ${e.id} points at missing test function ${e.testMethod}`);
  }
  for (const fn of testFns) if (!evidenceMethods.has(fn)) report(dir, `test ${fn} has no evidence entry (every test needs a label)`);
  if (testFns.size < 3) report(dir, `at least 3 test functions expected, found ${testFns.size}`);
}

console.log(`${dirs.length} exercise(s) checked, ${problems} problem(s).`);
process.exit(problems ? 1 : 0);
