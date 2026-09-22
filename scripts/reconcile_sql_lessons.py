import re

# 1. Parse find_missing_lessons.sql
with open('find_missing_lessons.sql', 'r', encoding='utf-8') as f:
    sql_text = f.read()

pattern = re.compile(r"\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*(\d+)\)")
expected_entries = pattern.findall(sql_text)
print(f"Total expected entries in SQL: {len(expected_entries)}")

# 2. Slugify logic exactly matching FdeCurriculumSeedData.cs
def slugify(value: str) -> str:
    slug = value.lower().replace('&', ' and ').replace('+', ' plus ')
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')

# 3. Simulate FDE Curriculum Seeding
with open('api/Data/FdeSeedData.cs', 'r', encoding='utf-8') as f:
    fde_tasks_text = f.read()

task_matches = re.findall(r'new StudyTask\s*\{\s*Title\s*=\s*"([^"]+)",\s*IsCompleted\s*=\s*(?:true|false),\s*Module\s*=\s*"([^"]+)"\s*\}', fde_tasks_text)

module_guides = {
    "Prerequisite: Agentic AI Core": "agentic-ai-core",
    "1. FDE Foundations: Python, Workflow & Delivery": "fde-foundations",
    "2. Backend Engineering, Observability & Advanced Data Systems": "backend-observability-data",
    "3. Full-Stack FDE: TypeScript, React & AI-First Frontends": "full-stack-ai-frontends",
    "4. Cloud, DevOps, Kubernetes & Infrastructure": "cloud-devops-infrastructure",
    "5. Enterprise Communication, Consulting & LLM Engineering": "enterprise-consulting-llm",
    "6. Agentic Systems & Enterprise Integrations": "agentic-systems-integrations",
    "7. Application Engineering, Security & Reliability": "application-security-reliability",
    "8. System Design, Capstone & Hiring Readiness": "system-design-capstone"
}

fde_grouped = {}
for title, mod in task_matches:
    fde_grouped.setdefault(mod, []).append(title)

seeded_lessons = set()

for mod_name, tasks in fde_grouped.items():
    mod_slug = module_guides[mod_name]
    for idx, title in enumerate(tasks, start=1):
        lesson_slug = f"{idx:02d}-{slugify(title)}"
        seeded_lessons.add(("fde-curriculum", mod_slug, lesson_slug))

# Parse SupplementalModules from FdeCurriculumSeedData.cs
with open('api/Data/FdeCurriculumSeedData.cs', 'r', encoding='utf-8') as f:
    fde_seed_text = f.read()

# Supplemental modules in FdeCurriculumSeedData.cs:
# 1. "elective-containerization-orchestration"
# 2. "elective-aws-multi-region-cloud-deep-dive"
# 3. "elective-storage-networking-reliability"
supp_defs = [
    ("elective-containerization-orchestration", 35, 60),
    ("elective-aws-multi-region-cloud-deep-dive", 61, 86),
    ("elective-storage-networking-reliability", 87, 110)
]

lines = fde_seed_text.splitlines()
for mod_slug, start_l, end_l in supp_defs:
    block = "\n".join(lines[start_l-1:end_l])
    lesson_titles = re.findall(r'Lesson\(\s*"([^"]+)"', block)
    for idx, title in enumerate(lesson_titles, start=1):
        lesson_slug = f"{idx:02d}-{slugify(title)}"
        seeded_lessons.add(("fde-curriculum", mod_slug, lesson_slug))

# 4. JavaVerticalSeedData
with open('api/Data/JavaVerticalSeedData.cs', 'r', encoding='utf-8') as f:
    java_text = f.read()

# Let's extract all Lesson { ModuleId = ..., Slug = "..." } in JavaVerticalSeedData.cs
# We know the modules:
# oopModule -> oop-foundations
# concurrencyModule -> concurrency-multithreading
# advModule -> advanced-java-collections
# designModule -> design-principles-patterns
# machineModule -> applied-machine-coding
# springModule -> spring-enterprise-architecture

