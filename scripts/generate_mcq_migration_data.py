#!/usr/bin/env python3
"""
Python helper script to extract MCQ data from app/src/data/lessonInteractions.js
and generate scripts/mcq-migration-data.json and api/Data/mcq-migration-data.json.
This mirrors the exact extraction logic of scripts/migrate-mcqs-to-db.mjs.
"""

import json
import os
import re
import sys

class JsParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.len = len(text)
        self.last_comment = None

    def skip_whitespace_and_comments(self):
        while self.pos < self.len:
            if self.text[self.pos].isspace():
                self.pos += 1
                continue
            
            if self.text[self.pos:self.pos+2] == '//':
                start = self.pos
                end = self.text.find('\n', self.pos)
                if end == -1:
                    comment = self.text[start:]
                    self.pos = self.len
                else:
                    comment = self.text[start:end]
                    self.pos = end + 1
                self.last_comment = comment.strip()
                continue
            
            if self.text[self.pos:self.pos+2] == '/*':
                start = self.pos
                end = self.text.find('*/', self.pos + 2)
                if end == -1:
                    self.pos = self.len
                else:
                    self.pos = end + 2
                continue
            
            break

    def peek_char(self):
        self.skip_whitespace_and_comments()
        if self.pos < self.len:
            return self.text[self.pos]
        return None

    def read_char(self):
        self.skip_whitespace_and_comments()
        if self.pos < self.len:
            ch = self.text[self.pos]
            self.pos += 1
            return ch
        raise ValueError(f"Unexpected EOF at pos {self.pos}")

    def expect_char(self, expected):
        ch = self.read_char()
        if ch != expected:
            snippet = self.text[max(0, self.pos - 20):min(self.len, self.pos + 20)]
            raise ValueError(f"Expected '{expected}' but got '{ch}' at pos {self.pos}. Context: {snippet}")

    def parse_string(self):
        self.skip_whitespace_and_comments()
        quote = self.text[self.pos]
        if quote not in ("'", '"', '`'):
            snippet = self.text[max(0, self.pos - 20):min(self.len, self.pos + 20)]
            raise ValueError(f"Expected quote at pos {self.pos}. Context: {snippet}")
        
        self.pos += 1
        chars = []
        while self.pos < self.len:
            ch = self.text[self.pos]
            if ch == '\\':
                self.pos += 1
                if self.pos >= self.len:
                    break
                next_ch = self.text[self.pos]
                if next_ch == 'n':
                    chars.append('\n')
                elif next_ch == 'r':
                    chars.append('\r')
                elif next_ch == 't':
                    chars.append('\t')
                elif next_ch == '\\':
                    chars.append('\\')
                elif next_ch == quote:
                    chars.append(quote)
                elif next_ch == "'":
                    chars.append("'")
                elif next_ch == '"':
                    chars.append('"')
                elif next_ch == '`':
                    chars.append('`')
                else:
                    chars.append('\\' + next_ch)
                self.pos += 1
            elif ch == quote:
                self.pos += 1
                return ''.join(chars)
            else:
                chars.append(ch)
                self.pos += 1
        raise ValueError(f"Unterminated string starting with {quote}")

    def parse_identifier_or_keyword(self):
        self.skip_whitespace_and_comments()
        start = self.pos
        while self.pos < self.len and (self.text[self.pos].isalnum() or self.text[self.pos] in '_$-'):
            self.pos += 1
        return self.text[start:self.pos]

    def parse_value(self):
        self.skip_whitespace_and_comments()
        if self.pos >= self.len:
            return None
        ch = self.text[self.pos]
        if ch in ("'", '"', '`'):
            return self.parse_string()
        if ch == '{':
            return self.parse_object()
        if ch == '[':
            return self.parse_array()
        
        ident = self.parse_identifier_or_keyword()
        if ident == 'true':
            return True
        if ident == 'false':
            return False
        if ident == 'null':
            return None
        if ident.isdigit() or (ident.startswith('-') and ident[1:].isdigit()):
            return int(ident)

        return ident

    def parse_array(self):
        self.expect_char('[')
        items = []
        while True:
            self.skip_whitespace_and_comments()
            if self.peek_char() == ']':
                self.read_char()
                break
            
            pre_comment = self.last_comment
            self.last_comment = None
            val = self.parse_value()
            if isinstance(val, dict) and pre_comment:
                val['__comment__'] = pre_comment
            items.append(val)
            
            self.skip_whitespace_and_comments()
            ch = self.peek_char()
            if ch == ',':
                self.read_char()
                continue
            elif ch == ']':
                self.read_char()
                break
            else:
                snippet = self.text[max(0, self.pos - 20):min(self.len, self.pos + 20)]
                raise ValueError(f"Expected ',' or ']' at pos {self.pos}. Context: {snippet}")
        return items

    def parse_object(self):
        self.expect_char('{')
        obj = {}
        while True:
            self.skip_whitespace_and_comments()
            if self.peek_char() == '}':
                self.read_char()
                break
            
            ch = self.peek_char()
            if ch in ("'", '"', '`'):
                key = self.parse_string()
            else:
                key = self.parse_identifier_or_keyword()
            
            if key == 'get':
                prop_name = self.parse_identifier_or_keyword()
                self.expect_char('(')
                self.expect_char(')')
                self.expect_char('{')
                body_start = self.pos
                depth = 1
                while self.pos < self.len and depth > 0:
                    if self.text[self.pos] == '{':
                        depth += 1
                    elif self.text[self.pos] == '}':
                        depth -= 1
                    self.pos += 1
                body = self.text[body_start:self.pos-1].strip()
                target_match = re.search(r"return\s+lessonInteractions\['([^']+)'\]\.([a-zA-Z0-9_]+);?", body)
                if target_match:
                    target_key = target_match.group(1)
                    target_prop = target_match.group(2)
                    obj[prop_name] = ('__alias__', target_key, target_prop)
                else:
                    obj[prop_name] = ('__getter__', body)
                
                self.skip_whitespace_and_comments()
                if self.peek_char() == ',':
                    self.read_char()
                continue

            self.expect_char(':')
            val = self.parse_value()
            obj[key] = val
            
            self.skip_whitespace_and_comments()
            ch = self.peek_char()
            if ch == ',':
                self.read_char()
                continue
            elif ch == '}':
                self.read_char()
                break
            else:
                snippet = self.text[max(0, self.pos - 20):min(self.len, self.pos + 20)]
                raise ValueError(f"Expected ',' or '}}' at pos {self.pos}. Context: {snippet}")
        return obj


