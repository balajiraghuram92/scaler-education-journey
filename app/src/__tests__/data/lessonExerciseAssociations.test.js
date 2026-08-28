import { describe, expect, it } from 'vitest';
import { getLessonExerciseAssociation } from '../../data/lessonExerciseAssociations';

describe('lesson exercise associations', () => {
  it('associates the intro to lld lesson with the trip state management exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '01-intro-to-lld'
    )).toEqual({ exerciseId: 'java-lld-oop1-trip-state-management' });
  });

  it('associates the oop 1 lab lesson with the rider entity exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '02-oop-1-intro-lab'
    )).toEqual({ exerciseId: 'java-lld-oop2-rider-entity' });
  });

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