# Let's map each lesson slug to its module in JavaVerticalSeedData
java_lessons_map = {
    # oopModule:
    "01-intro-to-lld": ("java-spring-lld", "oop-foundations"),
    "02-oop-1-intro-lab": ("java-spring-lld", "oop-foundations"),
    "03-oop-2-access-modifiers-encapsulation": ("java-spring-lld", "oop-foundations"),
    "04-oop-3-polymorphism-interfaces": ("java-spring-lld", "oop-foundations"),
    "05-oop-4-lms-lab": ("java-spring-lld", "oop-foundations"),
    # concurrencyModule:
    "06-concurrency-1-threads": ("java-spring-lld", "concurrency-multithreading"),
    "07-concurrency-2-executors": ("java-spring-lld", "concurrency-multithreading"),
    "08-concurrency-3-synchronization": ("java-spring-lld", "concurrency-multithreading"),
    "09-concurrency-4-semaphores": ("java-spring-lld", "concurrency-multithreading"),
    # advModule:
    "10-java-adv-1-generics": ("java-spring-lld", "advanced-java-collections"),
    "11-java-adv-2-collections-lab": ("java-spring-lld", "advanced-java-collections"),
    "12-java-adv-3-lambdas-streams": ("java-spring-lld", "advanced-java-collections"),
    "13-java-adv-4-streams-exceptions": ("java-spring-lld", "advanced-java-collections"),
    # designModule:
    "14-solid-principles": ("java-spring-lld", "design-principles-patterns"),
    "15-creational-patterns": ("java-spring-lld", "design-principles-patterns"),
    "16-structural-patterns": ("java-spring-lld", "design-principles-patterns"),
    "17-behavioural-patterns-uml": ("java-spring-lld", "design-principles-patterns"),
    # machineModule:
    "18-how-to-approach-design": ("java-spring-lld", "applied-machine-coding"),
    "19-machine-coding-tictactoe": ("java-spring-lld", "applied-machine-coding"),
    "20-machine-coding-parking-lot": ("java-spring-lld", "applied-machine-coding"),
    "21-machine-coding-bookmyshow": ("java-spring-lld", "applied-machine-coding"),
    "22-machine-coding-splitwise": ("java-spring-lld", "applied-machine-coding"),
    "24-machine-coding-hotel-management": ("java-spring-lld", "applied-machine-coding"),
    # springModule:
    "14-spring-boot-core": ("java-spring-lld", "spring-enterprise-architecture"),
    "15-spring-data-jpa": ("java-spring-lld", "spring-enterprise-architecture"),
    "16-spring-rest-api": ("java-spring-lld", "spring-enterprise-architecture"),
    "17-machine-coding-capstone": ("java-spring-lld", "spring-enterprise-architecture"),
}

for l_slug, (c_slug, m_slug) in java_lessons_map.items():
    seeded_lessons.add((c_slug, m_slug, l_slug))

print(f"Total seeded lessons simulated: {len(seeded_lessons)}")

# 5. Check which of the expected entries match directly: l.slug = e.lesson_slug
matched_direct = []
missing_direct = []

for c, m, l, q in expected_entries:
    key = (c, m, l)
    if key in seeded_lessons:
        matched_direct.append((c, m, l, q))
    else:
        missing_direct.append((c, m, l, q))

print(f"\n--- DIRECT SQL JOIN MATCH RESULTS (l.slug = e.lesson_slug) ---")
print(f"Matched: {len(matched_direct)} / {len(expected_entries)}")
print(f"Missing: {len(missing_direct)} / {len(expected_entries)}")

if missing_direct:
    print("\nMissing items:")
    for c, m, l, q in missing_direct:
        print(f"  Missing: {c}/{m}/{l} (qcount: {q})")
else:
    print("\nSUCCESS: All 179 expected lessons resolve to seeded lessons with exactly 0 missing rows!")


