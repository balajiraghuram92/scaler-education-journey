# Module 1 — MCQs by Lesson

Multiple-choice questions transcribed from the screenshots in `info/Python-vertical/Lessons/Module-1/Mcqs/`, grouped by the lesson named in each screenshot's page header. Lessons are in class-date order. Within a lesson, questions are split into the page's two sections (**Assignment** and **Additional Problems**), each numbered as on the page (Qn). Options are lettered a, b, c, … in on-screen order. The screenshots show no answers, so none are given.

**128 questions** from 128 screenshots, across 9 lessons.

## Contents

- [MCQs for lesson: Backend LLD: OOP-3: Inheritance, MRO and Polymorphism](#mcqs-for-lesson-backend-lld-oop-3-inheritance-mro-and-polymorphism) — 15 questions
- [MCQs for lesson: Backend LLD: OOP-4: ABCs, Protocols and Mixins](#mcqs-for-lesson-backend-lld-oop-4-abcs-protocols-and-mixins) — 15 questions
- [MCQs for lesson: Backend LLD: OOP-5: Magic Methods and the Python Data Model](#mcqs-for-lesson-backend-lld-oop-5-magic-methods-and-the-python-data-model) — 15 questions
- [MCQs for lesson: Backend LLD: OOP Lab Session](#mcqs-for-lesson-backend-lld-oop-lab-session) — 15 questions
- [MCQs for lesson: Backend LLD: Concurrency-1: Processes, Threads and the GIL](#mcqs-for-lesson-backend-lld-concurrency-1-processes-threads-and-the-gil) — 10 questions
- [MCQs for lesson: Backend LLD: Concurrency-2: Executors and Futures](#mcqs-for-lesson-backend-lld-concurrency-2-executors-and-futures) — 18 questions
- [MCQs for lesson: Backend LLD: Concurrency-3: Synchronization and Async Intro](#mcqs-for-lesson-backend-lld-concurrency-3-synchronization-and-async-intro) — 10 questions
- [MCQs for lesson: Backend LLD: Pythonic-1: Decorators, Iterators and Generators](#mcqs-for-lesson-backend-lld-pythonic-1-decorators-iterators-and-generators) — 20 questions
- [MCQs for lesson: Backend LLD: Pythonic-2: Collections, Dataclasses, Type Hints and Exceptions](#mcqs-for-lesson-backend-lld-pythonic-2-collections-dataclasses-type-hints-and-exceptions) — 10 questions

---

## MCQs for lesson: Backend LLD: OOP-3: Inheritance, MRO and Polymorphism

_Class date: Wed, 08 Jul 2026_

### Assignment

#### Q1. Method Resolution Order (MRO)

Given the hierarchy class A: pass, class B(A): pass, class C(A): pass, class D(B, C): pass, what does D.__mro__ show (ignoring object)? Apply C3 merge — parents in written order, and any ancestor appears after all its descendants.

- **a)** D → A → B → C
- **b)** D → B → C → A
- **c)** D → C → B → A
- **d)** D → B → A → C

<sub>Screenshot: `1.png`</sub>

#### Q2. Duck Typing Silent Bug

In Uber's dispatch code, a function dispatch(vehicle) calls vehicle.start(). A colleague passes in an EmailNotification object (unrelated to Vehicle) which happens to have a .start() method that marks the email as "sending". No error is raised and the email gets marked as sending. Which best explains this per duck typing?

- **a)** Python auto-converted the object into a Vehicle
- **b)** Python only checks whether the method exists on the object at runtime, never what the method means — so wrong-object-right-name bugs run silently
- **c)** dispatch should have raised a TypeError and this is a Python bug
- **d)** EmailNotification must secretly inherit from Vehicle

<sub>Screenshot: `2.png`</sub>

#### Q3. Missing Super Init Call

What will be the output:

```python
class Vehicle:
    def __init__(self, reg): self.reg = reg
class Bike(Vehicle):
    def __init__(self, reg, has_carrier):
        self.has_carrier = has_carrier
b = Bike("KA02", True)
print(b.reg)
```

- **a)** Prints "KA02" — parent __init__ runs automatically
- **b)** Prints None
- **c)** AttributeError — Bike.__init__ never calls super().__init__(), so reg was never set
- **d)** Compile-time error

<sub>Screenshot: `3.png`</sub>

#### Q4. Diamond Inheritance Method Resolution

In the diamond class EC(EV, CV) where EV and CV both define get_priority_score() differently (20 and 30), and EC defines nothing, what does EC().get_priority_score() return, and why?

- **a)** 30 — rightmost parent wins by convention
- **b)** 20 — EV comes before CV in EC's MRO, and Python stops at the first class that defines the method
- **c)** Raises AmbiguityError
- **d)** Returns the sum (50) — Python merges both

<sub>Screenshot: `4.png`</sub>

#### Q5. Method Overloading Myth

What will be the output:

```python
class Fare:
    def calc(self, dist): return 10*dist
    def calc(self, dist, surge): return 10*dist*surge
f = Fare()
print(f.calc(5))
```

- **a)** Prints 50 — Python picks the 1-arg version by overloading
- **b)** Prints 50 — both methods coexist
- **c)** TypeError — the second def replaced the first (Python has no overloading), so calc now needs 2 args
- **d)** Prints None

<sub>Screenshot: `5.png`</sub>

### Additional Problems

#### Q1. MRO Search Order

For class D(B, C) where B and C both inherit from A, in what order does Python search for a method called on a D() instance?

- **a)** D → A → B → C
- **b)** D → B → A → C
- **c)** D → B → C → A
- **d)** D → C → B → A

<sub>Screenshot: `msedge_gpB15xxbQ0.png`</sub>

#### Q2. Understanding super() Semantics

super() in a multiple-inheritance chain refers to:

- **a)** The direct parent class always
- **b)** The next class in the current object's MRO after the class where super() is written
- **c)** The leftmost parent
- **d)** The top-most ancestor

<sub>Screenshot: `msedge_x7eQEXlPOf.png`</sub>

#### Q3. isinstance vs type Check

Given class A: pass, class B(A): pass, an object b = B(). Which is True?

- **a)** type(b) == A → True
- **b)** isinstance(b, A) → True and type(b) == A → False
- **c)** Both are True
- **d)** Both are False

<sub>Screenshot: `msedge_2KZ7j6HUnq.png`</sub>

#### Q4. Duck Typing With Drones

Uber's dispatch(vehicle) calls vehicle.start(). If a totally unrelated Drone class (not inheriting from Vehicle) has a .start() method, what does Python's duck typing say?

- **a)** TypeError — Drone is not a Vehicle
- **b)** Works fine — Python only checks that .start() exists on the passed object
- **c)** Silently returns None
- **d)** Raises NotImplementedError

<sub>Screenshot: `msedge_c9exZm0AXl.png`</sub>

#### Q5. Redefined Method Overwrite

What will be the output:
```python
class N:
    def send(self, m): print("A")
    def send(self, m, r): print("B")
N().send("hi")
```

- **a)** Prints "A"
- **b)** Prints "B"
- **c)** TypeError — missing arg r
- **d)** Prints both

<sub>Screenshot: `msedge_giThLo8VRB.png`</sub>

#### Q6. Missing eq/hash Method

A Zone class defines __lt__ by area. Which of these will NOT work out of the box?

- **a)** sorted(zones)
- **b)** min(zones)
- **c)** zones.sort()
- **d)** zone in some_set (membership test on a set of Zones)

<sub>Screenshot: `msedge_EZwnfKLXsO.png`</sub>

#### Q7. Cooperative Init Chain Behavior

In cooperative multiple inheritance with **kwargs-passing super().__init__ calls, the shared top-most ancestor's __init__:

- **a)** Runs once per parent that inherits it (twice in a diamond)
- **b)** Runs exactly once, because everyone follows the same MRO chain
- **c)** Never runs
- **d)** Runs only if explicitly called by name

<sub>Screenshot: `msedge_DI20WQJukj.png`</sub>

#### Q8. Overload Dispatch Comparison

Which best distinguishes Java overloading from Python's @singledispatch?

- **a)** Both dispatch at compile time
- **b)** Java at compile time based on declared types; @singledispatch at runtime based on actual argument type
- **c)** Both dispatch at runtime
- **d)** @singledispatch dispatches on all arguments, not just the first

<sub>Screenshot: `msedge_0BCY1wc48n.png`</sub>

#### Q9. Skipped Parent Constructor Call

What will be the output:
```python
class A:
    def __init__(self): print("A")
class B(A):
    def __init__(self):
        print("B") # no super() call
b = B()
```

