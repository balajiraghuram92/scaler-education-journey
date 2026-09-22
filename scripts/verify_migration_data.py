import json
import os

def verify():
    paths = [
        r'c:\Users\coforge-rythmos\Documents\raghu\scaler-education-journey\scripts\mcq-migration-data.json',
        r'c:\Users\coforge-rythmos\Documents\raghu\scaler-education-journey\api\Data\mcq-migration-data.json'
    ]

    for p in paths:
        assert os.path.exists(p), f"File missing: {p}"
        size_bytes = os.path.getsize(p)
        print(f"File: {os.path.basename(os.path.dirname(p))}/{os.path.basename(p)} - Size: {size_bytes:,} bytes")
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert isinstance(data, list), "Data must be a JSON array"

    # Deep verification on scripts/mcq-migration-data.json
    with open(paths[0], 'r', encoding='utf-8') as f:
        lessons = json.load(f)

    print(f"\n--- Detailed Verification ---")
    print(f"Total lesson groups: {len(lessons)}")

    total_questions = 0
    legacy_keys = []
    source_counts = {'FROM_MATERIAL': 0, 'LLM_GENERATED': 0}
    total_options = 0

    for l_idx, lesson in enumerate(lessons):
        for field in ['courseSlug', 'moduleSlug', 'lessonSlug', 'questions']:
            assert field in lesson, f"Missing field '{field}' in lesson index {l_idx}"
            assert lesson[field] is not None, f"Null field '{field}' in lesson index {l_idx}"
        
        for q_idx, q in enumerate(lesson['questions']):
            total_questions += 1
            for field in ['legacyKey', 'questionText', 'sourceType', 'explanation', 'options']:
                assert field in q, f"Missing field '{field}' in question {q.get('legacyKey', q_idx)}"
                assert q[field] is not None, f"Null field '{field}' in question {q['legacyKey']}"
            
            assert q['sourceType'] in ('FROM_MATERIAL', 'LLM_GENERATED'), f"Invalid sourceType: {q['sourceType']} in {q['legacyKey']}"
            source_counts[q['sourceType']] += 1
            legacy_keys.append(q['legacyKey'])

            opts = q['options']
            assert isinstance(opts, list) and len(opts) >= 2, f"Options must be a list of >= 2 items in {q['legacyKey']}"
            correct_opts = 0
            for opt in opts:
                total_options += 1
                assert 'optionKey' in opt and opt['optionKey'] is not None, f"Missing optionKey in {q['legacyKey']}"
                assert 'optionText' in opt and opt['optionText'] is not None, f"Missing optionText in {q['legacyKey']}"
                assert isinstance(opt.get('isCorrect'), bool), f"isCorrect must be boolean in {q['legacyKey']}"
                if opt['isCorrect']:
                    correct_opts += 1
            
            assert correct_opts == 1, f"Expected exactly 1 correct option in {q['legacyKey']}, got {correct_opts}"

    unique_keys = set(legacy_keys)
    print(f"Total questions: {total_questions}")
    print(f"Unique legacy keys: {len(unique_keys)}")
    print(f"Total options: {total_options}")
    print(f"Source types breakdown: {source_counts}")
    print(f"All verification checks PASSED perfectly!")

if __name__ == '__main__':
    verify()
