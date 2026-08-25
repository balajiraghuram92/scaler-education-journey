import { describe, expect, it } from 'vitest';
import { getLessonExerciseAssociation } from '../../data/lessonExerciseAssociations';

describe('lesson exercise associations', () => {
  it('associates the polymorphism lesson with the canonical exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '04-oop-3-polymorphism-interfaces'
    )).toEqual({ exerciseId: 'java-lld-oop3-point-threedpoint' });
  });

  it('does not associate unrelated lessons', () => {
    expect(getLessonExerciseAssociation('java-spring-lld', 'oop-foundations', 'other-lesson')).toBeNull();
  });
});