- **a)** A then B
- **b)** B only
- **c)** B then A
- **d)** A only

<sub>Screenshot: `msedge_Jlhq8qnzYi.png`</sub>

#### Q10. Unhashable Type After eq

Defining __eq__ on a class without also defining __hash__ causes:

- **a)** A SyntaxError
- **b)** Instances of the class become unhashable — cannot be used in set or as dict keys
- **c)** No effect at all
- **d)** Python auto-generates a matching __hash__

<sub>Screenshot: `msedge_gTx59NJ4QP.png`</sub>

## MCQs for lesson: Backend LLD: OOP-4: ABCs, Protocols and Mixins

_Class date: Mon, 13 Jul 2026_

### Assignment

#### Q4. Abstract Method Enforcement Check

Uber's checkout team builds a PaymentGateway ABC with @abstractmethod for process_payment and refund. A new developer writes class StripeGateway(PaymentGateway) implementing only process_payment, forgetting refund. They then write s = StripeGateway(). What happens?

- **a)** Object is created, AttributeError only when s.refund() is called later
- **b)** SyntaxError at class definition time
- **c)** TypeError at instantiation — Python refuses to create an object of a class that hasn't implemented all abstract methods
- **d)** Object is created with refund returning None by default

<sub>Screenshot: `msedge_tCsZR5VIzR.png`</sub>

#### Q5. Nominal Vs Structural Typing

Uber integrates a third-party VendorFraudScanner (installed via pip, not editable) that has a scan(amount, location) method. The team defines class FraudChecker(ABC) with @abstractmethod def scan(...). What does isinstance(VendorFraudScanner(), FraudChecker) return, and why?

- **a)** True — ABC checks method presence structurally
- **b)** False — ABC uses nominal typing; the vendor class never inherited from FraudChecker, so it fails regardless of having the right methods
- **c)** True — all classes satisfy any ABC by default
- **d)** Raises TypeError

<sub>Screenshot: `msedge_AvtlZcq2n1.png`</sub>

#### Q6. Protocol Structural Type Check

The team rewrites the fraud contract as @runtime_checkable class FraudCheckable(Protocol) with def scan(self, amount, location) -> bool. Without touching the vendor's code, what does isinstance(VendorFraudScanner(), FraudCheckable) now return?

- **a)** False — Protocol also requires explicit inheritance
- **b)** True — Protocol uses structural typing; it checks whether the object has a matching scan method, regardless of inheritance
- **c)** Raises NotImplementedError
- **d)** True only if @runtime_checkable is removed

<sub>Screenshot: `msedge_Jv4VCVh8Ux.png`</sub>

#### Q7. Multiple Mixin Method Resolution

RazorpayGateway is declared as class RazorpayGateway(PaymentGateway, LoggingMixin, JSONSerializableMixin). Both PaymentGateway and LoggingMixin define a method called describe(). When razorpay.describe() is called, whose version runs?

- **a)** PaymentGateway's — it comes before LoggingMixin in the MRO because it was listed first in the class declaration
- **b)** LoggingMixin's — mixins always take priority
- **c)** Python raises AmbiguityError
- **d)** Both run sequentially

<sub>Screenshot: `msedge_USOZeeoa22.png`</sub>

#### Q8. Silent Registry Skip Behavior

PaymentGateway uses __init_subclass__ with a gateway_name keyword to auto-register subclasses into PaymentGateway.registry. A new developer adds PaytmGateway but forgets gateway_name=... in the class declaration. What happens?

- **a)** TypeError — gateway_name is required
- **b)** registry auto-generates a name from the class name
- **c)** __init_subclass__ doesn't run at all
- **d)** The class is created normally, but it is NOT added to registry (the if gateway_name: guard skips it silently)

<sub>Screenshot: `msedge_ZODkThXz5L.png`</sub>

### Additional Problems

#### Q1. Abstract Method Instantiation Guarantee

What does @abstractmethod on a method inside an ABC subclass guarantee?

- **a)** The method runs automatically when the object is created
- **b)** Any subclass that does not implement this method cannot be instantiated — TypeError at object creation
- **c)** The method is private and inaccessible from outside
- **d)** The method is optimized for performance

<sub>Screenshot: `msedge_XXBjnPhhdV.png`</sub>

#### Q2. Inherited Abstract Method Satisfaction

A PaymentGateway ABC has two abstract methods. StripeGateway inherits from it and implements both. StripeGateway is then subclassed by StripeGatewayV2 which adds a new method but does NOT re-implement the abstract ones. Can StripeGatewayV2() be instantiated?

- **a)** No — each subclass must re-implement all abstract methods
- **b)** Only if StripeGatewayV2 explicitly calls super()
- **c)** Only if StripeGatewayV2 also inherits from ABC
- **d)** Yes — StripeGateway already satisfied the contract, and StripeGatewayV2 inherits those implementations

<sub>Screenshot: `msedge_T3kCzDaBJY.png`</sub>

#### Q3. Protocol Runtime Check Requirement

A Protocol is defined without @runtime_checkable. What happens when you call isinstance(some_obj, MyProtocol)?

- **a)** Returns True if methods match
- **b)** Returns False always
- **c)** TypeError — isinstance requires @runtime_checkable to work with Protocols
- **d)** Works normally — @runtime_checkable is only for static checkers

<sub>Screenshot: `msedge_69dLOGZMom.png`</sub>

#### Q4. Purpose Of Mixin Classes

A mixin named TimestampMixin adds a created_at attribute. It is designed to be combined via multiple inheritance. Which statement is true about mixins, per the lecture?

- **a)** Mixins represent an "is-a" relationship
- **b)** Mixins should be instantiated directly and used standalone
- **c)** Mixins must inherit from ABC
- **d)** Mixins add focused, reusable capabilities — never meant to be instantiated alone, combined via multiple inheritance

<sub>Screenshot: `msedge_vRVEUApzvx.png`</sub>

#### Q5. Subclass Definition Hook Timing

__init_subclass__ runs:

- **a)** Every time an instance of the class is created (__init__ equivalent for classes)
- **b)** Automatically when a new subclass is defined — at class-definition time, not at instance-creation time
- **c)** Only when explicitly called with super().__init_subclass__()
- **d)** Only in metaclasses

<sub>Screenshot: `msedge_Cvn4vDxSW6.png`</sub>

#### Q6. Multiple Parent Method Priority

class RGW(PaymentGateway, LoggingMixin, JSONMixin) — all three parents define describe(). Whose version does RGW().describe() call?

- **a)** LoggingMixin's — mixins override everything
- **b)** JSONMixin's — last parent wins
- **c)** PaymentGateway's — it appears first in the MRO after RGW itself
- **d)** All three run in sequence

<sub>Screenshot: `msedge_d4YOVSo4Fp.png`</sub>

#### Q7. Class Type Hierarchy

The type() of an ordinary Python class (e.g., type(str)) is:

- **a)** object
- **b)** type
- **c)** ABCMeta
- **d)** classmethod

<sub>Screenshot: `msedge_sVSSN7djwL.png`</sub>

#### Q8. Abstract Method Name-Only Check

An ABC defines @abstractmethod def validate(self). A subclass implements validate but with a different signature (def validate(self, strict=False)). Can the subclass be instantiated?

- **a)** Yes — Python only checks that a method with the name validate exists on the subclass, not its exact signature
- **b)** No — signatures must match exactly
- **c)** Only if strict has a default value
- **d)** Raises TypeError at class definition

<sub>Screenshot: `msedge_pqxHQuoOvq.png`</sub>

#### Q9. Nominal Vs Structural Typing Distinction

Which is the key difference between nominal typing (ABC) and structural typing (Protocol)?

- **a)** Nominal checks method presence; structural checks inheritance
- **b)** They are the same mechanism with different names
- **c)** Structural typing does not support isinstance
- **d)** Nominal requires the class to explicitly declare lineage via inheritance; structural only checks whether the required methods exist on the object

<sub>Screenshot: `msedge_9MQ2Qqo3Yn.png`</sub>

#### Q10. Optional Keyword Registration Guard

PaymentGateway uses __init_subclass__ with gateway_name keyword. A developer writes class TestGateway(PaymentGateway) (no gateway_name). Which is true?

- **a)** TypeError — missing required keyword
- **b)** __init_subclass__ still runs, but the if gateway_name: guard means the class is NOT added to registry — it exists as a normal subclass
- **c)** __init_subclass__ does not run at all
- **d)** registry stores it under the key None

<sub>Screenshot: `msedge_8vU5d61Hqu.png`</sub>

