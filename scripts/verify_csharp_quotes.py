#!/usr/bin/env python3
"""
Mechanical verification script to prove that all C# verbatim string literals (@"...")
in api/Data/JavaVerticalSeedData.cs have zero unescaped single double-quote characters.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILE = os.path.join(ROOT, 'api', 'Data', 'JavaVerticalSeedData.cs')

def verify():
    print("=" * 70)
    print("  JAVA VERTICAL SEED DATA — C# VERBATIM QUOTE AUDITOR")
    print("=" * 70)

    if not os.path.exists(TARGET_FILE):
        print(f"[FAIL] Target file not found: {TARGET_FILE}")
        sys.exit(1)

    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    pattern = re.compile(r'("[^"]+"\s*(?:or\s*"[^"]+"\s*)*=>\s*@")', re.MULTILINE)
    matches = list(pattern.finditer(text))

    print(f"Auditing {len(matches)} lesson case blocks in GetAuthoredLessonContent...\n")

    total_failures = 0
    total_quotes_audited = 0

    for i, m in enumerate(matches):
        start = m.end()  # right after => @"
        matched_text = m.group(1).split('=>')[0].strip()

        if i + 1 < len(matches):
            next_start = matches[i + 1].start()
        else:
            next_start = text.find('_ => null', start)

        case_block = text[start:next_start]
        last_quote_idx = case_block.rfind('"')
        if last_quote_idx == -1:
            print(f"[FAIL] {matched_text}: No closing quote delimiter found!")
            total_failures += 1
            continue

        content = case_block[:last_quote_idx]

        # Scan for odd runs of quotes
        odd_runs = []
        for qm in re.finditer(r'"+', content):
            run_len = len(qm.group(0))
            total_quotes_audited += run_len
            if run_len % 2 != 0:
                line_no = content[:qm.start()].count('\n') + 1
                snippet_start = max(0, qm.start() - 25)
                snippet_end = min(len(content), qm.end() + 25)
                snippet = content[snippet_start:snippet_end].replace('\n', ' ')
                odd_runs.append((line_no, run_len, snippet))

        if odd_runs:
            print(f"[FAIL] {matched_text}: {len(odd_runs)} unescaped quote(s) found:")
            for line_no, rlen, snip in odd_runs:
                print(f"   Line +{line_no} (length {rlen}): ...{snip}...")
            total_failures += len(odd_runs)
        else:
            print(f"[PASS] {matched_text:50} -> All quotes paired ({content.count('\"\"')} escaped quotes)")

    print("\n" + "=" * 70)
    if total_failures == 0:
        print(f"  AUDIT PASSED! All {len(matches)} cases verified clean.")
        print(f"  Total escaped quote pairs validated: {total_quotes_audited // 2}")
        print("=" * 70)
        return 0
    else:
        print(f"  AUDIT FAILED! {total_failures} unescaped quote(s) found.")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(verify())