def extract_source_type_map(raw_content):
    """
    Reads raw text of lessonInteractions.js to extract sourceType comment
    preceding each practice question ID.
    """
    source_map = {}
    lines = raw_content.splitlines()
    in_pq = False
    last_comment = None

    for line in lines:
        line_strip = line.strip()
        if 'conceptChecks:' in line_strip:
            in_pq = False
            last_comment = None
            continue
        if 'practiceQuestions:' in line_strip:
            in_pq = True
            last_comment = None
            continue
        
        if in_pq:
            if line_strip.startswith('//'):
                if 'FROM_MATERIAL' in line_strip:
                    last_comment = 'FROM_MATERIAL'
                elif 'LLM_GENERATED' in line_strip:
                    last_comment = 'LLM_GENERATED'
                continue

            m = re.match(r"^\s*id:\s*['\"]([^'\"]+)['\"]", line)
            if m:
                qid = m.group(1)
                if qid not in ['a', 'b', 'c', 'd', 'e']:
                    if last_comment:
                        source_map[qid] = last_comment
                        last_comment = None

    return source_map


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    interactions_path = os.path.join(root_dir, 'app', 'src', 'data', 'lessonInteractions.js')
    output_scripts_path = os.path.join(script_dir, 'mcq-migration-data.json')
    output_api_path = os.path.join(root_dir, 'api', 'Data', 'mcq-migration-data.json')

    print(f"Reading lesson interactions from: {interactions_path}")
    with open(interactions_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    source_map = extract_source_type_map(raw_text)
    print(f"Extracted {len(source_map)} source type mappings from raw comments.")

    start_pos = raw_text.find('const lessonInteractions = {')
    if start_pos == -1:
        raise ValueError("Could not find 'const lessonInteractions = {' in source file.")

    obj_start = raw_text.find('{', start_pos)
    parser = JsParser(raw_text)
    parser.pos = obj_start
    data = parser.parse_object()

    print(f"Parsed {len(data)} lesson interaction entries.")

    results = []
    total_questions = 0
    from_material_count = 0
    llm_generated_count = 0

    for key, interaction in data.items():
        if not isinstance(interaction, dict):
            continue

        parts = key.split('/')
        if len(parts) != 3:
            print(f"[WARN] Key '{key}' does not match courseSlug/moduleSlug/lessonSlug format. Skipping.")
            continue

        course_slug, module_slug, lesson_slug = parts

        pqs = interaction.get('practiceQuestions')
        if isinstance(pqs, tuple) and pqs[0] == '__alias__':
            # Resolve getter alias
            target_key = pqs[1]
            target_prop = pqs[2]
            pqs = data.get(target_key, {}).get(target_prop, [])

        if not isinstance(pqs, list):
            pqs = []

        lesson_questions = []
        for q in pqs:
            legacy_key = q.get('id', '')
            question_text = q.get('question', '')
            source_type = source_map.get(legacy_key)
            if not source_type:
                # Fallback to comment attached to parsed question or default
                comment = q.get('__comment__', '')
                if 'FROM_MATERIAL' in comment:
                    source_type = 'FROM_MATERIAL'
                elif 'LLM_GENERATED' in comment:
                    source_type = 'LLM_GENERATED'
                else:
                    source_type = 'FROM_MATERIAL'

            explanation = q.get('explanation', '')
            correct_option_id = q.get('correctOptionId', '')
            raw_options = q.get('options', [])

            options = []
            for opt in raw_options:
                opt_id = opt.get('id', '')
                opt_text = opt.get('text', '')
                options.append({
                    'optionKey': opt_id,
                    'optionText': opt_text,
                    'isCorrect': opt_id == correct_option_id
                })

            if source_type == 'FROM_MATERIAL':
                from_material_count += 1
            elif source_type == 'LLM_GENERATED':
                llm_generated_count += 1

            total_questions += 1
            lesson_questions.append({
                'legacyKey': legacy_key,
                'questionText': question_text,
                'sourceType': source_type,
                'explanation': explanation,
                'options': options
            })

        results.append({
            'courseSlug': course_slug,
            'moduleSlug': module_slug,
            'lessonSlug': lesson_slug,
            'questions': lesson_questions
        })

    json_str = json.dumps(results, indent=2, ensure_ascii=False)

    print(f"Writing {len(results)} lesson groups to: {output_scripts_path}")
    with open(output_scripts_path, 'w', encoding='utf-8') as f:
        f.write(json_str)

    print(f"Writing copy to: {output_api_path}")
    os.makedirs(os.path.dirname(output_api_path), exist_ok=True)
    with open(output_api_path, 'w', encoding='utf-8') as f:
        f.write(json_str)

    print("\nExtraction Summary:")
    print(f"  Total Lessons: {len(results)}")
    print(f"  Total Questions Extracted: {total_questions}")
    print(f"    - FROM_MATERIAL: {from_material_count}")
    print(f"    - LLM_GENERATED: {llm_generated_count}")
    print("Generation completed successfully.")


if __name__ == '__main__':
    main()