## MCQs for lesson: Backend LLD: OOP-5: Magic Methods and the Python Data Model

_Class date: Wed, 15 Jul 2026_

### Assignment

#### Q1. Default Identity-Based Equality

Uber's Driver class originally has no custom dunders. A dispatcher writes d1 = Driver("Ramesh", 4.8, driver_id="D101") and d2 = Driver("Ramesh", 4.8, driver_id="D101") — two separately-loaded copies of the same real driver record. Without any __eq__ defined, what does d1 == d2 evaluate to, and why?

- **a)** True — Python compares all attributes by default
- **b)** True — because driver_id matches
- **c)** Raises TypeError — objects can't be compared without __eq__
- **d)** False — the default __eq__ is an identity check (same object in memory), not a content check

<sub>Screenshot: `msedge_hItskLqCg2.png`</sub>

#### Q2. Custom Eq Hash Conflict

After adding def __eq__(self, other): return self.driver_id == other.driver_id to Driver (with no hash defined), a dispatch engineer runs online_drivers = {d1, d2}. What happens, and why?

- **a)** Works fine — Python auto-generates a matching __hash__ from __eq__
- **b)** TypeError: unhashable type — defining __eq__ sets __hash__ to None automatically, since a hash based on identity would now contradict content-based equality
- **c)** Silently creates two separate entries in the set
- **d)** AttributeError — sets require a driver_id attribute

<sub>Screenshot: `msedge_OBE53anKtu.png`</sub>

#### Q3. Repr Fallback For Str

A class defines only __repr__, no __str__. A developer runs print(some_object). What is printed?

- **a)** The default memory address, ignoring __repr__
- **b)** TypeError — print() requires __str__
- **c)** The __repr__ output — __str__'s default implementation falls back to calling __repr__
- **d)** An empty string

<sub>Screenshot: `msedge_CfwaWLkxR7.png`</sub>

#### Q4. Context Manager Exception Propagation

Inside a with TripTimer(trip) as t: block, a ValueError is raised (not the TripCancelledError that __exit__ explicitly checks for and returns True on). What happens?

- **a)** __exit__ never runs since the exception isn't the one it checks for
- **b)** The ValueError is silently swallowed just like TripCancelledError
- **c)** Python skips straight to the next line after the with block, ignoring the error entirely
- **d)** __exit__ runs (cleanup/logging happens), returns False since the type doesn't match, and the ValueError propagates normally after cleanup

<sub>Screenshot: `msedge_P3hiRKaaAu.png`</sub>

#### Q5. Callable Objects Configuration Benefit

A SurgePricing class is configured once via __init__(multiplier, base_fare) and defines __call__(self, distance). A developer then writes surge = SurgePricing(15, 50) followed by fare = surge(4.2). What allows surge(4.2) to work syntactically, and what's the main benefit over a plain function calculate_surge(distance, multiplier, base_fare)?

- **a)** __call__ button; benefit is it's always faster than a function
- **b)** __call__ button; benefit is the object remembers configuration (multiplier, base_fare) across calls, so each call only needs what actually varies
- **c)** __init__ is called again each time; no real benefit over a function
- **d)** This is invalid syntax — objects cannot be called like functions in Python

<sub>Screenshot: `msedge_C3xK7eYV66.png`</sub>

### Additional Problems

#### Q1. Repr Fallback When Missing

Uber's Trip class defines __repr__ but not __str__. What is the output of print(trip)?

- **a)** Raises TypeError since print() requires __str__
- **b)** The default <Trip object at 0x…> memory address
- **c)** The __repr__ output, since __str__ falls back to __repr__ when undefined
- **d)** An empty string, since __str__ is missing

<sub>Screenshot: `msedge_QV3JBZDhKC.png`</sub>

#### Q2. Hash Disabled After Eq

A Vehicle class overrides __eq__ to compare by reg_number, but never defines __hash__. A developer runs Vehicle.__hash__ in the REPL. What does it show?

- **a)** A working hash function inherited from object
- **b)** None — Python automatically disables hashing when __eq__ is overridden without a matching __hash__
- **c)** AttributeError
- **d)** A function that always returns 0

<sub>Screenshot: `msedge_uaeiQVEunm.png`</sub>

#### Q3. Consistent Hash Equality Check

Two Driver objects d1 and d2 have the same driver_id. __eq__ compares by driver_id, and __hash__ is defined as return hash(self.driver_id). What is d1 in {d2}?

- **a)** False — different objects in memory
- **b)** Raises TypeError
- **c)** True only if d1 is d2
- **d)** True — equal objects hash to the same "shelf," so membership lookup finds it

<sub>Screenshot: `msedge_zsB0j0bsxe.png`</sub>

#### Q4. Operator Overloading Under Hood

a + b on custom objects is secretly routed through which mechanism?

- **a)** Python parses + as raw syntax with no method call involved
- **b)** a.__add__(b) — operators are method calls "wearing a costume"
- **c)** A hidden compiler-level operation invisible to the data model
- **d)** b.__add__(a) always, regardless of order

<sub>Screenshot: `msedge_DDymgZy4QU.png`</sub>

#### Q5. Hash Equality Contract Safeguard

Why does Python set __hash__ to None automatically the instant a class defines __eq__ (without also defining __hash__)?

- **a)** It's an arbitrary restriction with no real reason
- **b)** To force you to also implement __str__
- **c)** Because the default identity-based hash would now disagree with your new content-based equality — letting "equal" objects land on different hash "shelves," silently breaking sets/dicts
- **d)** To improve performance of the class

<sub>Screenshot: `msedge_nG1DWZInE0.png`</sub>

#### Q6. Exit Always Runs Rule

Inside a with Resource() as r: block that raises an exception, which statement is TRUE about __exit__?

- **a)** __exit__ is skipped entirely if an exception occurs
- **b)** __exit__ always runs, exception or not; its return value (True/False) decides whether the exception is suppressed or re-raised
- **c)** __exit__ only runs if the exception is caught elsewhere first
- **d)** __exit__ runs only on the normal (non-exception) exit path

<sub>Screenshot: `msedge_6SXSLw1nQu.png`</sub>

#### Q7. Slice Object Delegation

A class defines __getitem__ by delegating to an internal list (return self._data[index]) but does NOT write any special slicing logic. What happens when a user calls obj[:2]?

- **a)** TypeError — slicing requires a separate __slice__ method
- **b)** Works correctly — the slice object is passed through to the internal list, which already knows how to slice itself
- **c)** Returns None
- **d)** Only single-index access works; slicing always fails

<sub>Screenshot: `msedge_HLMTUsu4Ey.png`</sub>

#### Q8. Callable Object Design Tradeoff

A SurgePricing object is configured with multiplier and base_fare, then used as surge(4.2). Which dunder makes this possible, and what's the risk of overusing this pattern?

- **a)** __call__; risk is that readers may assume it's a plain function and be confused it carries hidden state — use only when the object genuinely represents "a function with memory"
- **b)** __init__; no risk, it's always safe
- **c)** __getattr__; no meaningful risk
- **d)** __new__; risk of infinite recursion

<sub>Screenshot: `msedge_LqrkTPBnYs.png`</sub>

#### Q9. Membership Operator Auto-Dispatch

A class defines __contains__ for membership tests (x in obj). Which best describes when Python calls it?

- **a)** Only when explicitly invoked as obj.__contains__(x)
- **b)** Never — in only works on built-in types
- **c)** Only inside for loops
- **d)** Automatically, whenever the in operator is used on an instance of that class

<sub>Screenshot: `msedge_5p4n4em3hz.png`</sub>

#### Q10. Purposeful Dunder Method Design

Which of these is the most accurate summary of the "one rule" for deciding whether to add a dunder method to a class?

- **a)** Add as many dunders as possible to make the class feel powerful
- **b)** Only add dunders if the class will be used in a set or dict
- **c)** Add a dunder only when a real caller needs the object to speak Python's existing language (len, in, ==, with) — don't wire buttons nobody presses or create surprising behavior behind familiar syntax
- **d)** Dunders should only be added to classes without any regular methods

<sub>Screenshot: `msedge_gzjknyYIoN.png`</sub>

## MCQs for lesson: Backend LLD: OOP Lab Session

_Class date: Fri, 17 Jul 2026_

### Assignment

#### Q1. ABC Instantiation Enforcement

The User class is an ABC with two abstract methods: display_dashboard and can_borrow. A developer creates class Volunteer(User) implementing only display_dashboard, then runs v = Volunteer("Priya", "p@x.com"). What happens, and which OOP concept is enforcing this?

