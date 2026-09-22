import re
import json

# 1. Check updated migrate-mcqs script or filter
with open('scripts/mcq-migration-data.json', 'r', encoding='utf-8') as f:
    raw_groups = json.load(f)

# Filter out the 2 alias groups
canonical_groups = [
    g for g in raw_groups
    if g['lessonSlug'] not in ('02-oop-classes-objects', '03-oop2-encapsulation-inheritance')
]

print(f"Original groups: {len(raw_groups)}, Canonical groups: {len(canonical_groups)}")

# Write canonical mcq-migration-data.json
with open('scripts/mcq-migration-data.json', 'w', encoding='utf-8') as f:
    json.dump(canonical_groups, f, indent=2)

with open('api/Data/mcq-migration-data.json', 'w', encoding='utf-8') as f:
    json.dump(canonical_groups, f, indent=2)

print("Updated scripts/mcq-migration-data.json and api/Data/mcq-migration-data.json")

# Calculate total questions
total_q = sum(len(g['questions']) for g in canonical_groups)
unique_q = len({q['legacyKey'] for g in canonical_groups for q in g['questions']})
print(f"Total questions in canonical dataset: {total_q}, unique legacyKey: {unique_q}")
assert total_q == unique_q == 1182, "Questions count mismatch!"
