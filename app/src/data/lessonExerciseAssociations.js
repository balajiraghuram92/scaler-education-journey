const lessonExerciseAssociations = {
  'java-spring-lld/oop-foundations/01-intro-to-lld': {
    exerciseId: 'java-lld-oop1-trip-state-management'
  },
  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    exerciseId: 'java-lld-oop3-point-threedpoint'
  }
};

export function getLessonExerciseAssociation(courseSlug, moduleSlug, lessonSlug) {
  return lessonExerciseAssociations[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonExerciseAssociations;
