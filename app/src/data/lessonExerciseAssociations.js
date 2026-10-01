const lessonExerciseAssociations = {
  'java-spring-lld/oop-foundations/01-intro-to-lld': {
    exerciseIds: [
      'java-lld-oop1-trip-state-management'
    ]
  },
  'java-spring-lld/oop-foundations/02-oop-1-intro-lab': {
    exerciseIds: [
      'java-lld-oop2-rider-entity'
    ]
  },
  'java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation': {
    exerciseIds: [
      'java-lld-oop2-point-rectangle',
      'java-lld-shape-hierarchy'
    ]
  },
  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    exerciseIds: [
      'java-lld-media-file-player',
      'java-lld-oop3-point-threedpoint',
      'java-lld-vehicle-renting'
    ]
  },
  'java-spring-lld/oop-foundations/05-oop-4-lms-lab': {
    exerciseIds: [
      'java-lld-scaler-learning-platform-users'
    ]
  },
  'java-spring-lld/concurrency-multithreading/06-concurrency-1-threads': {
    exerciseIds: [
      'java-lld-big-factorial-thread',
      'java-lld-thread-basics-adder-subtractor'
    ]
  },
  'java-spring-lld/concurrency-multithreading/07-concurrency-2-executors': {
    exerciseIds: [
      'java-lld-image-painter-executors'
    ]
  },
  'java-spring-lld/concurrency-multithreading/08-concurrency-3-synchronization': {
    exerciseIds: [
      'java-lld-movie-ticket-reservation',
      'java-lld-synchronized-counter',
      'java-lld-train-reservation-per-class-locks'
    ]
  },
  'java-spring-lld/advanced-java-collections/10-java-adv-1-generics': {
    exerciseIds: [
      'java-lld-bounded-generics-find-max',
      'java-lld-generic-comparison',
      'java-lld-generic-linked-list',
      'java-lld-generic-pair',
      'java-lld-generic-print-array'
    ]
  },
  'java-spring-lld/advanced-java-collections/11-java-adv-2-collections-lab': {
    exerciseIds: [
      'java-lld-frequency-counter',
      'java-lld-group-anagrams',
      'java-lld-unique-persons'
    ]
  },
  'java-spring-lld/advanced-java-collections/12-java-adv-3-lambdas-streams': {
    exerciseIds: [
      'java-lld-count-unique-words',
      'java-lld-distinct-numbers',
      'java-lld-filter-fruits',
      'java-lld-process-sentences',
      'java-lld-sort-animals-by-length',
      'java-lld-student-sorter'
    ]
  },
  'java-spring-lld/design-principles-patterns/14-solid-principles': {
    exerciseIds: [
      'java-lld-cloud-provider-adapter-integration'
    ]
  },
  'java-spring-lld/design-principles-patterns/15-creational-patterns': {
    exerciseIds: [
      'java-lld-abstract-factory-audio',
      'java-lld-abstract-factory-document-processing',
      'java-lld-abstract-factory-notifications',
      'java-lld-builder-database-configuration',
      'java-lld-builder-message',
      'java-lld-builder-query',
      'java-lld-factory-board-game',
      'java-lld-factory-database-connection',
      'java-lld-factory-document',
      'java-lld-prototype-configuration',
      'java-lld-prototype-invoice',
      'java-lld-prototype-user',
      'java-lld-singleton-file-config'
    ]
  },
  'java-spring-lld/design-principles-patterns/16-structural-patterns': {
    exerciseIds: [
      'java-lld-adapter-insurance',
      'java-lld-adapter-social-media',
      'java-lld-adapter-translation',
      'java-lld-decorator-api',
      'java-lld-decorator-file-storage',
      'java-lld-decorator-image',
      'java-lld-facade-booking',
      'java-lld-facade-data-analysis',
      'java-lld-facade-image-editing',
      'java-lld-flyweight-chess-user',
      'java-lld-flyweight-graphics'
    ]
  },
  'java-spring-lld/design-principles-patterns/17-behavioural-patterns-uml': {
    exerciseIds: [
      'java-lld-observer-stock-price-alerts',
      'java-lld-observer-task-assignment',
      'java-lld-observer-weather-monitoring',
      'java-lld-strategy-pricing',
      'java-lld-strategy-stock-trading',
      'java-lld-strategy-video-streaming'
    ]
  },
  'java-spring-lld/applied-machine-coding/19-machine-coding-tictactoe': {
    exerciseIds: [
      'java-lld-tictactoe-undo-and-win-check',
      'java-lld-tictactoe-win-check'
    ]
  },
  'java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot': {
    exerciseIds: [
      'java-lld-generate-parking-ticket',
      'java-lld-display-parking-lot-capacity'
    ]
  },
  'java-spring-lld/applied-machine-coding/21-machine-coding-bookmyshow': {
    exerciseIds: [
      'java-lld-bms-book-ticket'
    ]
  },
  'java-spring-lld/applied-machine-coding/22-machine-coding-splitwise': {
    exerciseIds: [
      'java-lld-splitwise-create-delete-group',
      'java-lld-splitwise-manage-group-members'
    ]
  },
  'java-spring-lld/applied-machine-coding/24-machine-coding-hotel-management': {
    exerciseIds: [
      'java-lld-hotel-add-rooms',
      'java-lld-hotel-book-rooms',
      'java-lld-hotel-generate-invoice',
      'java-lld-hotel-get-rooms'
    ]
  }
};

export function getLessonExerciseAssociation(courseSlug, moduleSlug, lessonSlug) {
  return lessonExerciseAssociations[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonExerciseAssociations;