- **a)** Object is created - Python only checks abstract methods when they're called
- **b)** TypeError at instantiation - ABC (the licence-test rule) refuses to create an object until ALL abstract methods are implemented
- **c)** SyntaxError at class definition time
- **d)** Object is created with can_borrow returning None

<sub>Screenshot: `msedge_wpyfPQP4xU.png`</sub>

#### Q2. Shared Class Attribute Counter

User._id_counter is a class attribute incremented in User.__init__. Three users are created: two Members and one Librarian. What is User._id_counter after all three, and why does it work correctly despite being three different objects across two different subclasses?

- **a)** 1 — each subclass has its own counter
- **b)** 3 — it's a class attribute on User, shared by all subclasses; super().__init__() in each child routes to User.__init__, which increments the single shared counter
- **c)** 2 — Librarian doesn't increment it
- **d)** 0 — class attributes can't be modified inside __init__

<sub>Screenshot: `msedge_cme4xFMRtT.png`</sub>

#### Q3. Nominal Typing With ABCs

lend_item checks isinstance(item, Borrowable) before lending. A third-party AudioGuide class (you can't edit it) happens to have borrow, return item, and is borrowable methods with correct signatures. Will lend_item(AudioGuide(...), member) pass the check?

- **a)** No — Borrowable is an ABC, and isinstance against an ABC checks inheritance (nominal typing), not method presence; AudioGuide never inherited from Borrowable
- **b)** Yes — it has all the right methods
- **c)** Yes — @abstractmethod makes it structural
- **d)** Raises AttributeError

<sub>Screenshot: `msedge_SqfgGxZ5oi.png`</sub>

#### Q4. Protocol Structural Duck Typing

Searchable is defined as a @runtime_checkable Protocol requiring matches(query) -> bool. Book implements matches but does NOT inherit from Searchable. What does isinstance(Novel("N-1","Dune","Herbert","SciFi"), Searchable) return, and why does this differ from Q3?

- **a)** False — Protocol also checks inheritance
- **b)** Raises TypeError — Protocols can't be used with isinstance
- **c)** True — Protocol uses structural typing (checks shape, not lineage), so any object with a matching matches method satisfies it without inheriting
- **d)** True only if Novel explicitly inherits Searchable

<sub>Screenshot: `msedge_oJu0d2sNC4.png`</sub>

#### Q5. Unhashable Type After Eq Definition

Loan defines __eq__ (comparing by book.isbn + member.user_id) but a developer forgets __hash__. They create two Loan objects for the same member/book and run len({l1, l2}). What happens?

- **a)** Returns 1 — Python auto-generates __hash__ from __eq__
- **b)** Returns 2 — duplicates aren't detected
- **c)** Returns 0
- **d)** TypeError: unhashable type 'Loan' — defining __eq__ without __hash__ causes Python to set __hash__ = None, making the object unusable in sets

<sub>Screenshot: `msedge_7wyraB3W3O.png`</sub>

### Additional Problems

#### Q1. Inherited Abstract Method Fulfillment

User is an ABC with abstract methods display_dashboard and can_borrow. Member implements both. PremiumMember(Member) adds a loyalty field but does NOT re-implement either abstract method. Can PremiumMember("X", "x@x") be instantiated?

- **a)** Yes — Member already satisfied the contract, and PremiumMember inherits those implementations
- **b)** No — every subclass must re-implement all abstract methods directly
- **c)** Only if PremiumMember also inherits from ABC
- **d)** Only if PremiumMember calls super()

<sub>Screenshot: `msedge_7v6Hx0eOL5.png`</sub>

#### Q2. Read-Only Property Assignment Blocked

user_id is stored as self._user_id with only a @property getter (no setter). What happens when code runs member.user_id = "NEW"?

- **a)** Overwrites the ID silently
- **b)** ValueError
- **c)** AttributeError — property has no setter, so assignment is blocked
- **d)** Creates a second attribute called user_id on the instance

<sub>Screenshot: `msedge_RFJKPzEWww.png`</sub>

#### Q3. Live Class Attribute Update

Member.MAX_BORROW_LIMIT is a class attribute set to 5. At runtime, Member.MAX_BORROW_LIMIT = 2 is executed. What happens to an existing Member who checks can_borrow()?

- **a)** Unaffected — the old value 5 is frozen at object creation
- **b)** Now uses 2 — class attributes are shared and can_borrow reads Member.MAX_BORROW_LIMIT live at each call
- **c)** AttributeError — constants can't be changed
- **d)** Only new Member objects see 2

<sub>Screenshot: `msedge_SJMt4vdudu.png`</sub>

#### Q4. ABC Nominal Check Fails

A MagazineArchive has a borrow() method (meaning "log a photocopy"). lend_item checks isinstance(item, Borrowable) before calling borrow(). Does the archive pass the check?

- **a)** Yes — duck typing checks methods
- **b)** No — Borrowable is an ABC; isinstance checks inheritance, and MagazineArchive never inherited from Borrowable
- **c)** Yes — Borrowable is a Protocol
- **d)** Raises NotImplementedError

<sub>Screenshot: `msedge_cWZAMnwVMm.png`</sub>

#### Q5. Protocol Passes Without Inheritance

Searchable is a @runtime_checkable Protocol. A third-party JournalDB class (uneditable) has matches(query) -> bool. Does isinstance(JournalDB(), Searchable) return True?

- **a)** No — Protocol also checks inheritance
- **b)** Only if JournalDB explicitly inherits Searchable
- **c)** Yes — @runtime_checkable Protocol checks shape (structural typing); JournalDB has a matching matches method
- **d)** Raises TypeError

<sub>Screenshot: `msedge_N48XqnSqRp.png`</sub>

#### Q6. Determine Super Order

Loan.__init__ calls super().__init__() where Loan inherits from TimestampedMixin. TimestampedMixin.__init__ also calls super().__init__(**kwargs). What determines the order of these calls?

- **a)** Alphabetical order of parent class names
- **b)** The MRO (Method Resolution Order) — super() means "next in the MRO," not "my parent"
- **c)** The order they appear in the source file
- **d)** Python picks randomly

<sub>Screenshot: `msedge_UMdH2XoKVx.png`</sub>

#### Q7. In Operator Under Hood

Library defines __contains__(self, isbn) checking against internal _books. What does "N-1" in lib do under the hood?

- **a)** Searches lib.__dict__ for a key "N-1"
- **b)** Calls lib.__getitem__("N-1")
- **c)** Calls lib.__contains__("N-1"), which iterates _books checking isbn matches
- **d)** Raises TypeError — in only works with built-in types

<sub>Screenshot: `msedge_RDBbrDxqb7.png`</sub>

#### Q8. Encapsulation Vs Centralized Policy

In the code review, Design A has Book.borrow(member) owning lending logic. Design B has Library.lend(member, book) owning it. Which statement best captures the trade-off?

- **a)** Design A is always better because it follows OOP
- **b)** Design B is always better because it's simpler
- **c)** There is no meaningful difference
- **d)** Design A keeps behaviour with its data (encapsulation) but spreads policy across classes; Design B centralizes policy but risks the Library becoming a god object reaching into internals

<sub>Screenshot: `msedge_ynhvp7F854.png`</sub>

#### Q9. Set Deduplication Via Eq

Book.__eq__ compares by isbn. Two books with different titles but same isbn are added to a set. How many entries does the set contain?

- **a)** 1 — __eq__ says they're equal, __hash__ (also by isbn) puts them on the same shelf, so the set deduplicates
- **b)** 2 — different titles means different objects
- **c)** 0 — the set rejects both
- **d)** Depends on insertion order

<sub>Screenshot: `msedge_2ibbBcGdaS.png`</sub>

#### Q10. Slicing Delegates To List

Library defines __getitem__ delegating to self._books[index] but writes NO slicing logic. A user runs lib[:2]. What happens?

- **a)** TypeError — slicing requires a separate __slice__ method
- **b)** Works correctly — the slice is passed through to the internal list, which already handles slicing
- **c)** Returns None
- **d)** Returns only the first element

<sub>Screenshot: `msedge_sF0tUpcQPa.png`</sub>

## MCQs for lesson: Backend LLD: Concurrency-1: Processes, Threads and the GIL

_Class date: Mon, 20 Jul 2026_

### Assignment

#### Q4. difference between concurrency and parallelism?

What is the main difference between concurrency and parallelism?

- **a)** Concurrency needs multiple CPU cores; parallelism doesn't
- **b)** Concurrency is switching between tasks to make progress on all of them; parallelism is tasks actually running at the same instant
- **c)** They are the same thing, just different names
- **d)** Parallelism only applies to Python; concurrency applies to all languages

