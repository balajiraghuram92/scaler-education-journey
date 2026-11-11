"""One-off converter: extract seed DATA from the big C# seed files to JSON.

NOTE: regular-string escapes are decoded manually (never codecs.unicode_escape,
which mangles non-ASCII source characters). Verbatim strings keep raw bytes,
including the CRLF line endings the database stores.
"""

Parses the C# object initializers in api/Data/JavaVerticalSeedData.cs and
api/Data/FdeCurriculumSeedData.cs and writes app/seed/data/*.json, which the
hand-ported Python seeders load. Run from the repository root:

    python api-python/tools/extract_seed_data.py [--check]

--check only validates and reports counts without writing files.
The script fails loudly on any value shape it does not understand.
"""

from __future__ import annotations

import json
import os
import re
import sys

_SIMPLE_ESCAPES = {
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "0": "\0",
    "\\": "\\",
    '"': '"',
    "'": "'",
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "v": "\v",
}


def _decode_escapes(raw: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(raw):
        if raw[i] != "\\" or i + 1 >= len(raw):
            out.append(raw[i])
            i += 1
            continue
        nxt = raw[i + 1]
        if nxt in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[nxt])
            i += 2
        elif nxt == "u" and i + 5 < len(raw):
            out.append(chr(int(raw[i + 2 : i + 6], 16)))
            i += 6
        elif nxt == "U" and i + 9 < len(raw):
            out.append(chr(int(raw[i + 2 : i + 10], 16)))
            i += 10
        elif nxt == "x":
            digits = ""
            for k in range(i + 2, min(i + 6, len(raw))):
                if raw[k] in "0123456789abcdefABCDEF":
                    digits += raw[k]
                else:
                    break
            if not digits:
                raise ValueError(f"bad \\x escape in {raw!r}")
            out.append(chr(int(digits, 16)))
            i += 2 + len(digits)
        else:
            raise ValueError(f"unsupported escape in {raw!r}")
    return "".join(out)


def read_source(path: str) -> str:
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def mask_strings(src: str) -> str:
    """Blank string literal bodies (offsets kept) but preserve the quote delimiters,
    so structural matching still sees where strings start and end."""
    chars = list(src)
    i, n = 0, len(src)
    while i < n:
        if src[i] == "@" and i + 1 < n and src[i + 1] == '"':
            j = i + 2
            while j < n:
                if src[j] == '"' and j + 1 < n and src[j + 1] == '"':
                    j += 2
                    continue
                if src[j] == '"':
                    break
                j += 1
            for k in range(i + 2, min(j, n)):
                if chars[k] not in ("\n", "\r"):
                    chars[k] = " "
            i = min(j + 1, n)
        elif src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\":
                    j += 1
                j += 1
            for k in range(i + 1, min(j, n)):
                if chars[k] not in ("\n", "\r"):
                    chars[k] = " "
            i = min(j + 1, n)
        else:
            i += 1
    return "".join(chars)


def decode_at(src: str, start: int) -> tuple[str, int]:
    """Decode the string literal starting at `start` (regular or verbatim)."""
    if src[start] == "@":
        assert src[start + 1] == '"', f"expected verbatim string at {start}"
        j = start + 2
        parts: list[str] = []
        while True:
            if src[j] == '"' and j + 1 < len(src) and src[j + 1] == '"':
                parts.append('"')
                j += 2
                continue
            if src[j] == '"':
                return "".join(parts), j + 1
            parts.append(src[j])
            j += 1
    assert src[start] == '"', f"expected string at {start}"
    j = start + 1
    raw: list[str] = []
    while src[j] != '"':
        if src[j] == "\\":
            raw.append(src[j])
            raw.append(src[j + 1])
            j += 2
        else:
            raw.append(src[j])
            j += 1
    return _decode_escapes("".join(raw)), j + 1


def extract_balanced(text: str, open_index: int, open_ch: str, close_ch: str) -> str:
    """Extract the balanced span starting at an opening bracket (masked text)."""
    assert text[open_index] == open_ch
    depth = 0
    for j in range(open_index, len(text)):
        if text[j] == open_ch:
            depth += 1
        elif text[j] == close_ch:
            depth -= 1
            if depth == 0:
                return text[open_index : j + 1]
    raise ValueError(f"unbalanced {open_ch}{close_ch} at {open_index}")


def split_top_level(text: str, separator: str = ",") -> list[str]:
    """Split on separator at depth 0 (masked text: strings are spaces)."""
    parts, depth, current = [], 0, []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closers = set(pairs.values())
    for ch in text:
        if ch in pairs:
            depth += 1
            current.append(ch)
        elif ch in closers:
            depth -= 1
            current.append(ch)
        elif ch == separator and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    parts.append("".join(current))
    return parts


def _decode_string_in_span(src: str, masked: str, span_start: int, span_text: str) -> str:
    """Decode the single string literal inside a masked span."""
    offset = next(
        i
        for i, ch in enumerate(span_text)
        if ch == '"' or (ch == "@" and span_text[i + 1 : i + 2] == '"')
    )
    value, _ = decode_at(src, span_start + offset)
    return value


def parse_initializer(
    src: str, masked: str, block_start: int, block_text: str
) -> dict:
    """Parse `Prop = value, ...` inside a `new X { ... }` block."""
    inner = block_text[1:-1]
    result: dict = {}
    cursor = block_start
    for part in split_top_level(inner):
        part = part.strip()
        if not part:
            continue
        name, _, value = part.partition("=")
        name = name.strip()
        value = value.strip()
        if not name or not value:
            raise ValueError(f"cannot parse initializer part: {part!r}")
        part_offset = masked.index(part, cursor)
        cursor = part_offset + len(part)
        result[name] = parse_value(src, masked, part_offset, value)
    return result


def parse_value(src: str, masked: str, part_offset: int, value: str):  # type: ignore[no-untyped-def]
    stripped = value.strip()
    if stripped.startswith('"') or stripped.startswith("@\""):
        return _decode_string_in_span(src, masked, part_offset, stripped)
    if re.fullmatch(r"-?\d+", stripped):
        return int(stripped)
    if stripped in ("true", "false"):
        return stripped == "true"
    if stripped == "null":
        return None
    match = re.fullmatch(r'GetAuthoredLessonContent\("([^"\\]+)"\)\s*\?\?\s*string\.Empty', stripped)
    if match:
        return {"$content_ref": match.group(1)}
    if re.fullmatch(r"[A-Za-z_][\w.]*", stripped):
        return {"$var": stripped}
    raise ValueError(f"unsupported initializer value: {stripped!r}")


def parse_call_args(src: str, masked: str, call_start: int, call_text: str) -> list:
    """Parse positional args of a `Name(...)` call."""
    inner = call_text[call_text.index("(") + 1 : -1]
    args = []
    cursor = call_start
    for part in split_top_level(inner):
        part = part.strip()
        if not part:
            continue
        part_offset = masked.index(part, cursor)
        cursor = part_offset + len(part)
        args.append(parse_value(src, masked, part_offset, part))
    return args


def extract_new_blocks(src: str, masked: str, type_name: str) -> list[dict]:
    blocks = []
    for match in re.finditer(rf"\bnew\s+{re.escape(type_name)}\b", masked):
        brace = masked.index("{", match.end())
        block_text = extract_balanced(masked, brace, "{", "}")
        blocks.append(parse_initializer(src, masked, brace, block_text))
    return blocks


def _string_spans_in(masked: str, start: int, end: int) -> list[int]:
    """Absolute offsets of string-literal starts within [start, end) of masked text."""
    spans = []
    i = start
    while i < end:
        if masked[i] == "@" and i + 1 < len(masked) and masked[i + 1] == '"':
            spans.append(i)
            i = masked.index('"', i + 2, end) + 1
        elif masked[i] == '"':
            spans.append(i)
            i = masked.index('"', i + 1, end) + 1
        else:
            i += 1
    return spans


def extract_switch_content(src: str, masked: str) -> dict[str, str]:
    """Extract `"slug" [or "slug2"] => @"..."` arms."""
    content: dict[str, str] = {}
    arm_re = re.compile(r'"(?:[^"\\]|\\.)*"(?:\s+or\s*"(?:[^"\\]|\\.)*")*\s*=>\s*@"')
    for match in arm_re.finditer(masked):
        # The match ends at the body's opening @"; slugs precede it.
        body_start = match.end() - 2
        spans = _string_spans_in(masked, match.start(), body_start)
        if not spans:
            raise ValueError(f"cannot parse switch arm at {match.start()}")
        text, _ = decode_at(src, body_start)
        for span in spans:
            slug, _ = decode_at(src, span)
            if slug in content:
                raise ValueError(f"duplicate authored slug: {slug}")
            content[slug] = text
    if not content:
        raise ValueError("no authored switch arms found")
    return content


def extract_java(path: str) -> dict:
    src = read_source(path)
    masked = mask_strings(src)

    vertical_tasks = extract_new_blocks(src, masked, "StudyTask")

    # Lessons grouped by SeedModuleNLessons method; each region ends at the next
    # method so EnsureExpandedModules' own `new Lesson` is not misattributed.
    module_lessons: dict[str, list[dict]] = {}
    all_methods = [m.start() for m in re.finditer(r"private static \w[\w<>\[\],\s\?]*\w+\(", masked)]
    method_starts = [
        (m.group(1), m.end()) for m in re.finditer(r"private static void (SeedModule\dLessons)\(", masked)
    ]
    for name, start in method_starts:
        following = [p for p in all_methods if p > start]
        end = min(following) if following else len(masked)
        region = masked[start:end]
        lessons = []
        for match in re.finditer(r"\bnew\s+Lesson\b", region):
            brace = region.index("{", match.end())
            block_text = extract_balanced(region, brace, "{", "}")
            lessons.append(parse_initializer(src, masked, start + brace, block_text))
        module_lessons[name] = lessons

    # Study-guide tuples ("Title", @"...", order)
    guide_start = masked.index("SeedLesson3StudyGuide")
    guide_end = masked.index("private static void SeedModule2Lessons")
    guide_region = masked[guide_start:guide_end]
    study_guide = []
    for match in re.finditer(r'\(\s*"', guide_region):
        paren_text = extract_balanced(guide_region, match.start(), "(", ")")
        args = parse_call_args(src, masked, guide_start + match.start(), paren_text)
        if len(args) != 3:
            raise ValueError(f"unexpected study-guide tuple: {args!r}")
        study_guide.append({"title": args[0], "content": args[1], "order": args[2]})

    # Expanded modules: new("slug", "title", "desc", "badge", order, new[] { Chapter(...)... })
    expanded_modules = []
    for match in re.finditer(r"\bnew\s*\(\s*\"", masked):
        # Only top-level `new(` calls with 6 args ending in `new[]` are modules.
        paren = extract_balanced(masked, masked.index("(", match.start()), "(", ")")
        if "new[]" not in paren and "new [" not in paren:
            continue
        # Manual parse: first five top-level args + chapter list.
        inner = paren[paren.index("(") + 1 : -1]
        top = split_top_level(inner)
        if len(top) != 6:
            raise ValueError(f"unexpected expanded-module shape: {paren[:80]!r}")
        base = masked.index(top[0], match.start())
        slug = parse_value(src, masked, base, top[0].strip())
        title = parse_value(src, masked, base, top[1].strip())
        description = parse_value(src, masked, base, top[2].strip())
        badge = parse_value(src, masked, base, top[3].strip())
        order_index = parse_value(src, masked, base, top[4].strip())
        array_text = top[5]
        array_off = masked.index(array_text, match.start())
        chapters = []
        for chapter_match in re.finditer(r"\bChapter\s*\(", array_text):
            absolute = array_off + chapter_match.start()
            call_text = extract_balanced(masked, masked.index("(", absolute), "(", ")")
            chapter_args = parse_call_args(src, masked, absolute, call_text)
            if len(chapter_args) not in (10, 11):
                raise ValueError(f"unexpected Chapter() arity: {len(chapter_args)}")
            chapters.append(
                {
                    "slug": chapter_args[0],
                    "title": chapter_args[1],
                    "description": chapter_args[2],
                    "concepts": chapter_args[3],
                    "scenario": chapter_args[4],
                    "practice": chapter_args[5],
                    "evidence": chapter_args[6],
                    "extension": chapter_args[7],
                    "estimated_minutes": chapter_args[8],
                    "reference": chapter_args[9],
                    "difficulty": chapter_args[10] if len(chapter_args) == 11 else "Intermediate",
                }
            )
        expanded_modules.append(
            {
                "slug": slug,
                "title": title,
                "description": description,
                "badge": badge,
                "order_index": order_index,
                "lessons": chapters,
            }
        )

    authored_content = extract_switch_content(src, masked)

    return {
        "vertical_tasks": vertical_tasks,
        "module_lessons": module_lessons,
        "study_guide": study_guide,
        "expanded_modules": expanded_modules,
        "authored_content": authored_content,
    }


def extract_fde(path: str) -> dict:
    src = read_source(path)
    masked = mask_strings(src)

    # Supplemental modules
    supplemental_modules = []
    for match in re.finditer(r"\bnew\s+SupplementalModuleDefinition\s*\(", masked):
        call_text = extract_balanced(masked, masked.index("(", match.start()), "(", ")")
        inner = call_text[call_text.index("(") + 1 : -1]
        top = split_top_level(inner)
        if len(top) != 6:
            raise ValueError(f"unexpected supplemental-module shape: {call_text[:80]!r}")
        base = match.start()
        slug = parse_value(src, masked, base, top[0].strip())
        title = parse_value(src, masked, base, top[1].strip())
        description = parse_value(src, masked, base, top[2].strip())
        reference_url = parse_value(src, masked, base, top[3].strip())
        delivery_context = parse_value(src, masked, base, top[4].strip())
        array_off = masked.index(top[5], match.start())
        lessons = []
        for lesson_match in re.finditer(r"\bLesson\s*\(", top[5]):
            absolute = array_off + lesson_match.start()
            lesson_call = extract_balanced(masked, masked.index("(", absolute), "(", ")")
            lesson_args = parse_call_args(src, masked, absolute, lesson_call)
            if len(lesson_args) not in (6, 7):
                raise ValueError(f"unexpected Lesson() arity: {len(lesson_args)}")
            lessons.append(
                {
                    "title": lesson_args[0],
                    "focus": lesson_args[1],
                    "core_concepts": lesson_args[2],
                    "scenario": lesson_args[3],
                    "practice": lesson_args[4],
                    "evidence": lesson_args[5],
                    "estimated_minutes": lesson_args[6] if len(lesson_args) == 7 else 75,
                }
            )
        supplemental_modules.append(
            {
                "slug": slug,
                "title": title,
                "description": description,
                "reference_url": reference_url,
                "delivery_context": delivery_context,
                "lessons": lessons,
            }
        )

    # ModuleGuides: ["key"] = new(...)
    guides: dict[str, dict] = {}
    for match in re.finditer(r'\["[^"\\]+"\]\s*=\s*new\s*\(', masked):
        key_span = _string_spans_in(masked, match.start(), match.end())[0]
        key, _ = decode_at(src, key_span)
        call_text = extract_balanced(masked, masked.index("(", match.start()), "(", ")")
        args = parse_call_args(src, masked, match.start(), call_text)
        if len(args) != 6:
            raise ValueError(f"unexpected ModuleGuide shape for {key}")
        guides[key] = {
            "slug": args[0],
            "title": args[1],
            "description": args[2],
            "badge": args[3],
            "reference_url": args[4],
            "delivery_context": args[5],
        }

    authored_content = extract_switch_content(src, masked)

    return {
        "supplemental_modules": supplemental_modules,
        "module_guides": guides,
        "authored_content": authored_content,
    }


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    java_cs = os.path.join(repo_root, "api", "Data", "JavaVerticalSeedData.cs")
    fde_cs = os.path.join(repo_root, "api", "Data", "FdeCurriculumSeedData.cs")
    out_dir = os.path.join(here, "..", "seed", "data")

    java = extract_java(java_cs)
    fde = extract_fde(fde_cs)

    java_lessons = sum(len(v) for v in java["module_lessons"].values())
    java_expanded = sum(len(m["lessons"]) for m in java["expanded_modules"])
    fde_lessons = sum(len(m["lessons"]) for m in fde["supplemental_modules"])
    print(f"java: {len(java['vertical_tasks'])} tasks, "
          f"{java_lessons} module lessons, "
          f"{len(java['study_guide'])} study-guide topics, "
          f"{len(java['expanded_modules'])} expanded modules ({java_expanded} lessons), "
          f"{len(java['authored_content'])} authored bodies")
    print(f"fde: {len(fde['supplemental_modules'])} supplemental modules "
          f"({fde_lessons} lessons), "
          f"{len(fde['module_guides'])} module guides, "
          f"{len(fde['authored_content'])} authored bodies")

    if check_only:
        print("check OK (no files written)")
        return 0

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "java_vertical.json"), "w", encoding="utf-8") as fh:
        json.dump(java, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(os.path.join(out_dir, "fde_curriculum.json"), "w", encoding="utf-8") as fh:
        json.dump(fde, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"wrote {out_dir}/java_vertical.json and {out_dir}/fde_curriculum.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
