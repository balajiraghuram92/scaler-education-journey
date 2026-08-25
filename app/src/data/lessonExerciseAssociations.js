const lessonExerciseAssociations = {
  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    exerciseId: 'java-lld-oop3-point-threedpoint'
  }
};

export function getLessonExerciseAssociation(courseSlug, moduleSlug, lessonSlug) {
  return lessonExerciseAssociations[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonExerciseAssociations;