<sub>Screenshot: `msedge_dUyAXicfyF.png`</sub>

#### Q5. What will this print?

What will this print?

```python
t1 = threading.Thread(target=notify_driver, args=("D101",))
t1.start()
print("Main thread is done!")
```

- **a)** "Main thread is done!" always prints after notify_driver finishes
- **b)** notify_driver never runs because .join() was skipped
- **c)** This code throws an error because .join() was not called
- **d)** "Main thread is done!" prints almost immediately, likely before notify_driver finishes

<sub>Screenshot: `msedge_8sX7O9JTLq.png`</sub>

#### Q6. what does .join() do?

In Python's threading module, what does .join() do?

- **a)** Merges two threads into one
- **b)** Starts a thread that was created but not yet running
- **c)** Pauses the calling code until that specific thread has finished
- **d)** Kills the thread immediately

<sub>Screenshot: `msedge_l3k9zNCq7u.png`</sub>

#### Q7. A student wrote:

A student wrote:
```python
t1 = threading.Thread(target=notify_driver, args=("D101"))
t1.start()
```
This crashes with a TypeError about arguments not being iterable correctly. What's the mistake?

- **a)** target should be a string, not a function reference
- **b)** args is missing a trailing comma — ("D101") is just a string, not a one-item tuple, so Python tries to unpack each character as a separate argument
- **c)** .start() must be called before target is assigned
- **d)** notify_driver cannot accept any arguments

<sub>Screenshot: `msedge_sRTGJ1sdZj.png`</sub>

#### Q8. Given a single CPU-bound function

Given a single CPU-bound function cpu_heavy() that takes 4 seconds to run alone, what is the most likely total time if it's run twice using two threading.Thread instances (started and joined) on a machine with free cores?

- **a)** About 8 seconds — roughly the same as running both sequentially, since the GIL prevents real parallel CPU execution
- **b)** About 4 seconds total, since threads run in true parallel
- **c)** About 2 seconds (threads split the CPU work evenly)
- **d)** Less than 1 second, since threads always speed up computation

<sub>Screenshot: `msedge_itlPPUmi8b.png`</sub>

### Additional Problems

#### Q2. GIL (Global Interpreter Lock) actually guarantee?

What does the GIL (Global Interpreter Lock) actually guarantee?

- **a)** That your shared variables will always update correctly across threads
- **b)** That only one thread can execute Python bytecode at a time, and each individual bytecode instruction runs without interruption
- **c)** That threads always run in the order they were started
- **d)** That CPU-bound tasks will run faster with more threads

<sub>Screenshot: `msedge_MKIXYcyKnj.png`</sub>

#### Q3. Two threads both run this function, then the final value is printed:

Two threads both run this function, then the final value is printed:

```python
counter = 0
def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1
```

What is the most likely printed value after both threads finish?

- **a)** Always exactly 2,000,000
- **b)** Always exactly 1,000,000
- **c)** Some number less than 2,000,000, and it may differ each time the program runs
- **d)** The program crashes with a RuntimeError

<sub>Screenshot: `msedge_82UsDXbJFE.png`</sub>

#### Q4. scenario in H2 happen

Why does the scenario in H2 happen even though the GIL only lets one thread run at a time?

- **a)** counter += 1 is actually four separate bytecode steps, and the GIL can switch threads between those steps, not just between lines
- **b)** The GIL doesn't apply to loops
- **c)** global variables are not protected by the GIL at all
- **d)** Python re-runs the loop twice by mistake

<sub>Screenshot: `msedge_zRb1X4uxcQ.png`</sub>

#### Q5. threading and multiprocessing

A student wants to speed up a task that makes 5 slow network API calls (each takes 1 second, mostly spent waiting). They're deciding between threading and multiprocessing. What should they pick, and why?

- **a)** multiprocessing, because it always beats threading for any task
- **b)** threading, because I/O-bound waits release the GIL, letting waits overlap — cheaper than spinning up separate processes
- **c)** Neither will help; only rewriting the API calls can speed this up
- **d)** multiprocessing, because network calls are CPU-bound

<sub>Screenshot: `msedge_zaPBPUXAkD.png`</sub>

#### Q6. difference in output/behavior

What is the key difference in output/behavior between using raw multiprocessing.Process objects versus multiprocessing.Pool.map() for running the same function on 4 inputs?

- **a)** Process automatically collects and returns results in a list; Pool.map() does not
- **b)** Pool.map() runs the function sequentially, while Process runs it in parallel
- **c)** Process requires manually creating, starting, and joining each process with no built-in result collection, while Pool.map() handles all of that and returns results in order automatically
- **d)** There is no real difference; Pool is just a shorter way to write Process

<sub>Screenshot: `msedge_qKoJj3Hudz.png`</sub>

## MCQs for lesson: Backend LLD: Concurrency-2: Executors and Futures

_Class date: Wed, 22 Jul 2026_

### Assignment

#### Q2. executor.submit(fn, arg)

What does executor.submit(fn, arg) return?

- **a)** None, until the task finishes
- **b)** The result of fn(arg) directly
- **c)** A new thread object
- **d)** A Future object representing work in progress

<sub>Screenshot: `msedge_tqOvhbZj8H.png`</sub>

#### Q3. `.done()` and `.result()`

Which statement about .done() and .result() is correct?

- **a)** .done() never blocks; .result() blocks until the result is available
- **b)** Both block until the task finishes
- **c)** .done() blocks; .result() never blocks
- **d)** Both return True/False depending on task status

<sub>Screenshot: `msedge_VHU0IXLtKC.png`</sub>

#### Q4. `threading.Thread`'s target function

A raw threading.Thread's target function raises an exception. What happens?

- **a)** The thread silently retries the function
- **b)** The exception prints to the terminal but the main thread has no way to catch or react to it
- **c)** The program crashes immediately
- **d)** The exception propagates to the main thread automatically

<sub>Screenshot: `msedge_sKS0MhbBkk.png`</sub>

#### Q5. `Future` handle an exception

How does a Future handle an exception raised inside the worker function?

- **a)** It ignores the exception completely
- **b)** It crashes the executor immediately
- **c)** It logs the exception and returns None
- **d)** It stores the exception and re-raises it when .result() is called

<sub>Screenshot: `msedge_LkBGudEnbX.png`</sub>

#### Q6. executor.map(fn, iterable)

What guarantee does executor.map(fn, iterable) give you about result order?

- **a)** Only the first completed result is returned
- **b)** Order is undefined/random
- **c)** Results come back in the same order as the input iterable, regardless of finish order
- **d)** Results come back in the order tasks finish

<sub>Screenshot: `msedge_2m7YZCu3Bq.png`</sub>

#### Q7. python -What will this print?

What will this print?

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task():
    time.sleep(2)
    return "done"

with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(task)
    print(future.done())
```

- **a)** done
- **b)** Raises an error
- **c)** True
- **d)** False

<sub>Screenshot: `msedge_CdolGIAJgh.png`</sub>

#### Q8. python concurrency lecture 2 - What is the output of this code?

What is the output of this code?
```python
from concurrent.futures import ThreadPoolExecutor

def risky(x):
    if x == 3:
        raise ValueError("bad value")
    return x * 2

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(risky, i) for i in range(5)]
    for f in futures:
        try:
            print(f.result())
        except ValueError as e:
            print(f"Caught: {e}")
```

- **a)** Nothing prints — .result() swallows all output
- **b)** 0 2 4 6 8 (errors silently skipped)
- **c)** Program crashes at x == 3 and stops printing
- **d)** 0 2 Caught: bad value 6 8 (in order, exception caught for x=3)

<sub>Screenshot: `msedge_udXtfNbQdT.png`</sub>

#### Q9. A student wrote this to collect driver locations. What does it get wrong relative to today's lecture taught?

A student wrote this to collect driver locations. What does it get wrong relative to what today's lecture taught?
```python
import threading
results = []

def fetch_and_store(driver_id):
    location = fetch_driver_location(driver_id)
    results.append(location)

threads = [threading.Thread(target=fetch_and_store, args=(d,)) for d in drivers]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

- **a)** threading.Thread cannot take args
- **b)** t.join() will deadlock
- **c)** This code will throw a syntax error
- **d)** This works, but relies on a manually shared list instead of ThreadPoolExecutor/Future to collect results and handle errors cleanly

<sub>Screenshot: `msedge_W9Xr0LBC62.png`</sub>

#### Q10. Find the bug: the student wants to catch the error from a failed task, but the `except` block never triggers, even though `fetch_driver_location("D103")` is known to raise `ConnectionError`.

