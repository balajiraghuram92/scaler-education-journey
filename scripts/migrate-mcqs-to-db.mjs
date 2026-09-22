#!/usr/bin/env node
/**
 * Standalone Node.js ES module script to migrate practice MCQs from
 * app/src/data/lessonInteractions.js to mcq-migration-data.json.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import lessonInteractions from '../app/src/data/lessonInteractions.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Reads raw text of lessonInteractions.js to extract the sourceType comment
 * (// FROM_MATERIAL, // LLM_GENERATED, // SOURCE_TYPE: ...) immediately preceding
 * each practice question ID.
 *
 * @param {string} rawContent
 * @returns {Map<string, string>}
 */
function extractSourceTypeMap(rawContent) {
  const lines = rawContent.split('\n');
  const sourceMap = new Map();
  let inPracticeQuestions = false;
  let lastComment = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes('conceptChecks:')) {
      inPracticeQuestions = false;
      lastComment = null;
      continue;
    }
    if (line.includes('practiceQuestions:')) {
      inPracticeQuestions = true;
      lastComment = null;
      continue;
    }
    if (inPracticeQuestions) {
      if (line.startsWith('//')) {
        if (line.includes('FROM_MATERIAL')) {
          lastComment = 'FROM_MATERIAL';
        } else if (line.includes('LLM_GENERATED')) {
          lastComment = 'LLM_GENERATED';
        }
        continue;
      }

      const idMatch = line.match(/^\s*id:\s*['"]([^'"]+)['"]/);
      if (idMatch) {
        const id = idMatch[1];
        if (!['a', 'b', 'c', 'd', 'e'].includes(id)) {
          if (lastComment) {
            sourceMap.set(id, lastComment);
            lastComment = null;
          }
        }
      }
    }
  }

  return sourceMap;
}

function main() {
  const rootDir = path.resolve(__dirname, '..');
  const interactionsPath = path.join(rootDir, 'app', 'src', 'data', 'lessonInteractions.js');
  const outputScriptsPath = path.join(__dirname, 'mcq-migration-data.json');
  const outputApiPath = path.join(rootDir, 'api', 'Data', 'mcq-migration-data.json');

  console.log(`Reading raw lesson interactions from: ${interactionsPath}`);
  const rawText = fs.readFileSync(interactionsPath, 'utf-8');

  const sourceMap = extractSourceTypeMap(rawText);
  console.log(`Extracted ${sourceMap.size} source type mappings from raw comments.`);

  const results = [];
  let totalQuestions = 0;
  let fromMaterialCount = 0;
  let llmGeneratedCount = 0;

  for (const [key, interaction] of Object.entries(lessonInteractions)) {
    if (!interaction) continue;

    // Skip backward-compatibility aliases that mirror canonical lessons
    if (key === 'java-spring-lld/oop-foundations/02-oop-classes-objects' ||
        key === 'java-spring-lld/oop-foundations/03-oop2-encapsulation-inheritance') {
      continue;
    }

    const parts = key.split('/');
    if (parts.length !== 3) {
      console.warn(`[WARN] Skipping key with invalid format: ${key}`);
      continue;
    }

    const [courseSlug, moduleSlug, lessonSlug] = parts;
    const practiceQuestions = interaction.practiceQuestions || [];

    const questions = [];
    for (const q of practiceQuestions) {
      const legacyKey = q.id || '';
      const questionText = q.question || '';
      const sourceType = sourceMap.get(legacyKey) || 'FROM_MATERIAL';
      const explanation = q.explanation || '';
      const correctOptionId = q.correctOptionId;

      const options = (q.options || []).map((opt) => ({
        optionKey: opt.id,
        optionText: opt.text,
        isCorrect: opt.id === correctOptionId,
      }));

      if (sourceType === 'FROM_MATERIAL') {
        fromMaterialCount++;
      } else if (sourceType === 'LLM_GENERATED') {
        llmGeneratedCount++;
      }

      totalQuestions++;
      questions.push({
        legacyKey,
        questionText,
        sourceType,
        explanation,
        options,
      });
    }

    results.push({
      courseSlug,
      moduleSlug,
      lessonSlug,
      questions,
    });
  }

  const jsonStr = JSON.stringify(results, null, 2);

  console.log(`Writing ${results.length} lesson groups to: ${outputScriptsPath}`);
  fs.writeFileSync(outputScriptsPath, jsonStr, 'utf-8');

  if (fs.existsSync(path.dirname(outputApiPath))) {
    console.log(`Writing copy to: ${outputApiPath}`);
    fs.writeFileSync(outputApiPath, jsonStr, 'utf-8');
  }

  console.log('\nExtraction Summary:');
  console.log(`  Total Lessons: ${results.length}`);
  console.log(`  Total Questions Extracted: ${totalQuestions}`);
  console.log(`    - FROM_MATERIAL: ${fromMaterialCount}`);
  console.log(`    - LLM_GENERATED: ${llmGeneratedCount}`);
  console.log('Migration data generation completed successfully.');
}

main();
