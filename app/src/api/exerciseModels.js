/**
 * @typedef {Object} ExerciseFileMetadata
 * @property {string} id
 * @property {string} path
 * @property {string} displayName
 * @property {boolean} editable
 * @property {string} starterContent
 */

/**
 * @typedef {Object} ExerciseEvidenceMetadata
 * @property {string} id
 * @property {string} label
 */

/**
 * @typedef {Object} ExerciseMetadata
 * @property {string} id
 * @property {string} lessonSlug
 * @property {string} title
 * @property {string} language
 * @property {string} difficulty
 * @property {number} estimatedMinutes
 * @property {string|null} instructions
 * @property {ExerciseFileMetadata[]} files
 * @property {ExerciseEvidenceMetadata[]} evidence
 */

/**
 * @typedef {Object} ExerciseWorkingFile
 * @property {string} id
 * @property {string} path
 * @property {string} displayName
 * @property {boolean} editable
 * @property {string} starterContent
 * @property {string} content
 */

export const EXERCISE_STATUSES = Object.freeze({
  SUCCESS: 'success',
  TEST_FAILURE: 'testFailure',
  COMPILATION_FAILURE: 'compilationFailure',
  TIMEOUT: 'timeout'
});

export const EVIDENCE_STATUSES = Object.freeze({
  NOT_RUN: 'notRun',
  PASSED: 'passed',
  FAILED: 'failed',
  SKIPPED: 'skipped',
  ERROR: 'error'
});

export function normalizeExerciseMetadata(rawMetadata) {
  if (!rawMetadata || !Array.isArray(rawMetadata.files) || !Array.isArray(rawMetadata.evidence)) {
    throw new Error('Exercise metadata is incomplete.');
  }

  const files = rawMetadata.files.map((file) => {
    if (!file?.id || !file.path || typeof file.starterContent !== 'string') {
      throw new Error('Exercise starter files are incomplete.');
    }

    return {
      id: file.id,
      path: file.path,
      displayName: file.displayName || file.path.split('/').pop(),
      editable: file.editable !== false,
      starterContent: file.starterContent
    };
  });

  if (files.length === 0) {
    throw new Error('Exercise metadata contains no editable files.');
  }

  return {
    id: rawMetadata.id,
    lessonSlug: rawMetadata.lessonSlug || '',
    title: rawMetadata.title || 'Coding exercise',
    language: rawMetadata.language || 'java',
    difficulty: rawMetadata.difficulty || '',
    estimatedMinutes: rawMetadata.estimatedMinutes || 0,
    instructions: rawMetadata.instructions || null,
    files,
    evidence: rawMetadata.evidence
      .filter((item) => item?.id && item?.label)
      .map((item) => ({ id: item.id, label: item.label }))
  };
}

export function createWorkingFiles(metadata) {
  return metadata.files.map((file) => ({
    ...file,
    content: file.starterContent
  }));
}

export function getInitialFileId(files) {
  return files.find((file) => file.editable)?.id || files[0]?.id || null;
}

export function getSourceFingerprint(files) {
  return JSON.stringify(files
    .filter((file) => file.editable !== false)
    .map((file) => [file.path, file.content]));
}

export function mergeEvidence(metadataEvidence, resultEvidence = []) {
  const resultById = new Map(resultEvidence.map((item) => [item.id, item]));

  return metadataEvidence.map((item) => {
    const result = resultById.get(item.id);
    return result
      ? { ...item, ...result }
      : { ...item, status: EVIDENCE_STATUSES.NOT_RUN, durationMilliseconds: 0, message: null };
  });
}