Find the bug: the student wants to catch the error from a failed task, but the except block never triggers, even though fetch_driver_location("D103") is known to raise ConnectionError.
```python
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(fetch_driver_location, "D103")

try:
    print(future.done())
except ConnectionError as e:
    print(f"Fetch failed: {e}")
```

- **a)** The with block suppresses all exceptions
- **b)** ConnectionError cannot be caught inside a with block
- **c)** The exception is only raised when .result() is called — .done() never raises, it only reports status
- **d)** executor.submit doesn't accept string arguments

<sub>Screenshot: `msedge_TxMDu3EtSb.png`</sub>

#### Q11. You're building a system that downloads 100 images from different URLs. Which executor should you use, and why?

You're building a system that downloads 100 images from different URLs. Which executor should you use, and why?

- **a)** ProcessPoolExecutor, because processes don't have a GIL limitation on network calls
- **b)** Neither — use a single thread since downloads must happen one at a time
- **c)** ProcessPoolExecutor, because more workers = more speed always
- **d)** ThreadPoolExecutor, because this is I/O-bound — the GIL releases during network waits, letting waits overlap

<sub>Screenshot: `msedge_C8ymbb6uj0.png`</sub>

### Additional Problems

#### Q1. `ProcessPoolExecutor` over `ThreadPoolExecutor`?

Which is the best use case for ProcessPoolExecutor over ThreadPoolExecutor?

- **a)** Waiting on 5 API calls with sleep/network delay
- **b)** Reading multiple files from disk
- **c)** Performing heavy numerical computation on 4 independent large datasets
- **d)** Fetching 10 web pages concurrently

<sub>Screenshot: `msedge_PJIV2tWaTy.png`</sub>

#### Q2. `ProcessPoolExecutor` speed up an I/O-bound task like web scraping, compared to `ThreadPoolExecutor`

Why doesn't ProcessPoolExecutor speed up an I/O-bound task like web scraping, compared to ThreadPoolExecutor?

- **a)** ProcessPoolExecutor doesn't support .map()
- **b)** The GIL blocks all network calls in processes
- **c)** Processes cannot perform network requests
- **d)** There's no computation to parallelize — the bottleneck is waiting, and processes add extra startup/communication overhead for no benefit

<sub>Screenshot: `msedge_5r58lschFl.png`</sub>

#### Q3. True or False: Using ThreadPoolExecutor automatically protects shared variables from race conditions (like counter += 1 from multiple threads).

True or False: Using ThreadPoolExecutor automatically protects shared variables from race conditions (like counter += 1 from multiple threads).

- **a)** True — executors serialize all writes automatically
- **b)** False — executors only manage task launching/collection; shared-state protection still needs tools like Lock

<sub>Screenshot: `msedge_BCZwfGRmXy.png`</sub>

#### Q4. What is `results`, and in what order, once this finishes?

What is results, and in what order, once this finishes?
```python
import time
from concurrent.futures import ThreadPoolExecutor

def work(n):
    time.sleep(n)
    return n

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(work, [3, 1, 2]))
print(results)
```

- **a)** Raises a TimeoutError
- **b)** [2, 1, 3] — random order
- **c)** [1, 2, 3] — sorted by finish time
- **d)** [3, 1, 2] — same order as input list

<sub>Screenshot: `msedge_xBiG74JDty.png`</sub>

#### Q5. A student benchmarks CPU-heavy work and is confused why threads didn't help. Identify the flaw in their reasoning.

A student benchmarks CPU-heavy work and is confused why threads didn't help. Identify the flaw in their reasoning.

```python
def cpu_heavy(n):
    return sum(i * i for i in range(n))

with ThreadPoolExecutor(max_workers=4) as executor:
    list(executor.map(cpu_heavy, [50_000_000] * 4))
```

"I used 4 workers for 4 tasks, so this should be 4x faster than sequential."

- **a)** max_workers=4 should be max_workers=1 for correctness
- **b)** executor.map doesn't support functions with numeric arguments
- **c)** The code has a syntax error, so it never runs
- **d)** This is CPU-bound work; the GIL means only one thread executes Python bytecode at a time, so threads don't overlap computation — ProcessPoolExecutor is needed instead

<sub>Screenshot: `msedge_0ChHeHejwQ.png`</sub>

#### Q6. You're processing 4 large video files, applying a CPU-intensive filter to each, independently. Which is the better choice and why?

You're processing 4 large video files, applying a CPU-intensive filter to each, independently. Which is the better choice and why?

- **a)** Doesn't matter, both give identical performance
- **b)** ThreadPoolExecutor — video processing is I/O-bound
- **c)** Neither — must be done sequentially
- **d)** ProcessPoolExecutor — CPU-bound work benefits from separate GILs per process, allowing true parallel computation across cores

<sub>Screenshot: `msedge_cTNBVfpcgV.png`</sub>

#### Q7. You submit 10 tasks to a `ThreadPoolExecutor(max_workers=3)`. At any given instant, what is the maximum number of tasks actually running concurrently?

You submit 10 tasks to a ThreadPoolExecutor(max_workers=3). At any given instant, what is the maximum number of tasks actually running concurrently?

- **a)** Depends on task type
- **b)** 1 (due to the GIL)
- **c)** 3
- **d)** 10

<sub>Screenshot: `msedge_slYarM5FBE.png`</sub>

#### Q8. `ThreadPoolExecutor` task that sometimes throws an exception. You use `executor.map()` instead of `submit()`

You have a ThreadPoolExecutor task that sometimes throws an exception. You use executor.map() instead of submit() + individual futures. What happens when you iterate over the results and one task failed?

- **a)** map() cannot raise exceptions, only submit() can
- **b)** map() skips the failed task and continues with the rest
- **c)** The failed task's result is silently None
- **d)** The exception is raised at the point of iteration when you reach that failed task's result, potentially stopping your loop from processing remaining results unless wrapped in try/except

<sub>Screenshot: `msedge_SUTzXZZu3F.png`</sub>

## MCQs for lesson: Backend LLD: Concurrency-3: Synchronization and Async Intro

_Class date: Fri, 24 Jul 2026_

### Assignment

#### Q4. What is a "critical section" in the context of threading.Lock?

What is a "critical section" in the context of threading.Lock?

- **a)** A section of code that never has bugs
- **b)** The block of code that only one thread can execute at a time while holding the lock
- **c)** Any function that uses threads
- **d)** The part of code that runs fastest

<sub>Screenshot: `msedge_6SAVKugd1Y.png`</sub>

#### Q5. `threading.Lock` cause a deadlock

Why does a plain threading.Lock cause a deadlock if the same thread tries to acquire it twice (e.g., a locked function calling another locked function)?

- **a)** The second acquire() call raises an exception immediately
- **b)** Python doesn't allow nested function calls
- **c)** A Lock has no memory of who is holding it, so it just waits forever for a release that never comes from itself
- **d)** Locks can only be used once per program

<sub>Screenshot: `msedge_ubGGpyNAaW.png`</sub>

#### Q6. Python Concurrency 3 - What will this print?

What will this print?

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(50_000):
        with lock:
            counter += 1

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)
```

- **a)** It will raise a deadlock error
- **b)** 50000
- **c)** A random number less than 100,000 each time it runs
- **d)** 100000, every single time

<sub>Screenshot: `msedge_NDZlwdW0UG.png`</sub>

#### Q7. The following code is supposed to safely reserve seats but has a bug. What is wrong?

The following code is supposed to safely reserve seats but has a bug. What is wrong?
```python
import threading

class BookingSystem:
    def __init__(self, seats):
        self.available_seats = seats
        self.lock = threading.Lock()

    def reserve(self, num_seats):
        if self.available_seats >= num_seats:
            with self.lock:
                pass
            self.available_seats -= num_seats
            return True
        return False
