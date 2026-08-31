import { describe, expect, it } from 'vitest';
import { getLessonExerciseAssociation } from '../../data/lessonExerciseAssociations';

describe('lesson exercise associations', () => {
  it('associates the intro to lld lesson with the trip state management exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '01-intro-to-lld'
    )).toEqual({ exerciseIds: ['java-lld-oop1-trip-state-management'] });
  });

  it('associates the oop 1 lab lesson with the rider entity exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '02-oop-1-intro-lab'
    )).toEqual({ exerciseIds: ['java-lld-oop2-rider-entity'] });
  });

  it('associates the polymorphism lesson with all three attached exercises', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '04-oop-3-polymorphism-interfaces'
    )).toEqual({
      exerciseIds: [
        'java-lld-media-file-player',
        'java-lld-oop3-point-threedpoint',
        'java-lld-vehicle-renting'
      ]
    });
  });

  it('does not associate unrelated lessons', () => {
    expect(getLessonExerciseAssociation('java-spring-lld', 'oop-foundations', 'other-lesson')).toBeNull();
  });
});
