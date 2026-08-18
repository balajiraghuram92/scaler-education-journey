-- PostgreSQL 16 Seed Script for StudyTracker Java LLD & Spring Architecture
-- Inserts Verticals, Courses, Modules, Lessons, Problems, and Study Guide Resources

-- 1. Insert / Update Vertical
INSERT INTO study_verticals (name, description)
VALUES ('Java & Spring Architecture', 'Low-Level Design, Concurrency, Spring Boot & Distributed Enterprise Systems')
ON CONFLICT (name) DO NOTHING;

-- 2. Insert Course
INSERT INTO courses (slug, title, description, order_index, vertical_id)
SELECT 'java-spring-lld', 'Java Low-Level Design & Spring Architecture', 'Mastering Object-Oriented Design, Concurrency, JVM Internals, and Spring Boot Enterprise Architecture.', 1, id
FROM study_verticals WHERE name = 'Java & Spring Architecture'
ON CONFLICT (slug) DO NOTHING;

-- 3. Insert Modules
INSERT INTO course_modules (course_id, slug, title, description, badge, order_index)
SELECT c.id, 'oop-foundations', 'OOP Foundations & Design Principles', 'Core encapsulation, constructor chaining, class hierarchies, polymorphism, and abstraction.', 'Module 1', 1
FROM courses c WHERE c.slug = 'java-spring-lld'
ON CONFLICT (course_id, slug) DO NOTHING;

INSERT INTO course_modules (course_id, slug, title, description, badge, order_index)
SELECT c.id, 'concurrency-multithreading', 'Concurrency & Multithreading', 'Thread lifecycles, race conditions, synchronized blocks, locks, semaphores, and executors.', 'Module 2', 2
FROM courses c WHERE c.slug = 'java-spring-lld'
ON CONFLICT (course_id, slug) DO NOTHING;

INSERT INTO course_modules (course_id, slug, title, description, badge, order_index)
SELECT c.id, 'advanced-java-collections', 'Advanced Java, Collections & Streams', 'Generics, type erasure, collections framework internals, lambda expressions, and functional stream pipelines.', 'Module 3', 3
FROM courses c WHERE c.slug = 'java-spring-lld'
ON CONFLICT (course_id, slug) DO NOTHING;

INSERT INTO course_modules (course_id, slug, title, description, badge, order_index)
SELECT c.id, 'spring-enterprise-architecture', 'Spring Boot & Enterprise Architecture', 'Dependency injection, Spring Data JPA, RESTful API design, PostgreSQL integration, and distributed architectures.', 'Module 4', 4
FROM courses c WHERE c.slug = 'java-spring-lld'
ON CONFLICT (course_id, slug) DO NOTHING;

-- 4. Insert Lesson 3 (OOP-2)
INSERT INTO lessons (module_id, slug, title, description, lecture_number, class_date, content_body, horstmann_ref, estimated_minutes, is_completed, order_index)
SELECT m.id, '03-oop-2-access-modifiers-encapsulation', 'Lesson 3 — OOP-2: Access Modifiers, Encapsulation & Inheritance', 'Deep dive into access levels, constructor overloading and chaining, final semantics, defensive copying, and the equals/hashCode contract.', 3, '2026-06-24',
'# Lesson 3 — OOP-2: Access Modifiers, Encapsulation & Inheritance
Comprehensive guide on object-oriented programming principles in Java, access levels, constructor chaining, and equality contracts.',
'Core Java Vol I Ch. 4 §4.5, Ch. 5 (all), Ch. 6 §6.1/§6.3; Vol II Ch. 5 §5.2', 120, TRUE, 3
FROM course_modules m WHERE m.slug = 'oop-foundations'
ON CONFLICT (module_id, slug) DO NOTHING;

-- 5. Insert OOP-2 Problems
INSERT INTO problems (lesson_id, slug, title, difficulty, package_name, test_class_name, problem_statement, requirements_body, worked_example, hints, is_completed, order_index)
SELECT l.id, 'prb1-immutable-fare', '1. Immutable Fare', 'Warm-up', 'com.assignment.prb1', 'FareTest',
'On a ride-hailing platform the business rule is absolute: the fare shown on screen when the rider taps Accept is the fare they are charged. Make that bug impossible using immutability.',
'Class declared final, all fields private final, no setter methods, withSurge returns new Fare instance.',
'Fare accepted = new Fare(150.0, 1.2, "INR"); Fare surged = accepted.withSurge(2.0);',
'String.format("%.2f", value) for toString. A final class prevents subclass mutability leaks.',
TRUE, 1
FROM lessons l WHERE l.slug = '03-oop-2-access-modifiers-encapsulation'
ON CONFLICT (lesson_id, slug) DO NOTHING;

