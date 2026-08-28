const lessonExerciseAssociations = {
  'java-spring-lld/oop-foundations/01-intro-to-lld': {
    exerciseId: 'java-lld-oop1-trip-state-management'
  },
  'java-spring-lld/oop-foundations/02-oop-1-intro-lab': {
    exerciseId: 'java-lld-oop2-rider-entity'
  },
  'java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation': null,
  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    exerciseId: 'java-lld-oop3-point-threedpoint'
  }
};

export function getLessonExerciseAssociation(courseSlug, moduleSlug, lessonSlug) {
  return lessonExerciseAssociations[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonExerciseAssociations;