```

- **a)** There is no bug, this code is correct
- **b)** reserve should be a @staticmethod
- **c)** threading.Lock() should be threading.RLock()
- **d)** The check (if self.available_seats >= num_seats) and the update (self.available_seats -= num_seats) are NOT both inside the with self.lock: block, so two threads can still race between the check and the update

<sub>Screenshot: `msedge_lkH6RTuqMF.png`</sub>

#### Q8. `outer()` acquires a lock and then calls `inner()`

A function outer() acquires a lock and then calls inner(), which also tries to acquire the same lock, from the same thread. Which tool correctly avoids deadlock here?

- **a)** queue.Queue()
- **b)** threading.Event()
- **c)** threading.RLock()
- **d)** threading.Semaphore(1)

<sub>Screenshot: `msedge_9P2JPwwAqZ.png`</sub>

### Additional Problems

#### Q4. `Semaphore(3)` was used to allow only 3 threads to run at once

In the lecture, a Semaphore(3) was used to allow only 3 threads to run at once (like a parking lot with 3 spots). If instead you initialize Semaphore(0), what happens when a thread immediately calls acquire() on it?

- **a)** It behaves exactly like Semaphore(1)
- **b)** It raises an error because 0 is not allowed
- **c)** It passes through instantly since there's nothing to block
- **d)** It blocks immediately, since there are zero permits available — the thread waits until something else calls release()

<sub>Screenshot: `msedge_yUkuKfcMDy.png`</sub>

#### Q5. For problems like "print first, then second, then third in strict order using multiple threads," why can a semaphore be used to enforce ordering, not just capacity limits?

For problems like "print first, then second, then third in strict order using multiple threads," why can a semaphore be used to enforce ordering, not just capacity limits?

- **a)** Semaphores cannot be used for ordering — only Lock can do this
- **b)** Because semaphores are faster than locks
- **c)** Because acquire() in one thread can be made to wait for a release() called by a different thread, effectively passing a signal/permission from one thread to another
- **d)** Because semaphores automatically sort threads by their function name

<sub>Screenshot: `msedge_LazuP2NqL7.png`</sub>

#### Q6. What is the guaranteed printed order?

What is the guaranteed printed order?
```python
import threading

sem = threading.Semaphore(0)

def waiter():
    sem.acquire()
    print("B")

t = threading.Thread(target=waiter)
t.start()
print("A")
sem.release()
t.join()
```

- **a)** It will hang forever and print nothing
- **b)** B then A, always
- **c)** Random — could be A then B, or B then A
- **d)** A then B, always

<sub>Screenshot: `msedge_fBGp7zlf12.png`</sub>

#### Q7. This is meant to make "second" print only after "first," using semaphores, but it has a bug.

This is meant to make "second" print only after "first," using semaphores, but it has a bug:

```python
import threading

class Foo:
    def __init__(self):
        self.sem = threading.Semaphore(1)  # BUG is here

    def first(self):
        print("first")
        self.sem.release()

    def second(self):
        self.sem.acquire()
        print("second")
```

What is wrong and what's the fix?

- **a)** threading.Semaphore should be threading.Lock
- **b)** The methods first and second should be swapped
- **c)** Semaphore(1) should be Semaphore(0) — since second() must be forced to wait until first() releases it. Starting at 1 lets second() run immediately without waiting
- **d)** second() should call release() instead of acquire()

<sub>Screenshot: `msedge_FMpiRsmmWw.png`</sub>

#### Q8. For the "ZeroEvenOdd" problem (three threads: one prints only 0s, one prints only evens, one prints only odds, in strict interleaved order), which setup is closest to correct?

For the "ZeroEvenOdd" problem (three threads: one prints only 0s, one prints only evens, one prints only odds, in strict interleaved order), which setup is closest to correct?

- **a)** It cannot be done with semaphores; only Condition will work
- **b)** Use time.sleep() with carefully tuned delays to control the order
- **c)** Use one single Lock shared by all three threads with no other coordination
- **d)** Use three separate semaphores — e.g., a zero_sem starting at 1, and even_sem/odd_sem starting at 0 — so each thread's release() signals exactly which thread should run next

<sub>Screenshot: `msedge_wQ1V6aq5dE.png`</sub>

## MCQs for lesson: Backend LLD: Pythonic-1: Decorators, Iterators and Generators

_Class date: Mon, 27 Jul 2026_

### Assignment

#### Q1. First-Class Functions Definition

In Python, what does it mean to say functions are "first-class"?

- **a)** Functions run faster than other code
- **b)** Functions can be stored in variables, passed as arguments, and returned from other functions
- **c)** Functions must always have a return statement
- **d)** Functions are automatically optimized by the interpreter

<sub>Screenshot: `msedge_7PanYpxMNZ.png`</sub>

#### Q2. Function Assignment Without Call

What does this print?
```python
def greet(name):
    return f"Hello, {name}"

say_hello = greet
print(say_hello("Alice"))
```

- **a)** Error: greet is not defined
- **b)** Hello, Alice
- **c)** <function greet>
- **d)** None

<sub>Screenshot: `msedge_eVxKxL0hGy.png`</sub>

#### Q3. Closure Concept Definition

What is a closure?

- **a)** A function that has no parameters
- **b)** A function defined inside another function that remembers variables from the outer function's scope
- **c)** A function that cannot be called more than once
- **d)** A class method that returns self

<sub>Screenshot: `msedge_pwX0bdge7Z.png`</sub>

#### Q4. UnboundLocalError In Closures

Why does this code crash?

```python
def counter():
    count = 0
    def increment():
        count += 1
        return count
    return increment

c = counter()
print(c())
```

- **a)** count was never initialized
- **b)** increment is missing a return statement
- **c)** Assigning to count inside increment makes Python treat it as a new local variable, so it's used before it's set
- **d)** counter() must be called with an argument

<sub>Screenshot: `msedge_98ryHRFaWO.png`</sub>

#### Q5. Decorator Syntax Sugar Explained

What is the correct relationship between @my_decorator and manual wrapping?

- **a)** @my_decorator is faster than manual wrapping
- **b)** @my_decorator above a function is shorthand for func = my_decorator(func)
- **c)** @my_decorator only works on class methods
- **d)** @my_decorator requires functools.wraps to function at all

<sub>Screenshot: `msedge_LxGlSsPGVN.png`</sub>

#### Q6. Decorator Identity Loss Bug

What does add.__name__ print after this?
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def add(a, b):
    """Adds two numbers."""
    return a + b

print(add.__name__)
```

- **a)** add
- **b)** wrapper
- **c)** my_decorator
- **d)** None

<sub>Screenshot: `msedge_e0deVhDAAV.png`</sub>

#### Q7. Universal Wrapper Signature Design

You are writing a decorator that must work on any function, regardless of how many arguments that function takes. What should the wrapper's signature look like?

- **a)** def wrapper():
- **b)** def wrapper(a, b):
- **c)** def wrapper(*args, **kwargs):
- **d)** def wrapper(func):

<sub>Screenshot: `msedge_m05ULWj0iE.png`</sub>

#### Q8. Iterator Protocol Requirements

What two special methods does an object need in order to work as an iterator?

- **a)** __iter__ and __next__
- **b)** __init__ and __str__
- **c)** __call__ and __repr__
- **d)** __get__ and __set__

<sub>Screenshot: `msedge_7zB4hEe2iE.png`</sub>

#### Q9. Custom Iterator Countdown Trace

What is printed by this loop?
```python
class Countdown:
    def __init__(self, start):
        self.current = start
    def __iter__(self):
        return self
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for n in Countdown(3):
    print(n)
```

- **a)** 1 2 3
- **b)** 3 2 1
- **c)** 0 1 2
- **d)** An infinite loop

<sub>Screenshot: `msedge_xxRrL4kSZ1.png`</sub>

#### Q10. For Loop StopIteration Mechanism

Why does a for loop stop automatically without you writing any stopping condition?

- **a)** Python has a hidden loop counter limit
- **b)** The for loop calls __next__ repeatedly and stops when it catches a StopIteration exception
- **c)** Lists in Python have a fixed maximum size
- **d)** The for loop checks len() before each iteration

<sub>Screenshot: `msedge_ti5DD0UQCw.png`</sub>

### Additional Problems

#### Q1. Decorator Factory Extra Layer

Why does a decorator that accepts an argument, like @repeat(3), need one extra layer compared to a normal decorator?

- **a)** Because Python requires exactly three functions in every decorator
- **b)** Because repeat(3) is called first with the setting, and only after that does it receive the function to wrap
- **c)** Because arguments always slow down decorators, so an extra layer is needed for optimization
- **d)** Because functools.wraps requires three layers to work

<sub>Screenshot: `msedge_0Z8l3WNqqd.png`</sub>

#### Q2. Repeat Decorator Execution Count

What does this print?
```python
import functools

def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(2)
def greet():
    print("Hi!")

greet()
```

- **a)** Hi! (printed once)
- **b)** Hi! printed twice
- **c)** Error: repeat() missing arguments
- **d)** Hi! printed three times

<sub>Screenshot: `msedge_UpXknGpZWt.png`</sub>

#### Q3. Stacked Decorator Execution Order

You have this stacked decorator setup:

```python
@bold
@italic
def text():
    return "hello"
```