INSERT INTO problems (lesson_id, slug, title, difficulty, package_name, test_class_name, problem_statement, requirements_body, worked_example, hints, is_completed, order_index)
SELECT l.id, 'prb2-driver-onboarding', '2. Driver Onboarding', 'Easy–Mid', 'com.assignment.prb2', 'DriverTest',
'Drivers onboard via 3 flows. Eliminate initialization duplication using constructor chaining with this(...).',
'driverId is private final, getDriverId is final. Overloaded constructors chain to canonical 4-arg constructor.',
'Driver.resetOnboardedCount(); Driver full = new Driver("D001", "Rahul", 4.8, "9876543210");',
'this(...) must be the first statement in constructor body. Only 4-arg constructor increments counter.',
TRUE, 2
FROM lessons l WHERE l.slug = '03-oop-2-access-modifiers-encapsulation'
ON CONFLICT (lesson_id, slug) DO NOTHING;

INSERT INTO problems (lesson_id, slug, title, difficulty, package_name, test_class_name, problem_statement, requirements_body, worked_example, hints, is_completed, order_index)
SELECT l.id, 'prb3-vehicle-hierarchy', '3. Vehicle Hierarchy', 'Mid', 'com.assignment.prb3', 'VehicleHierarchyTest',
'Dispatch platform manages Cars, Autos, and Bikes. Share common logic in parent Vehicle class and customize base rates via dynamic dispatch.',
'Vehicle parent has private fields and protected double getBaseRate(). Children call super(...) and override getBaseRate().',
'Car car = new Car("V001", "KA01AB1234"); car.calculateFare(10.0); // 120.0',
'super(...) must be first statement in child constructor. Polymorphic dispatch calls child rate.',
TRUE, 3
FROM lessons l WHERE l.slug = '03-oop-2-access-modifiers-encapsulation'
ON CONFLICT (lesson_id, slug) DO NOTHING;

INSERT INTO problems (lesson_id, slug, title, difficulty, package_name, test_class_name, problem_statement, requirements_body, worked_example, hints, is_completed, order_index)
SELECT l.id, 'prb4-trip-copy-semantics', '4. Trip Copy Semantics', 'Mid–Hard', 'com.assignment.prb4', 'TripCopyTest',
'Prevent trip dispute record corruption by implementing deep copying for mutable Route and sharing immutable Money references.',
'Money is immutable (share reference). Route and waypoints are mutable (deep copy). getWaypoints returns unmodifiable list.',
'Trip snapshot = new Trip(original); snapshot.getRoute().setDestination("Hebbal"); // original untouched',
'Mutable field -> deep copy; Immutable field -> share reference.',
TRUE, 4
FROM lessons l WHERE l.slug = '03-oop-2-access-modifiers-encapsulation'
ON CONFLICT (lesson_id, slug) DO NOTHING;

INSERT INTO problems (lesson_id, slug, title, difficulty, package_name, test_class_name, problem_statement, requirements_body, worked_example, hints, is_completed, order_index)
SELECT l.id, 'prb5-equals-hashcode-contract', '5. The equals/hashCode Contract', 'Hard', 'com.assignment.prb5', 'EqualsHashCodeContractTest',
'Fix vanishing HashMap entries by correctly implementing equals() and hashCode() contracts with strict type checking.',
'Driver equals/hashCode on driverId only. Use getClass() != obj.getClass(). PremiumDriver must not equal plain Driver.',
'DriverTripLog log = new DriverTripLog(); log.logTrip(d1, "Koramangala to Whitefield"); log.getTrips(d2);',
'If a.equals(b) is true, a.hashCode() == b.hashCode() MUST be true. Use getClass() for strict symmetry.',
TRUE, 5
FROM lessons l WHERE l.slug = '03-oop-2-access-modifiers-encapsulation'
ON CONFLICT (lesson_id, slug) DO NOTHING;
