#!/usr/bin/env python3
"""
Parking Lot Exercises Contract Auditor
---------------------------------------
Verifies contract compliance for:
  - exercises/java/java-lld/applied-machine-coding/generate-parking-ticket/
  - exercises/java/java-lld/applied-machine-coding/display-parking-lot-capacity/
  - app/src/data/lessonExerciseAssociations.js

Contract checks:
  1. exercise.json exists, is valid JSON, and has all required top-level fields
     ('id', 'lessonSlug', 'title', 'language', 'runtime', 'files', 'testSuite', 'evidence').
  2. Every file declared in files[]:
     - Exists in solution/ and exists in starter/.
     - Has unique 'id' and unique 'path'.
     - If editable == False: solution and starter are byte-for-byte identical.
     - If editable == True: starter has '// TODO:' and does NOT match solution.
  3. testSuite.path exists under the exercise directory.
  4. pom.xml exists and is valid XML with JUnit and reflections dependencies.
  5. For every entry in evidence[]:
     - Unique 'id' and unique 'testMethod'.
     - The testMethod actually exists in the Java test file with @Test annotation.
  6. lessonExerciseAssociations.js contains the entry for
     'java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot' with both IDs.
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXERCISES = [
    "exercises/java/java-lld/applied-machine-coding/generate-parking-ticket",
    "exercises/java/java-lld/applied-machine-coding/display-parking-lot-capacity",
]

REQUIRED_TOP_LEVEL_FIELDS = [
    "id",
    "lessonSlug",
    "title",
    "language",
    "runtime",
    "files",
    "testSuite",
    "evidence",
]

ASSOCIATIONS_FILE_REL = "app/src/data/lessonExerciseAssociations.js"
EXPECTED_LESSON_KEY = "java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot"
EXPECTED_EXERCISE_IDS = [
    "java-lld-generate-parking-ticket",
    "java-lld-display-parking-lot-capacity",
]


class AuditFailure(Exception):
    pass


def log(msg, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{msg}")


def audit_exercise(ex_rel_path):
    ex_dir = os.path.join(REPO_ROOT, ex_rel_path)
    log(f"\n{'='*70}")
    log(f"Auditing Exercise: {ex_rel_path}")
    log(f"{'='*70}")

    if not os.path.isdir(ex_dir):
        raise AuditFailure(f"Exercise directory missing: {ex_dir}")

    # 1. exercise.json existence, valid JSON, and required top-level fields
    manifest_path = os.path.join(ex_dir, "exercise.json")
    if not os.path.isfile(manifest_path):
        raise AuditFailure(f"Missing exercise.json at: {manifest_path}")

    log(f"[PASS] Found exercise.json ({os.path.getsize(manifest_path)} bytes)", indent=1)

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        raise AuditFailure(f"exercise.json is not valid JSON: {e}")

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in manifest:
            raise AuditFailure(f"Missing required top-level field '{field}' in exercise.json")
        if manifest[field] is None:
            raise AuditFailure(f"Field '{field}' in exercise.json is None")

    log(f"[PASS] All {len(REQUIRED_TOP_LEVEL_FIELDS)} required top-level fields present: "
        f"{', '.join(REQUIRED_TOP_LEVEL_FIELDS)}", indent=1)
    log(f"       id: '{manifest['id']}', title: '{manifest['title']}'", indent=1)

    # 2. Files[] verification
    files = manifest.get("files", [])
    if not isinstance(files, list) or len(files) == 0:
        raise AuditFailure(f"'files' must be a non-empty list in exercise.json")

    seen_file_ids = set()
    seen_file_paths = set()
    editable_count = 0
    read_only_count = 0

    log(f"\n  Auditing files declared in files[] ({len(files)} total files):")

    for file_entry in files:
        f_id = file_entry.get("id")
        f_path = file_entry.get("path")
        editable = file_entry.get("editable", False)

        if not f_id or not isinstance(f_id, str):
            raise AuditFailure(f"Invalid or missing 'id' in files[] entry: {file_entry}")
        if not f_path or not isinstance(f_path, str):
            raise AuditFailure(f"Invalid or missing 'path' in files[] entry: {file_entry}")

        if f_id in seen_file_ids:
            raise AuditFailure(f"Duplicate file id in files[]: '{f_id}'")
        seen_file_ids.add(f_id)

        if f_path in seen_file_paths:
            raise AuditFailure(f"Duplicate file path in files[]: '{f_path}'")
        seen_file_paths.add(f_path)

        sol_file = os.path.join(ex_dir, "solution", f_path)
        sta_file = os.path.join(ex_dir, "starter", f_path)

        if not os.path.isfile(sol_file):
            raise AuditFailure(f"Declared file missing in solution/: '{f_path}' (checked {sol_file})")
        if not os.path.isfile(sta_file):
            raise AuditFailure(f"Declared file missing in starter/: '{f_path}' (checked {sta_file})")

        with open(sol_file, "rb") as f_sol, open(sta_file, "rb") as f_sta:
            sol_bytes = f_sol.read()
            sta_bytes = f_sta.read()

        if not editable:
            read_only_count += 1
            if sol_bytes != sta_bytes:
                raise AuditFailure(
                    f"Non-editable file '{f_path}' is NOT byte-for-byte identical between solution/ and starter/!\n"
                    f"  solution bytes: {len(sol_bytes)}, starter bytes: {len(sta_bytes)}"
                )
        else:
            editable_count += 1
            if sol_bytes == sta_bytes:
                raise AuditFailure(
                    f"Editable file '{f_path}' matches solution/ byte-for-byte! It must have implementation stripped."
                )

            with open(sta_file, "r", encoding="utf-8") as f_sta_text:
                sta_text = f_sta_text.read()

            if "// TODO:" not in sta_text:
                raise AuditFailure(
                    f"Editable starter file '{f_path}' is missing '// TODO:' comment in starter implementation!"
                )

    log(f"[PASS] Unique IDs and unique paths verified across all {len(files)} files", indent=1)
    log(f"[PASS] {read_only_count} non-editable files verified byte-for-byte identical between solution/ and starter/", indent=1)
    log(f"[PASS] {editable_count} editable files verified to contain '// TODO:' and differ from solution/", indent=1)

    # 3. testSuite.path verification
    test_suite = manifest.get("testSuite", {})
    if not isinstance(test_suite, dict):
        raise AuditFailure(f"'testSuite' must be an object in exercise.json")

    ts_path = test_suite.get("path")
    if not ts_path or not isinstance(ts_path, str):
        raise AuditFailure(f"Missing or invalid 'path' in testSuite")

    full_ts_path = os.path.join(ex_dir, ts_path)
    if not os.path.isfile(full_ts_path):
        raise AuditFailure(f"testSuite.path '{ts_path}' does not exist on disk at: {full_ts_path}")

    log(f"\n  Auditing testSuite:")
    log(f"[PASS] testSuite.path exists: {ts_path} ({os.path.getsize(full_ts_path)} bytes)", indent=1)

    # 4. pom.xml verification
    pom_path = os.path.join(ex_dir, "pom.xml")
    if not os.path.isfile(pom_path):
        raise AuditFailure(f"pom.xml does not exist at: {pom_path}")

    log(f"\n  Auditing pom.xml:")
    try:
        pom_tree = ET.parse(pom_path)
        pom_root = pom_tree.getroot()
    except ET.ParseError as e:
        raise AuditFailure(f"pom.xml is not valid XML: {e}")

    log(f"[PASS] pom.xml exists and parsed successfully as valid XML", indent=1)

    # Inspect dependencies regardless of XML namespace
    dependencies = pom_root.findall(".//{*}dependency")
    has_junit = False
    has_reflections = False

    for dep in dependencies:
        group_el = dep.find("{*}groupId")
        artifact_el = dep.find("{*}artifactId")
        group_text = group_el.text.strip() if group_el is not None and group_el.text else ""
        artifact_text = artifact_el.text.strip() if artifact_el is not None and artifact_el.text else ""

        if "junit" in group_text.lower() or "junit" in artifact_text.lower():
            has_junit = True
        if "reflections" in group_text.lower() or "reflections" in artifact_text.lower():
            has_reflections = True

    if not has_junit:
        raise AuditFailure(f"pom.xml in {ex_rel_path} does not declare a JUnit dependency!")
    if not has_reflections:
        raise AuditFailure(f"pom.xml in {ex_rel_path} does not declare a Reflections dependency!")

    log(f"[PASS] pom.xml dependencies verified: JUnit and Reflections dependencies present", indent=1)

    # 5. Evidence[] verification
    evidence = manifest.get("evidence", [])
    if not isinstance(evidence, list) or len(evidence) == 0:
        raise AuditFailure(f"'evidence' must be a non-empty list in exercise.json")

    log(f"\n  Auditing evidence[] ({len(evidence)} entries):")
    with open(full_ts_path, "r", encoding="utf-8") as f:
        test_file_content = f.read()

    seen_ev_ids = set()
    seen_test_methods = set()

    for ev in evidence:
        ev_id = ev.get("id")
        test_method = ev.get("testMethod")

        if not ev_id or not isinstance(ev_id, str):
            raise AuditFailure(f"Invalid or missing 'id' in evidence entry: {ev}")
        if not test_method or not isinstance(test_method, str):
            raise AuditFailure(f"Invalid or missing 'testMethod' in evidence entry: {ev}")

        if ev_id in seen_ev_ids:
            raise AuditFailure(f"Duplicate evidence id: '{ev_id}'")
        seen_ev_ids.add(ev_id)

        if test_method in seen_test_methods:
            raise AuditFailure(f"Duplicate testMethod in evidence: '{test_method}'")
        seen_test_methods.add(test_method)

        # Check @Test annotation preceding testMethod
        # Match @Test followed by method signature
        pattern = rf"@Test\s+(?:public\s+)?(?:void|[A-Za-z0-9_<>]+)\s+{re.escape(test_method)}\s*\("
        if not re.search(pattern, test_file_content):
            raise AuditFailure(
                f"Test method '{test_method}' declared in evidence id '{ev_id}' "
                f"was NOT found with '@Test' in test file: {ts_path}"
            )
        log(f"[PASS] Evidence '{ev_id}' -> testMethod '{test_method}()' found in {os.path.basename(ts_path)}", indent=1)

    log(f"[PASS] All {len(evidence)} evidence entries have unique IDs, unique testMethods, and valid @Test bindings", indent=1)
    return manifest["id"]


def audit_lesson_associations(verified_exercise_ids):
    assoc_file = os.path.join(REPO_ROOT, ASSOCIATIONS_FILE_REL)
    log(f"\n{'='*70}")
    log(f"Auditing Lesson Exercise Associations: {ASSOCIATIONS_FILE_REL}")
    log(f"{'='*70}")

    if not os.path.isfile(assoc_file):
        raise AuditFailure(f"Associations file missing at: {assoc_file}")

    with open(assoc_file, "r", encoding="utf-8") as f:
        content = f.read()

    if EXPECTED_LESSON_KEY not in content:
        raise AuditFailure(
            f"lessonExerciseAssociations.js missing expected key: '{EXPECTED_LESSON_KEY}'"
        )

    log(f"[PASS] Found association key '{EXPECTED_LESSON_KEY}' in {ASSOCIATIONS_FILE_REL}", indent=1)

    for ex_id in EXPECTED_EXERCISE_IDS:
        if ex_id not in content:
            raise AuditFailure(
                f"lessonExerciseAssociations.js missing exercise id: '{ex_id}'"
            )
        log(f"[PASS] Found wired exercise id: '{ex_id}'", indent=1)

    for ex_id in verified_exercise_ids:
        if ex_id not in EXPECTED_EXERCISE_IDS:
            raise AuditFailure(f"Unexpected exercise id verified: {ex_id}")

    log(f"[PASS] Both exercise IDs correctly wired for lesson 20 in {ASSOCIATIONS_FILE_REL}", indent=1)


def main():
    print("=" * 70)
    print("  EXERCISE CONTRACT AUDITOR — PARKING LOT EXERCISES")
    print("=" * 70)

    verified_ids = []
    try:
        for ex_path in EXERCISES:
            ex_id = audit_exercise(ex_path)
            verified_ids.append(ex_id)

        audit_lesson_associations(verified_ids)

        print(f"\n{'='*70}")
        print("  ALL AUDIT CHECKS PASSED PERFECTLY!")
        print(f"  Verified Exercises: {', '.join(verified_ids)}")
        print(f"{'='*70}\n")
        return 0

    except AuditFailure as af:
        print(f"\n[FAIL] AUDIT FAILURE: {af}\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED AUDIT ERROR: {e}\n", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