When text() is called, which decorator's code runs on the outside (first to receive control)?
A) B) C) D)

- **a)** italic, because it's written closer to the function
- **b)** Both run at exactly the same time
- **c)** bold, because it's written on top
- **d)** Neither — only text() runs directly

<sub>Screenshot: `msedge_ELROQpXECC.png`</sub>

#### Q4. Class-Based Decorator State

When would you choose a class-based decorator (using __call__) over a regular function decorator?

- **a)** When the decorator needs to remember and update state across multiple calls
- **b)** Class-based decorators are always faster
- **c)** Function decorators cannot use *args, **kwargs
- **d)** Class-based decorators don't need functools.wraps or update_wrapper

<sub>Screenshot: `msedge_yWYhUJl5hx.png`</sub>

#### Q5. CountCalls Class Decorator Trace

What is printed?
```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count}")
        return self.func(*args, **kwargs)

@CountCalls
def hello():
    print("Hello!")

hello()
hello()
```

- **a)** Call #1 Hello! Call #1 Hello!
- **b)** Hello! Hello!
- **c)** Error: CountCalls object is not callable
- **d)** Call #1 Hello! Call #2 Hello!

<sub>Screenshot: `msedge_U2HnKQOyX9.png`</sub>

#### Q6. Singleton Pattern Closure Storage

In the lecture's @singleton decorator, what makes Config() always return the same object on every call?

- **a)** Python automatically caches all class instances
- **b)** A closure variable (a dictionary) stores the one created instance, and later calls return the stored one instead of creating a new one
- **c)** The @wraps decorator forces single-instance behavior
- **d)** Config overrides __eq__ to compare all instances as equal

<sub>Screenshot: `msedge_oaiNkcxMA8.png`</sub>

#### Q7. Return Vs Yield Behavior

What is the key difference between return and yield inside a function?

- **a)** return pauses the function; yield ends it completely
- **b)** They behave identically, just different syntax
- **c)** yield can only be used inside a class
- **d)** yield pauses the function and remembers where it left off; return ends the function completely

<sub>Screenshot: `msedge_lGgbv1rVQn.png`</sub>

#### Q8. Memory-Efficient Log Processing

You need to process a 10 GB log file on a machine with only 8 GB of RAM. Based on the lecture, what's the correct approach?

- **a)** Use a generator that yields one line at a time, so only one line is in memory at a time
- **b)** Load the whole file into a list using .readlines()
- **c)** Split the file into smaller files first using itertools.chain
- **d)** Increase Python's default memory limit before reading the file

<sub>Screenshot: `msedge_iFt8fKN9Wo.png`</sub>

#### Q9. Islice Infinite Generator Limit

What does this print?

```python
from itertools import islice

def naturals():
    n = 1
    while True:
        yield n
        n += 1

result = list(islice(naturals(), 4))
print(result)
```

- **a)** [1, 2, 3, 4]
- **b)** The program hangs forever
- **c)** [0, 1, 2, 3]
- **d)** Error: naturals() never stops

<sub>Screenshot: `msedge_7NWhXOajb3.png`</sub>

#### Q10. Generator Vs List Memory

Why is sys.getsizeof() so much smaller for a generator expression than for an equivalent list?

- **a)** Generators use a compressed storage format
- **b)** The generator hasn't stored any values — it only holds the "recipe" to produce them one at a time, while the list built and stored every value upfront
- **c)** Generators can only hold numbers, never strings
- **d)** Python deletes generator values automatically after creation

<sub>Screenshot: `msedge_MXkGLMpjJh.png`</sub>

## MCQs for lesson: Backend LLD: Pythonic-2: Collections, Dataclasses, Type Hints and Exceptions

_Class date: Wed, 29 Jul 2026_

### Assignment

#### Q3. Writing the Student Class Cleanly

You need to create a Student class with name and marks attributes for the sorting problem. You want it to have __init__, __repr__, and __eq__ automatically, without typing them by hand. Which approach is correct?

- **a)** Write __init__, __repr__, and __eq__ yourself inside the class
- **b)** Store each student as a plain dict like {"name": ..., "marks": ...}
- **c)** Use a namedtuple, since it also updates marks easily after creation
- **d)** Use @dataclass and declare name: str and marks: int as the fields

<sub>Screenshot: `msedge_C8DaM6YeWp.png`</sub>

#### Q4. Defaultdict Behavior

Consider the following code snippet:
```python
from collections import defaultdict

groups = defaultdict(list)
groups["a"].append(1)
groups["a"].append(2)
groups["b"].append(3)

print(groups["c"])
```
What gets printed?

- **a)** KeyError
- **b)** []
- **c)** None
- **d)** [1, 2]

<sub>Screenshot: `msedge_ZRVV0tgZaw.png`</sub>

#### Q5. Debug Group Anagrams Logic

A student wrote this to group anagrams but it's not grouping correctly:
```python
def group_anagrams(strs):
    groups = {}
    for word in strs:
        key = word          # BUG is here
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return list(groups.values())
```
What is the bug, and how should it be fixed?

- **a)** The key should be sorted(word) converted to a string, so that anagrams map to the same key
- **b)** The bug is using a dict — a list should be used instead
- **c)** The bug is in groups[key].append(word) — it should be groups[key] = word
- **d)** There is no bug; the code is correct as is

<sub>Screenshot: `msedge_Sp4bqwZHWS.png`</sub>

#### Q6. Choosing the Right Tool for Frequency Count

You need to count how many times each word appears in a large paragraph, and then quickly find the 3 most frequent words. Which tool is the most convenient choice?

- **a)** deque
- **b)** namedtuple
- **c)** Counter from collections
- **d)** A plain list with nested loops

<sub>Screenshot: `msedge_YOm1Vuexry.png`</sub>

#### Q7. Generic Compare Function Output

Consider the following code snippet:
```python
def compare(x, y, key=None):
    if key:
        x, y = key(x), key(y)
    if x < y:
        return -1
    elif x > y:
        return 1
    return 0

result = compare(5, 3)
print(result)
```
What does this print?

- **a)** 0
- **b)** -1
- **c)** True
- **d)** 1

<sub>Screenshot: `msedge_ThRmDEo1Uv.png`</sub>

### Additional Problems

#### Q3. Why Use Dataclass?

What is the main benefit of using @dataclass on a class instead of writing it manually?

- **a)** It automatically generates methods like __init__, __repr__, and __eq__ based on the fields you declare
- **b)** It automatically makes the class run faster than a normal class
- **c)** It automatically converts the class into a dictionary
- **d)** It prevents the class from ever being used inside a list

<sub>Screenshot: `msedge_FB7wdhbDET.png`</sub>

#### Q4. Frozen Dataclass Behavior

Consider the following code snippet:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(2, 3)
p.x = 10
print(p.x)
```

What happens when this code runs?

- **a)** It prints 10
- **b)** It raises a FrozenInstanceError
- **c)** It prints 2
- **d)** It raises a TypeError at class definition itself

<sub>Screenshot: `msedge_R5ioda2e26.png`</sub>

#### Q5. Debugging Mutable Default Trap

A student tries to give every Member object an empty list of borrowed books:
```python
from dataclasses import dataclass

@dataclass
class Member:
    name: str
    books: list = []
```
Running this raises an error. What is the correct fix?

- **a)** Change list to tuple and keep = []
- **b)** Remove the type hint list completely
- **c)** Change books: list = [] to books: list = field(default_factory=list)
- **d)** Move books above name in the class

<sub>Screenshot: `msedge_ckf3U1YxPu.png`</sub>

#### Q6. Choosing the Right Exception Approach

You're writing a borrow(book, member) function for a library system. If the book isn't available, you want the caller to know exactly why it failed (not just get a False or a generic error) and be able to catch that specific failure separately from other library errors. What's the best approach?

- **a)** Raise a custom exception like BookNotAvailable that inherits from a base LibraryError class
- **b)** Return False from the function when the book isn't available
- **c)** Print an error message and return None
- **d)** Use a bare except: block inside borrow() to silently ignore the problem

<sub>Screenshot: `msedge_CxQRViZEIP.png`</sub>

#### Q7. Enum Usage and Value Extraction

Consider the following code snippet:

```python
from enum import Enum

class LoanStatus(Enum):
    ACTIVE = "active"
    RETURNED = "returned"

status = LoanStatus.ACTIVE
print(status.value)
```

What is printed?

- **a)** LoanStatus.ACTIVE
- **b)** active
- **c)** ACTIVE
- **d)** It raises an AttributeError

<sub>Screenshot: `msedge_QLCCAhMjRV.png`</sub>

