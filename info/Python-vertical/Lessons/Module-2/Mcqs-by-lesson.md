# Module 2 — MCQs by Lesson

Multiple-choice questions transcribed from the screenshots in `info/Python-vertical/Lessons/Module-2/Mcqs/`, grouped by the lesson named in each screenshot's page header. Lessons are in class-date order. Within a lesson, questions are split into the page's two sections (**Assignment** and **Additional Problems**), each numbered as on the page (Qn). Options are lettered a, b, c, … in on-screen order. The screenshots show no answers, so none are given.

**167 questions** from 168 screenshots, across 9 lessons.

## Contents

- [MCQs for lesson: Backend LLD: SOLID Principles for Extensible Systems with AI integrations](#mcqs-for-lesson-backend-lld-solid-principles-for-extensible-systems-with-ai-integrations) — 27 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Introduction and Singleton](#mcqs-for-lesson-backend-lld-design-patterns-introduction-and-singleton) — 20 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Builder](#mcqs-for-lesson-backend-lld-design-patterns-builder) — 16 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Prototype and Registry](#mcqs-for-lesson-backend-lld-design-patterns-prototype-and-registry) — 18 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Leveraging Factory Pattern for Service Abstraction.](#mcqs-for-lesson-backend-lld-design-patterns-leveraging-factory-pattern-for-service-abstraction) — 14 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Adapter and Facade](#mcqs-for-lesson-backend-lld-design-patterns-adapter-and-facade) — 16 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Decorator and Flyweight](#mcqs-for-lesson-backend-lld-design-patterns-decorator-and-flyweight) — 16 questions
- [MCQs for lesson: Backend LLD: Design Patterns: Behavioural Design Patterns](#mcqs-for-lesson-backend-lld-design-patterns-behavioural-design-patterns) — 14 questions
- [MCQs for lesson: Backend LLD: UML Diagrams](#mcqs-for-lesson-backend-lld-uml-diagrams) — 26 questions

---

## MCQs for lesson: Backend LLD: SOLID Principles for Extensible Systems with AI integrations

_Class date: Mon, 03 Aug 2026_

### Assignment

#### Q1. Meaning Of Single Responsibility

What does the Single Responsibility Principle (SRP) actually say?

- **a)** A class should have only one method
- **b)** A class should have only one reason to change
- **c)** A class should never inherit from another class
- **d)** A class should only be used once in the program

<sub>Screenshot: `msedge_Ga9XAmOTAk.png`</sub>

#### Q2. Open/Closed Principle Extension

According to the Open/Closed Principle (OCP), how should you add a new feature to an existing class?

- **a)** By editing the class directly to add the new behaviour
- **b)** By adding new code (like a new class), without touching old working code
- **c)** By deleting the old class and rewriting it from scratch
- **d)** By adding more if-elif branches inside the same method

<sub>Screenshot: `msedge_HrwtWeRtKf.png`</sub>

#### Q3. Substitutability Of Subclasses

What does the Liskov Substitution Principle (LSP) require?

- **a)** A subclass should be replaceable in place of its parent, without breaking the program
- **b)** A subclass should have more methods than its parent class
- **c)** A subclass must always override every method of the parent
- **d)** A subclass should never be used directly in code

<sub>Screenshot: `msedge_p5eUGlPlp1.png`</sub>

#### Q4. Interface Segregation Core Idea

What is the core idea behind the Interface Segregation Principle (ISP)?

- **a)** Classes should be forced to implement every method of a shared interface
- **b)** One large interface is always better than many small ones
- **c)** A class should not be forced to depend on methods it doesn't actually use
- **d)** Interfaces should only be used in large-scale applications

<sub>Screenshot: `msedge_LKVIeCOXFV.png`</sub>

#### Q5. Dependency Inversion Core Rule

What does the Dependency Inversion Principle (DIP) say about two concrete classes?

- **a)** They should call each other's methods directly for efficiency
- **b)** They should never depend on each other directly — they should depend on a shared abstraction
- **c)** They should always be combined into a single class
- **d)** One concrete class should always inherit from the other

<sub>Screenshot: `msedge_eqD6PlnTf1.png`</sub>

#### Q6. Rectangle-Square Substitution Trace

What is the output of r.get_area() here?

```python
class Rectangle:
    def __init__(self):
        self.width = 0
        self.height = 0
    def set_width(self, w):
        self.width = w
    def set_height(self, h):
        self.height = h
    def get_area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w

r: Rectangle = Square()
r.set_width(5)
r.set_height(10)
print(r.get_area())
```

- **a)** 50
- **b)** 25
- **c)** 100
- **d)** Raises an error

<sub>Screenshot: `msedge_3mqQb2mjG9.png`</sub>

#### Q7. Penguin Fly Raises Error

What happens when this code runs?

```python
class Bird(ABC):
    def __init__(self, name):
        self.name = name
    def eat(self):
        pass
    @abstractmethod
    def fly(self):
        ...

class Penguin(Bird):
    def fly(self):
        raise NotImplementedError("Penguins can't fly!")

p = Penguin(name="Pingu")
p.fly()
```

- **a)** It runs silently, doing nothing
- **b)** It prints "Penguins can't fly!" and continues normally
- **c)** It raises a NotImplementedError and crashes the program at that line
- **d)** It raises a TypeError because Penguin didn't implement fly()

<sub>Screenshot: `msedge_nJbQheWNeo.png`</sub>

#### Q8. Multiple Jobs In One Method

Which SOLID principle does this code violate, and why?
```python
def save_to_database(self):
    connection = connect()
    query = build_query()
    result = run(query, connection)
    obj = map_to_object(result)
    connection.close()
    return obj
```

- **a)** OCP — because the method can't be extended
- **b)** SRP — because one method is doing five unrelated jobs (connect, build, run, map, close)
- **c)** LSP — because it overrides a parent method incorrectly
- **d)** DIP — because it depends on a concrete database

<sub>Screenshot: `msedge_FKg14rdY36.png`</sub>

#### Q9. Editing Working Code For New Types

What's wrong with this code, and which principle does it break?

```python
def fly(self):
    if self.type == "eagle":
        self.fly_like_eagle()
    elif self.type == "penguin":
        self.fly_like_penguin()
    elif self.type == "parrot":
        self.fly_like_parrot()
```

- **a)** LSP — because eagles and parrots aren't related
- **b)** ISP — because the method has too many parameters
- **c)** OCP — because adding a new bird type means editing this already-working method
- **d)** SRP — because fly() is not a good method name

<sub>Screenshot: `msedge_4mu7hS798I.png`</sub>

#### Q10. Bundled Interface Forces Fake Method

This class was designed for birds that can both fly and dance. What's the problem when Ostrich (which can only dance) inherits from it?

```python
class Performable(ABC):
    @abstractmethod
    def fly(self):
        ...
    @abstractmethod
    def dance(self):
        ...

class Ostrich(Bird, Performable):
    def dance(self):
        pass
    def fly(self):
        pass  # forced to write this even though Ostrich can't fly
```

- **a)** This violates OCP, because Performable cannot be extended
- **b)** This violates ISP, because Ostrich is forced to implement fly(), a method it doesn't need
- **c)** This violates SRP, because Performable has too many method names
- **d)** This is correct design — no principle is violated

<sub>Screenshot: `msedge_rkHao4Bj62.png`</sub>

#### Q11. Order Processing Multiple Jobs

A function process_order() validates the order, charges payment, updates inventory, and sends a confirmation email — all in one function. Which principle does this violate?

- **a)** SRP
- **b)** OCP
- **c)** DIP
- **d)** ISP

<sub>Screenshot: `msedge_MKJPYBccZi.png`</sub>

#### Q12. Editing Existing Discount Logic

A team adds a 6th discount type by adding another elif inside a apply_discount() function that already handles 5 discount types. Which principle is broken?

- **a)** SRP
- **b)** OCP
- **c)** LSP
- **d)** ISP

<sub>Screenshot: `msedge_oD7PFIUVg0.png`</sub>

#### Q13. Fat Interface Forces Fake Methods

A Machine abstract class declares print_doc(), scan(), and fax(). A class SimplePrinter inherits from it but only really prints — it raises NotImplementedError for scan() and fax(). Which principle does this violate?

- **a)** ISP — SimplePrinter is forced to depend on methods it doesn't use
- **b)** DIP — SimplePrinter depends on a concrete class
- **c)** LSP — SimplePrinter is not related to Machine
- **d)** SRP — Machine has too many jobs itself

<sub>Screenshot: `msedge_79UxAHoHCq.png`</sub>

#### Q14. Hardcoded Concrete Dependency

Inside OrderService, this line exists: self.gateway = RazorpayGateway(), where RazorpayGateway is a concrete class hardcoded directly. Which principle does this violate?

- **a)** SRP
- **b)** OCP
- **c)** DIP
- **d)** ISP

<sub>Screenshot: `msedge_DDpsL3pizb.png`</sub>

### Additional Problems

#### Q1. DIP Versus DI Distinction

What is the difference between DIP (Dependency Inversion Principle) and DI (Dependency Injection)?

- **a)** They are the same thing, just two different names
- **b)** DIP tells you who to depend on (an abstraction); DI tells you how that dependency reaches you (handed in from outside)
- **c)** DIP is only for Python; DI is only for other languages
- **d)** DIP applies to functions; DI applies only to classes

<sub>Screenshot: `msedge_6DRZbUQjGN.png`</sub>

#### Q2. Class Explosion With Behaviours

If a bird hierarchy has 4 independent behaviours (fly, dance, swim, sing), and you try to model each combination using plain "can/cannot" subclassing, how many classes would you need?

- **a)** 8
- **b)** 4
- **c)** 16
- **d)** 12

<sub>Screenshot: `msedge_crnBcJP31o.png`</sub>

#### Q3. Junk Drawer Utility File

A project has one utils.py file containing 40 unrelated functions — date logic, string logic, and file logic all mixed together. Which SRP trap is this an example of?

- **a)** The "does everything" method trap
- **b)** The "too many if-elif branches" trap
- **c)** The "junk drawer" utility file trap
- **d)** This isn't an SRP problem at all

<sub>Screenshot: `msedge_kXkzgP9lGC.png`</sub>

#### Q4. Special Handling Signals LSP Break

Why does needing a try-except block (or an isinstance check) before calling a method on a subclass count as an LSP violation?

- **a)** Because try-except blocks are always bad practice in Python - B) Because it means the subclass cannot genuinely be used in place of its
- **b)** Because it means the subclass cannot genuinely be used in place of its parent without special handling
- **c)** Because isinstance checks are slower than normal calls
- **d)** It is not actually an LSP violation

> Note: Option a) is shown exactly as on the source page, which accidentally includes the start of option b) in it.

<sub>Screenshot: `msedge_DarU1AVk6p.png`</sub>

#### Q5. Static Type Checking Catches Mismatch

With type hints in place, what does a static type checker like mypy do differently from Python itself when this code runs?
```python
flying_things: List[Flyable] = []
flying_things.append(Sparrow())
flying_things.append(Penguin())   # Penguin is NOT a Flyable

for f in flying_things:
    f.fly()
```

- **a)** mypy prevents the program from running at all, even without being called
- **b)** mypy would flag flying_things.append(Penguin()) as an error before the program even runs; Python itself only fails when .fly() is actually called on the Penguin, at runtime
- **c)** mypy and Python behave identically here
- **d)** mypy only checks syntax, not types like this

<sub>Screenshot: `msedge_rliweDgYcs.png`</sub>

#### Q6. Notification Service Loop Output

What is printed when this runs?

```python
class NotificationChannel(ABC):
    @abstractmethod
    def send(self, message): ...

class EmailChannel(NotificationChannel):
    def send(self, message):
        print(f"Sending Email: {message}")

class SMSChannel(NotificationChannel):
    def send(self, message):
        print(f"Sending SMS: {message}")

class NotificationService:
    def __init__(self, channels):
        self.channels = channels
    def notify(self, message):
        for channel in self.channels:
            channel.send(message)

service = NotificationService(channels=[EmailChannel(), SMSChannel()])
service.notify("Order shipped!")
```

- **a)** Only "Sending Email: Order shipped!" is printed
- **b)** Nothing is printed, because NotificationService doesn't create the channels itself
- **c)** Both "Sending Email: Order shipped!" and "Sending SMS: Order shipped!" are printed, in that order
- **d)** It raises a TypeError because NotificationChannel is abstract

<sub>Screenshot: `msedge_5viwk8L8NH.png`</sub>

#### Q7. Two Penguin Designs Compared

Compare these two Penguin designs. What is the key difference in the error each one produces?
```python
# Design 1 (Section 4)
class Penguin(Bird):
    def fly(self):
        raise NotImplementedError("Penguins can't fly!")

# Design 2 (Section 5)
class Penguin(NonFlyingBird):
    pass  # fly() does not exist at all
```

- **a)** Both raise the exact same error, so there's no real difference
- **b)** Design 1 raises NotImplementedError from inside a method that pretends to exist; Design 2 raises AttributeError because fly() was never defined for Penguin at all
- **c)** Design 1 crashes the program immediately on class creation; Design 2 does not
- **d)** Design 2 is worse because it gives no error at all

<sub>Screenshot: `msedge_FLRKeW20Nr.png`</sub>

#### Q8. Adding New Type Reopens Method

This code lets a VehicleService decide how each vehicle starts. A new team wants to add "ElectricStart" next month. What needs to change, and which principle does this design violate?
```python
class Vehicle:
    def __init__(self, engine_type):
        self.engine_type = engine_type

    def start(self):
        if self.engine_type == "petrol":
            print("Starting petrol engine")
        elif self.engine_type == "diesel":
            print("Starting diesel engine")
```

- **a)** No changes needed — this already supports any future engine type
- **b)** start() must be reopened and a new elif added for "electric" — this violates OCP
- **c)** This violates ISP, because Vehicle has too many attributes
- **d)** This violates DIP, because Vehicle doesn't use inheritance

<sub>Screenshot: `msedge_1mIwZwdA9p.png`</sub>

#### Q9. Concrete Payment Gateway Dependency

Spot the issue in this OrderService code and name the principle it violates:

```python
class RazorpayGateway:
    def pay(self, amount):
        print(f"Paying {amount} via Razorpay")

class OrderService:
    def __init__(self):
        self.gateway = RazorpayGateway()  # created directly, inside the class

    def checkout(self, amount):
        self.gateway.pay(amount)
```

- **a)** SRP — checkout() is doing too many jobs
- **b)** DIP — OrderService depends directly on the concrete RazorpayGateway, and also builds it itself, instead of depending on an abstraction and receiving it from outside
- **c)** LSP — RazorpayGateway cannot substitute for OrderService
- **d)** This code has no design issues

<sub>Screenshot: `msedge_ZGhpfzqkUQ.png`</sub>

#### Q10. Adding Channel Without Editing Service

A new team wants to add a WhatsAppChannel to a notification system, and they are told they "cannot touch NotificationService directly." If the system was built with one shared abstraction and channels injected from outside (the fixed AI Corner design), what would the new team actually need to do?

- **a)** Reopen NotificationService and add a new elif branch for WhatsApp
- **b)** Create a new WhatsAppChannel class implementing the same NotificationChannel abstraction, and pass it into NotificationService from outside
- **c)** Copy all of NotificationService and rename it
- **d)** It's impossible to add a new channel without editing NotificationService

<sub>Screenshot: `msedge_p8v9G9jSol.png`</sub>

#### Q11. AI Generated If-Elif Design Flaw

An AI assistant was asked to "write a NotificationService using good design principles," and it produced an if-elif chain based on a channel string, inside one send() method. Which principles does this design most clearly fail?

- **a)** LSP and ISP
- **b)** OCP, and to some extent SRP
- **c)** Only DIP
- **d)** None — "good design principles" was followed correctly

<sub>Screenshot: `msedge_ZPRJxXKcpV.png`</sub>

#### Q12. Interchangeable Gateways Via Abstraction

A checkout system currently uses Razorpay. The business wants to add Stripe next quarter, and possibly switch the default gateway per country later. If the system depends on a PaymentGateway abstraction (not a concrete gateway class), what is the main benefit for this business requirement?

- **a)** The checkout code doesn't need to change at all when a new gateway is added — only a new gateway class is created
- **b)** The business would need to rewrite the entire checkout flow for every new gateway
- **c)** This abstraction only helps with testing, not with adding new gateways
- **d)** There is no real benefit — hardcoding the gateway is simpler and just as flexible

<sub>Screenshot: `msedge_wPSmeFdBb7.png`</sub>

#### Q13. SQLAlchemy Engine Abstraction Example

SQLAlchemy's create_engine(url) reads the prefix of a connection string (like postgresql:// or mysql://) and automatically picks the right database driver internally. Which SOLID idea does this real-world example reflect?

- **a)** SRP only — because create_engine has one function name
- **b)** The application code depends on a general/abstracted interface, without hardcoding which specific database engine it's talking to — reflecting DIP-style thinking
- **c)** It reflects LSP only, because databases inherit from each other
- **d)** It has nothing to do with SOLID — it's just a convenience feature

<sub>Screenshot: `msedge_b2MlrjrZJA.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Introduction and Singleton

_Class date: Wed, 05 Aug 2026_

### Assignment

#### Q4. Assignment 1: Design Patterns – Introduction and Singleton

What is the main idea behind the Singleton pattern?

- **a)** A class that can create unlimited objects quickly
- **b)** A class that ensures only one object of it ever exists, with one shared access point
- **c)** A class that stores data in a database
- **d)** A class that cannot be inherited

<sub>Screenshot: `msedge_qh14ks0i9v.png`</sub>

#### Q5. Assignment 2: Design Patterns – Introduction and Singleton

Which of the following is a valid reason to use a Singleton?

- **a)** The class has private variables
- **b)** The class needs to support multiple inheritance
- **c)** A shared resource sits behind the class, OR creating the object is genuinely expensive
- **d)** The class has many public methods

<sub>Screenshot: `msedge_nuj3RYayo4.png`</sub>

#### Q6. Assignment 3: Design Patterns – Introduction and Singleton

What will this code print?

```python
class DBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, url):
        self.url = url

db1 = DBConnection("db.prod")
db2 = DBConnection("db.staging")

print(db1 is db2)
print(db1.url)
```

- **a)** False followed by db.prod
- **b)** True followed by db.prod
- **c)** True followed by db.staging
- **d)** False followed by db.staging

<sub>Screenshot: `msedge_o9PehN9V9Q.png`</sub>

#### Q7. Assignment 4: Design Patterns - Introduction and Singleton

Why can't we just put the "only one instance" check inside __init__ instead of __new__?

- **a)** __init__ doesn't have access to self
- **b)** __init__ runs before the object is created
- **c)** __init__ runs after the object already exists, so it's too late to refuse creation
- **d)** __init__ cannot access class-level variables

<sub>Screenshot: `msedge_04rD1MH6u8.png`</sub>

#### Q8. Assignment 5: Design Patterns – Introduction and Singleton

This code is meant to be a Singleton but has a bug. What's wrong?

```python
class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        cls._instance = super().__new__(cls)
        return cls._instance
```

- **a)** Nothing is wrong, this is correct
- **b)** It's missing an if cls._instance is None: check, so a new object is created on every single call
- **c)** super().__new__(cls) should be super().__init__(cls)
- **d)** _instance should be an instance variable, not a class variable

<sub>Screenshot: `msedge_N28WpayyC8.png`</sub>

#### Q9. Scenario

Your team's app creates its DBConnection singleton eagerly at module import time. QA reports that app startup has become noticeably slower. What is the most likely cause, based on the lecture?

- **a)** Eager loading builds the object immediately at import time, whether or not it's ever used, adding to startup time
- **b)** Singletons are always slower than regular classes
- **c)** The __new__ method is broken
- **d)** Python caches modules incorrectly

<sub>Screenshot: `msedge_6lY2uIMg5O.png`</sub>

#### Q10. Assignment 7: Design Patterns – Introduction and Singleton

Two threads, A and B, run this __new__ at nearly the same time, with _instance starting as None and no lock in place:

```python
class DBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

What is the most likely outcome under real concurrent traffic?

- **a)** Python's GIL guarantees only one object is ever created, so this is always safe
- **b)** The program will crash with a RuntimeError
- **c)** _instance will always end up as None
- **d)** Both threads could see _instance is None at the same time and each create a separate object, breaking the Singleton guarantee

<sub>Screenshot: `msedge_xBxSPoCMYK.png`</sub>

#### Q11. Assignment 8: Design Patterns – Introduction and Singleton

In double-checked locking, why is the second None check (inside the lock) necessary if we already checked None once outside the lock?

- **a)** It isn't necessary — one check is always enough
- **b)** Because the lock might not work correctly otherwise
- **c)** Because Python requires two checks by syntax rules
- **d)** Because another thread could have already created the instance while this thread was waiting for the lock

<sub>Screenshot: `msedge_AJiAZNtX1O.png`</sub>

#### Q12. Assignment 9: Design Patterns – Introduction and Singleton

A teammate wrote this "quick and simple" singleton after asking an AI assistant. What important detail is missing, based on the AI Corner discussion in the lecture?

```python
class DBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

- **a)** It's missing a threading.Lock to make it safe under concurrent access
- **b)** It's missing a __del__ method
- **c)** It's missing type hints
- **d)** It's missing a docstring

<sub>Screenshot: `msedge_6xFULGyrJD.png`</sub>

#### Q13. Assignment 10: Design Patterns – Introduction and Singleton

You import a module-level settings object (plain variables, no class) in five different files across your FastAPI app. How many actual objects/copies of settings exist across the whole app?

- **a)** Five — one per file that imports it
- **b)** It depends on how many threads are running
- **c)** One — Python caches a module after its first import, and every later import returns the same module object
- **d)** Zero, until the app finishes starting up

<sub>Screenshot: `msedge_WboQqmJrs9.png`</sub>

### Additional Problems

#### Q3. Homework 1: Design Patterns - Introduction and Singleton

Which of these real-world examples does the lecture NOT list as an existing Singleton in production systems?

- **a)** A brand-new list object created inside a loop
- **b)** Framework-managed settings objects (like FastAPI Settings)
- **c)** Python's logging.getLogger(name) returning the same logger object for a given name
- **d)** Connection pool managers like SQLAlchemy's engine

<sub>Screenshot: `msedge_iAMdwtvTDG.png`</sub>

#### Q4. Homework 2: Design Patterns – Introduction and Singleton

What does this print?

```python
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class DBConnection:
    def __init__(self, url):
        self.url = url

a = DBConnection("db.prod")
b = DBConnection("db.staging")

print(a is b)
```

- **a)** False
- **b)** It raises an error
- **c)** None
- **d)** True

<sub>Screenshot: `msedge_yfG2eMOlDr.png`</sub>

#### Q5. Homework 3: Design Patterns – Introduction and Singleton

This metaclass-based Singleton is supposed to be thread-safe, but a bug was introduced. Spot it.

```python
import threading

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

- **a)** There is no bug — this is a correct (if slightly less optimized) thread-safe singleton
- **b)** _lock should be an instance variable, not a class variable
- **c)** __call__ should be renamed to __init__
- **d)** _instances should be a list, not a dictionary

<sub>Screenshot: `msedge_qvgd9zgqF2.png`</sub>

#### Q6. Homework 4: Design Patterns – Introduction and Singleton

Why do some engineers avoid a class-based Singleton for objects that might get pickled?

- **a)** Pickling always deletes the object
- **b)** pickle doesn't support classes with __init__
- **c)** Unpickling can reconstruct a brand-new object, bypassing custom __new__ logic and breaking the "one instance" guarantee
- **d)** Pickled objects can't have class variables

<sub>Screenshot: `msedge_PEGkcEF5Gy.png`</sub>

#### Q7. Homework 5: Design Patterns – Introduction and Singleton

A test suite creates a DBConnection singleton, mutates some state on it, then finishes. The next test runs and unexpectedly sees leftover state from the previous test. What is the root cause?

- **a)** pytest doesn't support singletons
- **b)** A Singleton is shared for the entire life of the program, so it doesn't reset itself between tests
- **c)** The test file has a typo
- **d)** Singletons cannot hold any state

<sub>Screenshot: `msedge_ZWMsSD1Tna.png`</sub>

#### Q8. Homework 6: Design Patterns – Introduction and Singleton

What does this print?

```python
from enum import Enum

class Mode(Enum):
    SINGLE = "single"

a = Mode.SINGLE
b = Mode.SINGLE

print(a is b)
```

- **a)** True
- **b)** False
- **c)** None
- **d)** Raises a TypeError

<sub>Screenshot: `msedge_yjzFg5KUlk.png`</sub>

#### Q9. Homework 7: Design Patterns – Introduction and Singleton

What is a genuine downside (con) of using the Singleton pattern, according to the lecture?

- **a)** It uses too much memory since many objects are created
- **b)** It cannot be used in Python at all
- **c)** It requires a database to work
- **d)** It makes unit testing harder because you can't easily swap in a mock — everyone shares the same global instance

<sub>Screenshot: `msedge_y0VszHLLXU.png`</sub>

#### Q10. Homework 8: Design Patterns - Introduction and Singleton

A junior engineer wrote this thinking it's thread-safe double-checked locking. What's actually wrong with it?
```python
import threading

class DBConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
```

- **a)** This is fully correct double-checked locking
- **b)** _instance needs to be an instance variable
- **c)** threading.Lock() doesn't exist in Python
- **d)** This locks on every single call (not just the risky first-creation moment) because it's missing the outer, unlocked check before entering with cls._lock

<sub>Screenshot: `msedge_0Jqk7Ko0J6.png`</sub>

#### Q11. Homework 9: Design Patterns – Introduction and Singleton

Your team needs ten different classes to all become singletons, with minimal repeated code and full thread-safety. Based on the lecture's comparison of approaches, which option fits best?

- **a)** Copy-paste the __new__ override into all ten classes
- **b)** Use a metaclass (metaclass=SingletonMeta) so all ten classes get the behavior automatically and safely
- **c)** Make each class a single-member Enum
- **d)** Convert all ten classes into module-level variables

<sub>Screenshot: `msedge_9DtitXRmmO.png`</sub>

#### Q12. Homework 10: Design Patterns – Introduction and Singleton

Given the module below, what does the second script print?
config.py:
```python
value = 10

def increase():
    global value
    value += 5
```
main.py:
```python
import config
import config as config2

config.increase()

print(config2.value)
```

- **a)** 10
- **b)** 15
- **c)** None
- **d)** Raises an ImportError

<sub>Screenshot: `msedge_oDMHPuz7XV.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Builder

_Class date: Fri, 07 Aug 2026_

### Assignment

#### Q4. Builder Pattern – MCQ Assignment 1

What is the main reason we use the Builder pattern instead of one big constructor with many parameters?

- **a)** It makes the code run faster
- **b)** It helps us avoid using classes
- **c)** It makes object creation easier to read and lets us validate before the object is created
- **d)** It automatically saves the object to a database

<sub>Screenshot: `msedge_tPGPhEp3iS.png`</sub>

#### Q5. Builder Pattern – MCQ Assignment 2

```python
def add_item(cart=[]):
    cart.append("apple")
    return cart

print(add_item())
print(add_item())
```

What will this print?

- **a)** ['apple'] then ['apple']
- **b)** ['apple'] then ['apple', 'apple']
- **c)** [] then ['apple']
- **d)** Error

<sub>Screenshot: `msedge_ukuqhLfPAE.png`</sub>

#### Q6. Builder Pattern – MCQ Assignment 3

In the Builder pattern, why should every setter method (like set_name()) return self?

- **a)** So the object gets deleted after use
- **b)** So we can chain multiple setter calls together in one line
- **c)** So Python does not show an error
- **d)** It is not necessary, it is just a style choice

<sub>Screenshot: `msedge_BBRbsUIANs.png`</sub>

#### Q7. Builder Pattern – MCQ Assignment 4

```python
class Builder:
    def set_name(self, name):
        self.name = name

    def build(self):
        return self.name

b = Builder().set_name("Naman").build()
print(b)
```

What is wrong with this code?

- **a)** build() should not return anything
- **b)** set_name() does not return self, so chaining will fail
- **c)** self.name cannot be set inside a method
- **d)** Nothing is wrong, it will work fine

<sub>Screenshot: `msedge_tcqPh7ozOk.png`</sub>

#### Q8. Builder Pattern – MCQ Assignment 5

You are building a Student object. The rule is: grad_year must not be greater than 2022. Where should this check be written, based on what we learned in class?

- **a)** Inside the Student.__init__ or inside Builder.build(), before the Student object is created
- **b)** Anywhere in the code, it does not matter
- **c)** Only inside a separate function called after the object is created
- **d)** Inside set_grad_year() only, and nowhere else

<sub>Screenshot: `msedge_L4pW2cMaoB.png`</sub>

#### Q9. Builder Pattern – MCQ Assignment 6

```python
class Helper:
    __slots__ = ("name", "age")
    def __init__(self):
        self.name = None
        self.age = None

h = Helper()
h.nmae = "Riya"
```

What happens when this code runs?

- **a)** It runs fine, h.nmae is created silently
- **b)** It prints None
- **c)** It raises an AttributeError because nmae is not in __slots__
- **d)** It automatically fixes the typo to name

<sub>Screenshot: `msedge_L104QX3IJw.png`</sub>

#### Q10. Builder Pattern – MCQ Assignment 7

You ask an AI tool to generate a Builder for a class that has a tags list field. After build() runs, you change the original list you passed into the builder, and notice the already-built object's tags also change. What is the most likely mistake in the generated code?

- **a)** The build() method was never called
- **b)** The constructor copied the reference to the list (self.tags = builder.tags) instead of making a new copy
- **c)** __slots__ was used incorrectly
- **d)** The setter method did not return self

<sub>Screenshot: `msedge_Hz3tY5XJtw.png`</sub>

#### Q11. Builder Pattern – MCQ Assignment 8

Which of these is NOT a good reason to use the Builder pattern for a class?

- **a)** The class has many optional fields
- **b)** The object must be validated before it is allowed to exist
- **c)** The class is very small, like a Point class with only x and y
- **d)** Values for the object arrive gradually, over several steps

<sub>Screenshot: `msedge_aqOXO46f73.png`</sub>

### Additional Problems

#### Q3. Builder Pattern – MCQ Homework 1

In the homework assignments, the Builder class must be marked with @WithBuilder. What is the purpose of this annotation?

- **a)** It makes the class run faster
- **b)** It tells the test system which class to treat as the actual Builder implementation
- **c)** It automatically validates all fields
- **d)** It converts the class into an interface

<sub>Screenshot: `msedge_I3pK9kkVcv.png`</sub>

#### Q4. Builder Pattern – MCQ Homework 2

In the DatabaseConfiguration homework, the config object must be immutable once built. Which design choice from the Python lecture supports this same idea?

- **a)** Using a mutable default argument like subjects=[]
- **b)** Letting any part of the code change fields directly using dot notation after creation
- **c)** Setting all fields once inside build()/constructor, and never changing them again afterward
- **d)** Skipping validation to make the code shorter

<sub>Screenshot: `msedge_WFJcG8JNNt.png`</sub>

#### Q5. Builder Pattern – MCQ Homework 3

A developer writes a QueryBuilder where with_where("age > 18") is called three times to add three different conditions. But in the final Query object, only the last condition is saved. What is the likely bug?

- **a)** The build() method was never called
- **b)** with_where() is overwriting the stored value each time instead of adding (appending) to a list of conditions
- **c)** age > 18 is not a valid string
- **d)** The class is missing @WithBuilder

<sub>Screenshot: `msedge_wk3onBYaFn.png`</sub>

#### Q6. Builder Pattern – MCQ Homework 4

Why did the problem statement for "Builder Message" say the old way (multiple overloaded constructors) was "error-prone and hard to maintain"?

- **a)** Because overloaded constructors are slower to run
- **b)** Because adding a new message type or field means creating or changing many constructors, which is easy to get wrong
- **c)** Because constructors cannot have parameters
- **d)** Because Java does not support constructors

<sub>Screenshot: `msedge_oztcYH5c5H.png`</sub>

#### Q7. Builder Pattern – MCQ Homework 5

A student writes a MessageBuilder where build() just returns new Message(this) with no checks at all, even though a text message must always have non-empty content. What problem does this cause, based on what was taught?

- **a)** No problem, it will still work fine
- **b)** An invalid Message (with missing content) could be created and used elsewhere in the program
- **c)** The code will not compile
- **d)** The Builder pattern requires no validation ever

<sub>Screenshot: `msedge_keceYuIeKu.png`</sub>

#### Q8. Builder Pattern – MCQ Homework 6

```python
builder = DatabaseConfigurationBuilder()
builder.with_allowed_hosts(["localhost"])
config1 = builder.build()   // build() does: self.allowed_hosts =
list(builder.allowed_hosts)

builder.get_allowed_hosts_list().add("192.168.1.1")

print(config1.allowed_hosts)
```

If the Builder correctly follows what was taught in class (making a fresh copy of any list, not just pointing to it), what should this print?

- **a)** ["localhost", "192.168.1.1"], because both objects share the same list
- **b)** ["localhost"], because config1 got its own independent copy of the list when it was built
- **c)** An error, because lists cannot be copied
- **d)** An empty list, because copying clears the original values

<sub>Screenshot: `msedge_uAQzfL8YbH.png`</sub>

#### Q9. Builder Pattern - MCQ Homework 7

Which of these is the best reason to write validation logic inside build() rather than inside each individual setter (like with_username())?

- **a)** Setters are not allowed to have any logic at all
- **b)** Some validation rules depend on more than one field together, so they can only be checked once all fields are set
- **c)** It makes the code run faster
- **d)** It is required by the @WithBuilder annotation

<sub>Screenshot: `msedge_zZLuWeFpcW.png`</sub>

#### Q10. Builder Pattern – MCQ Homework 8

A teammate says: "I don't need the Builder pattern for my Point class with just x and y. I'll just do Point(x, y) directly." Based on the lecture's wrap-up, is this reasonable?

- **a)** No, Builder must always be used for every class
- **b)** Yes, for a very small class with few fields and no complex validation, a plain constructor is simpler and Builder would be unnecessary extra code
- **c)** No, because Point needs immutability and only Builder can provide that
- **d)** Yes, but only if the class is written in Java

<sub>Screenshot: `msedge_d4MsTUsUBE.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Prototype and Registry

_Class date: Mon, 10 Aug 2026_

### Assignment

#### Q3. Core Problem Solved by Prototype Pattern

(Theory) What problem does the Prototype pattern mainly solve?

- **a)** Creating a new object by copying an existing one instead of building it from scratch
- **b)** Creating an object step-by-step with validation before it is complete
- **c)** Making sure only one object of a class ever exists
- **d)** Choosing which subclass to create based on user input

<sub>Screenshot: `msedge_V37WY9AiB7.png`</sub>

#### Q4. Simple Object Cloning Output

(Code Output)

```python
from abc import ABC, abstractmethod

class Prototype(ABC):
    @abstractmethod
    def clone(self):
        ...

class Config(Prototype):
    def __init__(self, source=None):
        if source is None:
            self.env = None
            self.timeout = None
        else:
            self.env = source.env
            self.timeout = source.timeout

    def clone(self):
        return Config(self)

c1 = Config()
c1.env = "staging"
c1.timeout = 30

c2 = c1.clone()
c2.env = "production"

print(c1.env, c2.env)
```

What gets printed?

- **a)** production production
- **b)** staging production
- **c)** staging staging
- **d)** production staging

<sub>Screenshot: `msedge_KzMZQ0w4DR.png`</sub>

#### Q5. Thread Safety in Prototype Registry

(Code Debug) A student writes this registry method to add a new prototype only if it doesn't already exist:

```python
def add_if_missing(self, key, prototype):
    if key not in self._templates:
        self._templates[key] = prototype
```

Why might this method behave incorrectly if two threads call it at the same time with the same new key?

- **a)** Python dictionaries cannot store custom objects as values
- **b)** abstractmethod prevents this method from ever running twice
- **c)** The check ("is key missing?") and the action ("add it") are two separate steps, so both threads can pass the check before either one writes
- **d)** Python automatically locks every dictionary method, so this is actually safe

<sub>Screenshot: `msedge_RQuRArxbvB.png`</sub>

#### Q6. Multiple Constructors in Python

(Scenario) A Student class has an __init__ that takes no arguments and sets default values. A developer wants to also let Student be created by copying an existing Student object. They try adding a second __init__ method that takes a source object instead. What actually happens in Python?

- **a)** Python raises an error because a class cannot have two constructors
- **b)** Both __init__ methods work — Python picks the right one based on the arguments passed
- **c)** Python merges both __init__ methods into one automatically
- **d)** Only the second __init__ definition remains active; the first one is silently overwritten

<sub>Screenshot: `msedge_2otVPBQWgu.png`</sub>

#### Q7. Overriding Clone in Subclasses

(Theory) Why must every subclass of a Prototype-based class override clone() itself, even if the parent class already has a clone() method?

- **a)** Because if it doesn’t, calling .clone() runs the parent’s version, which doesn’t know about the subclass’s extra fields — silently dropping them
- **b)** Because Python requires every subclass to redefine every inherited method
- **c)** Because clone() is not inherited in Python
- **d)** Because subclasses are not allowed to call super().__init__()

<sub>Screenshot: `msedge_qazSX2Dns9.png`</sub>

#### Q8. Shallow Copy Bug in Cloning

(Code Output)

```python
class VMInstance:
    def __init__(self, source=None):
        if source is None:
            self.installed_packages = []
        else:
            self.installed_packages = source.installed_packages

    def clone(self):
        return VMInstance(self)

original = VMInstance()
original.installed_packages = ["nginx"]

copy = original.clone()
copy.installed_packages.append("redis")

print(original.installed_packages)
```

What gets printed?

- **a)** ["nginx"]
- **b)** ["nginx", "redis"]
- **c)** []
- **d)** ["redis"]

<sub>Screenshot: `msedge_CcBf2k1DfQ.png`</sub>

#### Q9. Fixing Shallow Copy in Lists

(Code Debug) How should the buggy line from Q6 be fixed so that copy.installed_packages becomes fully independent from original.installed_packages?

- **a)** self.installed_packages = source.installed_packages
- **b)** self.installed_packages = source.installed_packages.copy (without calling it)
- **c)** self.installed_packages = list(source.installed_packages)
- **d)** self.installed_packages = "installed_packages"

<sub>Screenshot: `msedge_x7mpYPc71F.png`</sub>

#### Q10. Dictionary get() Behavior on Missing Keys

(Scenario) A team keeps a dictionary-based registry of reusable templates, keyed by string names like "welcome_email" and "password_reset_email". A developer calls registry.get("passwordreset_email") (missing the underscore) using this method:

```python
def get(self, key):
    return self._templates.get(key)
```

What will actually happen?

- **a)** Python raises a KeyError immediately, right on this line
- **b)** The registry automatically finds the closest matching key
- **c)** A new empty template is created and returned
- **d)** get() returns None, and the program only fails later, wherever that None is used (e.g., calling .clone() on it)

<sub>Screenshot: `msedge_QtBoHwLQbj.png`</sub>

#### Q11. Prototype vs. Registry Pattern

(Theory) Which statement best describes the difference between the Prototype pattern and the Registry pattern?

- **a)** Prototype lets an object copy itself; Registry stores and retrieves reusable templates by key
- **b)** Prototype stores multiple templates by name; Registry copies a single object
- **c)** They are the same pattern with two different names
- **d)** Prototype is only used in Python; Registry is only used in Java

<sub>Screenshot: `msedge_wtGnjbUjHm.png`</sub>

### Additional Problems

#### Q2. Golden Image Analogy

(Theory) In the cloud VM analogy from the lecture, what does the “golden image” represent in Prototype pattern terms?

- **a)** The client code that requests a new VM
- **b)** The prototype / template object that gets cloned
- **c)** The registry
- **d)** The abstract Prototype interface

<sub>Screenshot: `msedge_g68f1zxMH0.png`</sub>

#### Q3. Inefficiency Solved by Prototype

(Scenario) In the SearchAPI example, the base URL, auth token, retry settings, and timeout rarely change between calls, but the search query changes every time. What is the main inefficiency in creating a brand-new SearchAPI object from scratch on every single call?

- **a)** Python cannot create more than one object of the same class
- **b)** The query field cannot be changed after object creation
- **c)** Identical, already-correct configuration is redone unnecessarily on every call
- **d)** SearchAPI objects cannot be cloned at all

<sub>Screenshot: `msedge_N539PRecgV.png`</sub>

#### Q4. Independent Clones

(Code Output)

```python
class Email:
    def __init__(self, source=None):
        if source is None:
            self.subject = None
            self.footer = None
        else:
            self.subject = source.subject
            self.footer = source.footer

    def clone(self):
        return Email(self)

template = Email()
template.subject = "Welcome!"
template.footer = "Thanks for joining"

email1 = template.clone()
email1.subject = "Welcome aboard!"

print(template.subject, email1.subject)
```

What gets printed?

- **a)** Welcome aboard! Welcome aboard!
- **b)** Welcome! Welcome!
- **c)** None None
- **d)** Welcome! Welcome aboard!

<sub>Screenshot: `msedge_X7YNbhzrFB.png`</sub>

#### Q5. Missing Clone Override in Inheritance

(Code Debug)
```python
class Animal:
    def __init__(self, source=None):
        if source is None:
            self.name = None
        else:
            self.name = source.name

    def clone(self):
        return Animal(self)

class Dog(Animal):
    def __init__(self, source=None):
        super().__init__(source)
        if source is None:
            self.breed = None
        else:
            self.breed = source.breed
    # clone() is NOT overridden here

d1 = Dog()
d1.name = "Rex"
d1.breed = "Labrador"

d2 = d1.clone()
print(d2.breed)
```
What actually happens?

- **a)** An AttributeError is raised, because Dog never overrode clone(), so Animal.clone() ran instead and returned a plain Animal object that never had breed set
- **b)** It prints "Labrador"
- **c)** It prints "Rex"
- **d)** It prints None

<sub>Screenshot: `msedge_20hahB1fma.png`</sub>

#### Q6. Drawbacks of Manual Object Copying

(Theory) Why is it usually a bad idea for client code to copy an object by manually setting each field from outside the class (e.g., copy.os = original.os, copy.runtime = original.runtime, ...)?

- **a)** It runs slower than every other approach in all cases
- **b)** It creates tight coupling to internal fields, can violate encapsulation, and leads to isinstance() chains for subclasses
- **c)** Python does not allow assigning attributes from outside a class
- **d)** It only works for classes with exactly two fields

<sub>Screenshot: `msedge_B9K2UMZw3l.png`</sub>

#### Q7. Mutating Registry Templates Directly

(Scenario) A registry is being used like this:

```python
registry = VMImageRegistry()
registry.register("backend-server-v3", backend_image)

server = registry.get("backend-server-v3")
server.hostname = "web-01"
```

Note: .clone() was never called before modifying server. What is the risk here?

- **a)** None — get() already returns a safe, independent copy
- **b)** This code will raise an error because hostname doesn't exist yet
- **c)** server is the same object stored inside the registry, so this directly modifies the shared template itself
- **d)** The registry will automatically detect and block this change

<sub>Screenshots: `msedge_TDJl3NpBdd.png`, `msedge_XzibunHfHP.png`</sub>

#### Q8. Shallow Copy Using copy Module

(Code Output)

```python
import copy

class Config:
    def __init__(self):
        self.settings = {"debug": True}

original = Config()
shallow = copy.copy(original)
shallow.settings["debug"] = False

print(original.settings["debug"])
```

What gets printed?

- **a)** True
- **b)** None
- **c)** An error is raised
- **d)** False

<sub>Screenshot: `msedge_VwjQl2GHZa.png`</sub>

#### Q9. When to Skip Prototype

(Theory) According to the lecture, when is it reasonable to skip the Prototype pattern entirely and just construct an object normally?

- **a)** When constructing the object fresh is already cheap and simple, so cloning would just add unnecessary overhead
- **b)** Never — Prototype must always be used, even for the simplest classes
- **c)** Only when the class has no fields at all
- **d)** Only when the class is abstract

<sub>Screenshot: `msedge_blQk5R7xko.png`</sub>

#### Q10. Separating Prototype and Registry Concerns

(Scenario) A registry needs to store several different “welcome email”, “password reset email”, and “invoice email” templates, and retrieve/clone the right one by name whenever a new email needs to be sent. Which two responsibilities does this design split apart, according to the lecture?

- **a)** Validation and testing
- **b)** Copying an object (Prototype) and storing/retrieving templates by key (Registry)
- **c)** Sending the email and formatting the email
- **d)** Creating the class and deleting the class

<sub>Screenshot: `msedge_m8bRlejK9V.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Leveraging Factory Pattern for Service Abstraction.

_Class date: Wed, 12 Aug 2026_

### Assignment

#### Q4. Assignment Question 1 – Factory Pattern

What is the main purpose of the Simple Factory pattern?

- **a)** To centralize object-creation logic in one place instead of repeating it everywhere
- **b)** To make a class inherit from multiple parent classes
- **c)** To make objects communicate over a network
- **d)** To remove the need for classes entirely

<sub>Screenshot: `msedge_iL3G8Ogv77.png`</sub>

#### Q5. Assignment Question 2 – Factory Pattern

What will this code print?

```python
class AudioPlayer:
    def __init__(self, volume):
        self.volume = volume
    def play(self):
        return f"Playing at volume {self.volume}"

class MP3AudioPlayer(AudioPlayer):
    pass

player = MP3AudioPlayer(50)
print(player.play())
```

- **a)** Playing at volume 0
- **b)** Playing at volume 50
- **c)** Error, MP3AudioPlayer has no play method
- **d)** None

<sub>Screenshot: `msedge_TIJOI7iskg.png`</sub>

#### Q6. Assignment Question 3 – Factory Pattern

What happens when this code runs?

```python
class AudioPlayerFactory:
    def create_audio_player(format, volume):
        if format == "mp3":
            return MP3AudioPlayer(volume)
        elif format == "wav":
            return WAVAudioPlayer(volume)

factory = AudioPlayerFactory()
player = factory.create_audio_player("mp3", 50)
```

- **a)** It works fine and returns an MP3AudioPlayer
- **b)** It silently returns None
- **c)** It raises a TypeError because self is passed automatically, leaving too many arguments for format and volume
- **d)** It raises an ImportError

<sub>Screenshot: `msedge_MA1XNzWrmL.png`</sub>

#### Q7. Assignment Question 4 – Factory Pattern

Your team needs AudioDecoder, AudioProcessor, and AudioPlayer objects that must always come from the same format (e.g. all MP3, never MP3 decoder + WAV processor). Which pattern fits best?

- **a)** Simple Factory
- **b)** A single if/elif inside each class
- **c)** No pattern is needed
- **d)** Abstract Factory

<sub>Screenshot: `msedge_MqeapUIlQG.png`</sub>

#### Q8. Assignment Question 5 – Factory Pattern

In the Abstract Factory pattern, what does supports_format typically do?

- **a)** Checks whether a given factory can handle a specific format
- **b)** Converts one audio format into another
- **c)** Plays the audio file
- **d)** Deletes unsupported audio files

<sub>Screenshot: `msedge_lejEv5RvFq.png`</sub>

#### Q9. Assignment Question 6 – Factory Pattern

What does this print?

```python
from abc import ABC, abstractmethod

class AudioFactory(ABC):
    @abstractmethod
    def create_audio_player(self):
        ...

class Mp3AudioFactory(AudioFactory):
    def create_audio_player(self):
        return "MP3 Player"

factory = Mp3AudioFactory()
print(factory.create_audio_player())
```

- **a)** Error: cannot instantiate AudioFactory
- **b)** MP3 Player
- **c)** None
- **d)** Error: create_audio_player is abstract

<sub>Screenshot: `msedge_bqM9dv9AOe.png`</sub>

#### Q10. Assignment Question 7 – Factory Pattern

Why will this code fail?

```python
from abc import ABC, abstractmethod

class AudioFactory(ABC):
    @abstractmethod
    def create_audio_player(self):
        ...

factory = AudioFactory()
```

- **a)** AudioFactory has too many methods
- **b)** create_audio_player should not use @abstractmethod
- **c)** You cannot instantiate a class that still has unimplemented abstract methods
- **d)** Nothing is wrong, this works fine

<sub>Screenshot: `msedge_7RhYN7sqpV.png`</sub>

### Additional Problems

#### Q4. Homework Question 1 – Factory Pattern

What problem does the Simple Factory pattern solve when a class has repeated if/elif blocks to decide which object to create?

- **a)** It removes the Open/Closed Principle
- **b)** It duplicates the decision logic further
- **c)** It makes the code run faster
- **d)** It fixes Open/Closed Principle violations by keeping creation logic in one place instead of scattered across callers

<sub>Screenshot: `msedge_ProUtSYBVL.png`</sub>

#### Q5. Homework Question 2 – Factory Pattern

What will this print?

```python
class Notification:
    def __init__(self, recipient, message):
        self.recipient = recipient
        self.message = message

class SMSNotification(Notification):
    def send(self):
        return f"SMS to {self.recipient}: {self.message}"

n = SMSNotification("9999999999", "Hello!")
print(n.send())
```

- **a)** SMS to 9999999999: Hello!
- **b)** Error: send() not defined in Notification
- **c)** None
- **d)** Hello! to 9999999999

<sub>Screenshot: `msedge_PSZrObW8jE.png`</sub>

#### Q6. Homework Question 3 - Factory Pattern

What's wrong with this Simple Factory method?
```python
class NotificationFactory:
    @staticmethod
    def create_notification(type_, *args):
        if type_ == "EMAIL":
            return EmailNotification(args)
        elif type_ == "SMS":
            return SMSNotification(args)
```

- **a)** @staticmethod should not be used here
- **b)** args is being passed as a single tuple instead of being unpacked, so the constructor won't receive separate arguments
- **c)** type_ should not be a string
- **d)** Nothing is wrong

<sub>Screenshot: `msedge_2b8dWGRydq.png`</sub>

#### Q7. Homework Question 4 – Factory Pattern

Which of these is true about Abstract Factory according to the lecture?

- **a)** It always eliminates the need for a common parent class
- **b)** It should be used even when there's only one object being created
- **c)** It's worth the extra structure only when a genuine family of related objects must stay matched together
- **d)** It replaces Simple Factory in every situation

<sub>Screenshot: `msedge_43S3AwyWGA.png`</sub>

#### Q8. Homework Question 5 - Factory Pattern

A document processing app needs DocumentParser, DocumentProcessor, and DocumentPrinter objects that must always match the same document type (e.g. all Text, never Text parser + Spreadsheet printer). Which pattern should be used?

- **a)** Simple Factory
- **b)** No factory, use if/elif in the client
- **c)** Singleton
- **d)** Abstract Factory

<sub>Screenshot: `msedge_HjRoOUi956.png`</sub>

#### Q9. Homework Question 6 – Factory Pattern

What will this print?

```python
from abc import ABC, abstractmethod

class NotificationFactory(ABC):
    @abstractmethod
    def create_sender(self):
        ...

class EmailNotificationFactory(NotificationFactory):
    def create_sender(self):
        return "Email Sender Ready"

factory = EmailNotificationFactory()
print(factory.create_sender())
```

- **a)** Email Sender Ready
- **b)** Error: abstract method not allowed
- **c)** None
- **d)** Error: cannot instantiate NotificationFactory

<sub>Screenshot: `msedge_ReierjHg3w.png`</sub>

#### Q10. Homework Question 7 – Factory Pattern

Why is this design flawed based on the lecture's "vendor leak" discussion?

```python
class NotificationService:
    def notify(self, type_, recipient, message):
        if type_ == "EMAIL":
            client = EmailNotification(recipient, message)
        client.send()
```

- **a)** There's nothing flawed, this is correct
- **b)** NotificationService directly builds concrete classes instead of going through a factory, reintroducing the coupling the factory pattern is meant to remove
- **c)** EmailNotification should not have a send() method
- **d)** recipient and message should be swapped

<sub>Screenshot: `msedge_pOmHjSgSxG.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Adapter and Facade

_Class date: Fri, 14 Aug 2026_

### Assignment

#### Q4. Adapter & Facade - Theroy for Beginner

A Builder class controls the step-by-step construction of a complex object. An Adapter class wraps an existing object so a client can call it through a different interface. Both classes "wrap" something in some sense. Why is Builder a Creational pattern while Adapter is a Structural pattern?

- **a)** Builder is concerned with assembling an object into existence; Adapter is concerned with connecting an already-existing object to a client that can't call it directly
- **b)** Builder uses inheritance while Adapter uses composition
- **c)** Builder is used for simple objects and Adapter is used for complex objects
- **d)** There's no real difference — the classification is arbitrary

<sub>Screenshot: `msedge_LYSwRPubsz.png`</sub>

#### Q5. Scenario Based - Beginner

Your app calls Yes Bank’s dopayment() and getacc_balance() directly everywhere in the codebase. Business now wants to add HDFC Bank, whose method names are totally different. What’s the correct fix per the lecture?

- **a)** Edit Yes Bank’s source code so its method names match HDFC’s
- **b)** Create a common BankAPI interface, and write one adapter class per bank that translates calls into that bank’s real methods
- **c)** Rewrite PhonePe with if/elif branches for each bank
- **d)** Merge Yes Bank and HDFC into a single class

<sub>Screenshot: `msedge_ldn055HHYb.png`</sub>

#### Q6. Code Output - Beginner

```python
class YesBank:
def do_payment(self, account, amt):
return 0 # 0 means success
class YesBankAdapter(BankAPI):
def __init__(self, yes_bank):
self.yes_bank = yes_bank
def pay(self, amount, account):
status = self.yes_bank.do_payment(account, amount)
return status == 0
adapter = YesBankAdapter(YesBank())
print(adapter.pay(100, "ACC1"))
```

- **a)** 0
- **b)** None
- **c)** True
- **d)** False

<sub>Screenshot: `msedge_8xRQ8ObXR7.png`</sub>

#### Q7. Debug the Code - Intermediate

```python
class Amazon:
    def order_place(self):
        self.invoice_generation()
        self.wms.update()
        self.ims.update()
        self.emails.send_email()
```

The team wants to apply the Facade pattern here to keep Amazon clean. What's wrong with the current code from a Facade perspective?

- **a)** The method name `order_place` should be renamed to `facade_order_place`
- **b)** Amazon is missing a BankAPI interface
- **c)** There’s nothing wrong — this already is a Facade
- **d)** Amazon.order_place() is doing the coordination job of four unrelated subsystems itself, instead of delegating to a dedicated Facade class

<sub>Screenshot: `msedge_XfHajFkumR.png`</sub>

#### Q8. Scenario Based - Intermediate

A class talks to three different logging services, each with a different API, and combines their output into one log() method. According to the lecture, this design is:

- **a)** Both — one Adapter per logging service to normalize each API, all sitting inside one Facade that exposes a single log() method
- **b)** Only an Adapter, since it’s about translating between APIs
- **c)** Only a Facade, since it exposes one simple method
- **d)** Neither — this is a Factory pattern

<sub>Screenshot: `msedge_SMIUWmU8aw.png`</sub>

#### Q9. SCALER QUESTION 66630 a140

```python
class PhonePeFacade:
    def __init__(self, phone_pe):
        self.phone_pe = phone_pe

    def checkout(self, amount, account, bank_name):
        if bank_name == "YesBank":
            self.phone_pe.bank_api = YesBankAdapter(YesBank())
        elif bank_name == "HDFCBank":
            self.phone_pe.bank_api = HDFCBankAdapter(HDFCBank())
        return self.phone_pe.bank_api.pay(amount, account)
```
What design flaw does the AI Corner exercise identify in this Facade?

- **a)** It's missing a try/except block around pay()
- **b)** It re-introduces the exact bank-selection coupling the Adapter pattern was meant to eliminate — adding a new bank still means editing this class
- **c)** PhonePeFacade should inherit from BankAPI
- **d)** The constructor should not take phone_pe as a parameter

<sub>Screenshot: `msedge_EcQzlwdqMt.png`</sub>

#### Q10. Theory Based

Suppose PhonePe is later refactored so it depends directly on YesBankAdapter (not on the BankAPI interface). It still works fine today. What has actually been lost by removing the interface, even though nothing is broken yet?

- **a)** Nothing — as long as it compiles and passes tests, the interface was optional
- **b)** The ability to swap in a different adapter (e.g., for HDFC) without changing PhonePe’s code — PhonePe is now coupled to one specific adapter class instead of an abstraction
- **c)** YesBankAdapter would stop being able to wrap YesBank
- **d)** The Adaptee (YesBank) would need to change its method names

<sub>Screenshot: `msedge_VdrzUJlbkG.png`</sub>

#### Q11. SCALER QUESTION 66632 be68

Two versions of the same Facade are shown below.
Version1
```python
class OrderPlacedFacade:
    def __init__(self):
        self.wms = WMS()
        self.ims = IMS()
```
Version 2
```python
class OrderPlacedFacade:
    def __init__(self, wms, ims):
        self.wms = wms
        self.ims = ims
```
A new requirement comes in: unit tests need to run OrderPlacedFacade against fake/mock warehouse and inventory systems, without touching the real ones. Which version supports this without modifying OrderPlacedFacade's code, and why?

- **a)** Version 1 — because it's simpler and has fewer parameters
- **b)** Version 1 — because internal creation is always safer for testing
- **c)** Both are equally testable
- **d)** Version 2 — because the caller can pass in mock wms/ims objects at construction time, instead of the Facade being hardwired to the real concrete classes

<sub>Screenshot: `msedge_EoG6NzQEAH.png`</sub>

### Additional Problems

#### Q4. Scenario based - homework question

A junior developer says: “I added a wrapper class in front of our payment code, so I’ve used the Facade pattern.” Looking closer, the wrapper only calls into a single third-party payment class, translating its method names and parameter shapes to match what the rest of the codebase expects — no other subsystem is involved. What’s the more accurate assessment?

- **a)** This is actually Adapter, not Facade — it’s translating one incompatible interface, not simplifying coordination across multiple subsystems
- **b)** This is correctly a Facade, since any wrapper class counts as one
- **c)** This is neither pattern, since only one class is involved
- **d)** This is both patterns simultaneously, since it wraps something

<sub>Screenshot: `msedge_n9k7oA1sfz.png`</sub>

#### Q5. Scenario based - Beginner Question

Your app needs to support OpenAI, Anthropic, and Gemini LLM SDKs, each with different request shapes and parameter names. You want your app to code against one common interface. Which pattern applies, and why?

- **a)** Facade — because it hides complexity
- **b)** Adapter — because it translates each SDK’s different shape into one common interface (ChatModel) your app depends on
- **c)** Singleton — because you only need one instance
- **d)** Strategy — because you’re switching algorithms

<sub>Screenshot: `msedge_ZbKhI8J3U0.png`</sub>

#### Q6. Code Output - Homework Question

```python
class ChatModel(ABC):
    @abstractmethod
    def generate(self, prompt, params): ...

class OpenAIAdapter(ChatModel):
    def __init__(self, client):
        self.client = client
    def generate(self, prompt, params):
        return f"OpenAI response to: {prompt}"

def run(model: ChatModel, prompt):
    return model.generate(prompt, {})

adapter = OpenAIAdapter(client=None)
print(run(adapter, "Hello"))
```

What gets printed?

- **a)** Error — run() cannot accept an Adapter object
- **b)** None
- **c)** OpenAI response to: Hello
- **d)** ChatModel response to: Hello

<sub>Screenshot: `msedge_AMVSZxI6Lf.png`</sub>

#### Q7. Debug the code - Intermediate Homework Question

```python
class YesBank:
def open_account(self, acc_number, holder_name):
...
class YesBankAdapter(BankAPI):
def __init__(self, yes_bank):
self.yes_bank = yes_bank

def add_bank_account(self, bank):
self.yes_bank.open_account(bank.holder_name, bank.account_number)
```
Assume `Bank.__init__(self, account_number, account_holder_name)` sets `self.account_number` and `self.account_holder_name`.
What's the bug?

- **a)** YesBankAdapter should inherit from Bank, not BankAPI
- **b)** open_account should not take any arguments
- **c)** There is no bug
- **d)** `bank.holder_name` does not exist (it's `bank.account_holder_name`), and the arguments are passed in the wrong order — it should be `open_account(bank.account_number, bank.account_holder_name)`

<sub>Screenshot: `msedge_Lbi44mYZCm.png`</sub>

#### Q8. Scenario Based -Intermediate Question

An AI coding assistant receives one user message, then internally pulls context, plans steps, calls tools, updates memory, and returns one final answer. The user sees only “message in, answer out.” What pattern does this AgentFacade.run() represent, and why?

- **a)** Facade — because it hides the coordination of multiple internal subsystems (retriever, planner, tool executor, memory) behind one simple run() entry point
- **b)** Adapter — because it translates between different tool APIs
- **c)** Singleton — because there is only one agent
- **d)** Builder — because it constructs a response step by step

<sub>Screenshot: `msedge_ZsntiiS5kL.png`</sub>

#### Q9. Code Output for this Question

```python
class InvoiceService:
    def generate(self, order): print("Invoice generated")

class WMS:
    def update(self, order): print("Warehouse updated")

class OrderPlacedFacade:
    def __init__(self, invoice_service, wms):
        self.invoice_service = invoice_service
        self.wms = wms
    def on_order_place(self, order):
        self.invoice_service.generate(order)
        self.wms.update(order)

facade = OrderPlacedFacade(InvoiceService(), WMS())
facade.on_order_place("order123")
```

What is printed, in order?

- **a)** “Warehouse updated” then “Invoice generated”
- **b)** “Invoice generated” then “Warehouse updated”
- **c)** Only “Invoice generated”
- **d)** Nothing — this raises an error

<sub>Screenshot: `msedge_n8cCdvq26k.png`</sub>

#### Q10. Debug this code - Intermediate Homework Question

```python
class PhonePe:
    def __init__(self, bank_api):
        self.bank_api = bank_api

    def perform_bank_operations(self, bank_name):
        if bank_name == "YesBank":
            self.bank_api = YesBankAdapter(YesBank())
        elif bank_name == "HDFCBank":
            self.bank_api = HDFCBankAdapter(HDFCBank())
        elif bank_name == "ICICIBank":
            self.bank_api = ICICIBankAdapter(ICICIBank())
        self.bank_api.pay(100.0, "ACC1")
```

What principle does this violate, based on the lecture's Open/Closed discussion?

- **a)** Single Responsibility — PhonePe should not have a constructor
- **b)** Dependency Injection — bank_api should never be passed into init
- **c)** Open/Closed Principle — PhonePe had to be edited (new elif) to support ICICI, instead of just adding a new adapter class and leaving PhonePe untouched
- **d)** Liskov Substitution — ICICIBankAdapter cannot substitute BankAPI

<sub>Screenshot: `msedge_pOS4E7s7qE.png`</sub>

#### Q11. Scenario--based Homework Question

A ride-hailing app needs to: (1) call three different maps SDKs — Google Maps, Mapbox, and OpenStreetMap — through one common MapProvider interface, and (2) offer callers a single book_ride() method that internally picks a map provider, calculates fare, finds a driver, and sends a confirmation. Which combination of patterns fits, and how would they relate to each other?

- **a)** Only one Facade is needed — it can also handle translating the three different maps SDKs internally
- **b)** One Adapter per maps SDK (to normalize their different APIs into MapProvider), plus one Facade around book_ride() that uses those adapters as part of its coordination
- **c)** Only three Adapters are needed — book_ride() doesn’t need a Facade since it’s just one method
- **d)** This scenario doesn’t fit either pattern since it involves both APIs and multi-step coordination

<sub>Screenshot: `msedge_60ywsX6ezY.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Decorator and Flyweight

_Class date: Mon, 17 Aug 2026_

### Assignment

#### Q3. Adapter & Facade Question-1

A Builder class controls the step-by-step construction of a complex object. An Adapter class wraps an existing object so a client can call it through a different interface. Both classes "wrap" something in some sense. Why is Builder a Creational pattern while Adapter is a Structural pattern?

- **a)** Builder is concerned with assembling an object into existence; Adapter is concerned with connecting an already-existing object to a client that can’t call it directly
- **b)** Builder uses inheritance while Adapter uses composition
- **c)** Builder is used for simple objects and Adapter is used for complex objects
- **d)** There’s no real difference — the classification is arbitrary

<sub>Screenshot: `msedge_qMWh7Q2htV.png`</sub>

#### Q4. Adapter & Facade Scenario Based

Your app calls Yes Bank’s do_payment() and get_acc_balance() directly everywhere in the codebase. Business now wants to add HDFC Bank, whose method names are totally different. What’s the correct fix per the lecture?

- **a)** Edit Yes Bank’s source code so its method names match HDFC’s
- **b)** Create a common BankAPI interface, and write one adapter class per bank that translates calls into that bank’s real methods
- **c)** Rewrite PhonePe with if/elif branches for each bank
- **d)** Merge Yes Bank and HDFC into a single class

<sub>Screenshot: `msedge_OHCLOM5rNI.png`</sub>

#### Q5. Code Output for this

What gets printed?
```python
class YesBank:
    def do_payment(self, account, amt):
        return 0 # 0 means success

class YesBankAdapter(BankAPI):
    def __init__(self, yes_bank):
        self.yes_bank = yes_bank

    def pay(self, amount, account):
        status = self.yes_bank.do_payment(account, amount)
        return status == 0

adapter = YesBankAdapter(YesBank())
print(adapter.pay(100, "ACC1"))
```

- **a)** 0
- **b)** None
- **c)** True
- **d)** False

<sub>Screenshot: `msedge_1KEG2lemLE.png`</sub>

#### Q6. Python - Debug the code

```python
class Amazon:
    def order_place(self):
        self.invoice_generation()
        self.wms.update()
        self.ims.update()
        self.emails.send_email()
```

The team wants to apply the Facade pattern here to keep Amazon clean. What's wrong with the current code from a Facade perspective?

- **a)** The method name `order_place` should be renamed to `facade_order_place`
- **b)** Amazon is missing a BankAPI interface
- **c)** There's nothing wrong — this already is a Facade
- **d)** Amazon.order_place() is doing the coordination job of four unrelated subsystems itself, instead of delegating to a dedicated Facade class

<sub>Screenshot: `msedge_0NwtxPcrhH.png`</sub>

#### Q7. Python- scenario based

A class talks to three different logging services, each with a different API, and combines their output into one log() method. According to the lecture, this design is:

- **a)** Both — one Adapter per logging service to normalize each API, all sitting inside one Facade that exposes a single log() method
- **b)** Only an Adapter, since it's about translating between APIs
- **c)** Only a Facade, since it exposes one simple method
- **d)** Neither — this is a Factory pattern

<sub>Screenshot: `msedge_6jUKeiOUFd.png`</sub>

#### Q8. Debug the code - Intermediate Question-6

```python
class PhonePeFacade:
    def __init__(self, phone_pe):
        self.phone_pe = phone_pe

    def checkout(self, amount, account, bank_name):
        if bank_name == "YesBank":
            self.phone_pe.bank_api = YesBankAdapter(YesBank())
        elif bank_name == "HDFCBank":
            self.phone_pe.bank_api = HDFCBankAdapter(HDFCBank())
        return self.phone_pe.bank_api.pay(amount, account)
```

What design flaw does the AI Corner exercise identify in this Facade?

- **a)** It's missing a try/except block around pay()
- **b)** It re-introduces the exact bank-selection coupling the Adapter pattern was meant to eliminate — adding a new bank still means editing this class
- **c)** PhonePeFacade should inherit from BankAPI
- **d)** The constructor should not take phone_pe as a parameter

<sub>Screenshot: `msedge_7mzggzQJFH.png`</sub>

#### Q9. Thoery for Beginner Question-07

Suppose PhonePe is later refactored so it depends directly on YesBankAdapter (not on the BankAPI interface). It still works fine today. What has actually been lost by removing the interface, even though nothing is broken yet?

- **a)** Nothing — as long as it compiles and passes tests, the interface was optional
- **b)** The ability to swap in a different adapter (e.g., for HDFC) without changing PhonePe’s code — PhonePe is now coupled to one specific adapter class instead of an abstraction
- **c)** YesBankAdapter would stop being able to wrap YesBank
- **d)** The Adaptee (YesBank) would need to change its method names

<sub>Screenshot: `msedge_feKenH91EL.png`</sub>

#### Q10. Scenario Based - Intermediate Question -08

```python
# Version 1
class OrderPlacedFacade:
    def __init__(self):
        self.wms = WMS()
        self.ims = IMS()

# Version 2
class OrderPlacedFacade:
    def __init__(self, wms, ims):
        self.wms = wms
        self.ims = ims
```

A new requirement comes in: unit tests need to run OrderPlacedFacade against fake/mock warehouse and inventory systems, without touching the real ones. Which version supports this without modifying OrderPlacedFacade’s code, and why?

- **a)** Version 1 — because it’s simpler and has fewer parameters
- **b)** Version 1 — because internal creation is always safer for testing
- **c)** Both are equally testable
- **d)** Version 2 — because the caller can pass in mock wms/ims objects at construction time, instead of the Facade being hardwired to the real concrete classes

<sub>Screenshot: `msedge_heFVWbStpr.png`</sub>

### Additional Problems

#### Q3. Homework Question-01

A junior developer says: “I added a wrapper class in front of our payment code, so I’ve used the Facade pattern.” Looking closer, the wrapper only calls into a single third-party payment class, translating its method names and parameter shapes to match what the rest of the codebase expects — no other subsystem is involved. What's the more accurate assessment?

- **a)** This is actually Adapter, not Facade — it’s translating one incompatible interface, not simplifying coordination across multiple subsystems
- **b)** This is correctly a Facade, since any wrapper class counts as one
- **c)** This is neither pattern, since only one class is involved
- **d)** This is both patterns simultaneously, since it wraps something

<sub>Screenshot: `msedge_wulniu0JPP.png`</sub>

#### Q4. Python Homework- Scenario Based

Your app needs to support OpenAI, Anthropic, and Gemini LLM SDKs, each with different request shapes and parameter names. You want your app to code against one common interface. Which pattern applies, and why?

- **a)** Facade — because it hides complexity
- **b)** Adapter — because it translates each SDK’s different shape into one common interface (ChatModel) your app depends on
- **c)** Singleton — because you only need one instance
- **d)** Strategy — because you’re switching algorithms

<sub>Screenshot: `msedge_a4FcbvM6Dg.png`</sub>

#### Q5. Code Output -Intermediate

```python
class ChatModel(ABC):
    @abstractmethod
    def generate(self, prompt, params): ...

class OpenAIAdapter(ChatModel):
    def __init__(self, client):
        self.client = client
    def generate(self, prompt, params):
        return f"OpenAI response to: {prompt}"

def run(model: ChatModel, prompt):
    return model.generate(prompt, {})

adapter = OpenAIAdapter(client=None)
print(run(adapter, "Hello"))
```
What gets printed?

- **a)** Error — run() cannot accept an Adapter object
- **b)** None
- **c)** OpenAI response to: Hello
- **d)** ChatModel response to: Hello

<sub>Screenshot: `msedge_85UEWlaZH2.png`</sub>

#### Q6. Debug the code - Intermediate Question 04

```python
def open_account(self, acc_number, holder_name):
    ...

class YesBankAdapter(BankAPI):
    def __init__(self, yes_bank):
        self.yes_bank = yes_bank

    def add_bank_account(self, bank):
        self.yes_bank.open_account(bank.holder_name, bank.account_number)
```

Assume Bank.__init__(self, account_number, account_holder_name) sets self.account_number and self.account_holder_name.

What's the bug?

- **a)** YesBankAdapter should inherit from Bank, not BankAPI
- **b)** open_account should not take any arguments
- **c)** There is no bug
- **d)** bank.holder_name does not exist (it’s bank.account_holder_name), and the arguments are passed in the wrong order — it should be open_account(bank.account_number, bank.account_holder_name)

<sub>Screenshot: `msedge_n5VrJA5ePe.png`</sub>

#### Q7. Question-05 Python Scenario Based

An AI coding assistant receives one user message, then internally pulls context, plans steps, calls tools, updates memory, and returns one final answer. The user sees only “message in, answer out.” What pattern does this AgentFacade.run() represent, and why?

- **a)** Facade — because it hides the coordination of multiple internal subsystems (retriever, planner, tool executor, memory) behind one simple run() entry point
- **b)** Adapter — because it translates between different tool APIs
- **c)** Singleton — because there is only one agent
- **d)** Builder — because it constructs a response step by step

<sub>Screenshot: `msedge_zdQjoANs3i.png`</sub>

#### Q8. Code Output - Intermediate

```python
class InvoiceService:
    def generate(self, order): print("Invoice generated")

class WMS:
    def update(self, order): print("Warehouse updated")

class OrderPlacedFacade:
    def __init__(self, invoice_service, wms):
        self.invoice_service = invoice_service
        self.wms = wms
    def on_order_place(self, order):
        self.invoice_service.generate(order)
        self.wms.update(order)

facade = OrderPlacedFacade(InvoiceService(), WMS())
facade.on_order_place("order123")
```
What is printed, in order?

- **a)** “Warehouse updated” then “Invoice generated”
- **b)** “Invoice generated” then “Warehouse updated”
- **c)** Only “Invoice generated”
- **d)** Nothing — this raises an error

<sub>Screenshot: `msedge_7xADLLvCvz.png`</sub>

#### Q9. Debug the code - Question 07

A teammate adds a new bank to the system this way:

```python
class PhonePe:
    def __init__(self, bank_api):
        self.bank_api = bank_api

    def perform_bank_operations(self, bank_name):
        if bank_name == "YesBank":
            self.bank_api = YesBankAdapter(YesBank())
        elif bank_name == "HDFCBank":
            self.bank_api = HDFCBankAdapter(HDFCBank())
        elif bank_name == "ICICIBank":
            self.bank_api = ICICIBankAdapter(ICICIBank())
        self.bank_api.pay(100.0, "ACC1")
```

What principle does this violate, based on the lecture's Open/Closed discussion?

- **a)** Single Responsibility — PhonePe should not have a constructor
- **b)** Dependency Injection — bank_api should never be passed into init
- **c)** Open/Closed Principle — PhonePe had to be edited (new elif) to support ICICI, instead of just adding a new adapter class and leaving PhonePe untouched
- **d)** Liskov Substitution — ICICIBankAdapter cannot substitute BankAPI

<sub>Screenshot: `msedge_AIV2aekkQR.png`</sub>

#### Q10. Question - 08 scenario based Intermediate

A ride-hailing app needs to: (1) call three different maps SDKs — Google Maps, Mapbox, and OpenStreetMap — through one common MapProvider interface, and (2) offer callers a single book_ride() method that internally picks a map provider, calculates fare, finds a driver, and sends a confirmation. Which combination of patterns fits, and how would they relate to each other?

- **a)** Only one Facade is needed — it can also handle translating the three different maps SDKs internally
- **b)** One Adapter per maps SDK (to normalize their different APIs into MapProvider), plus one Facade around book_ride() that uses those adapters as part of its coordination
- **c)** Only three Adapters are needed — book_ride() doesn't need a Facade since it's just one method
- **d)** This scenario doesn't fit either pattern since it involves both APIs and multi-step coordination

<sub>Screenshot: `msedge_CezABJMAE1.png`</sub>

## MCQs for lesson: Backend LLD: Design Patterns: Behavioural Design Patterns

_Class date: Wed, 19 Aug 2026_

### Assignment

#### Q4. shared interface

What is the main idea behind having one shared interface with many classes that each do a task in their own way?

- **a)** It hides all the code so nobody can read it
- **b)** It lets you add a new way of doing the task without changing the code that already works
- **c)** It forces every class to behave exactly the same way
- **d)** It removes the need for interfaces completely

<sub>Screenshot: `msedge_GIOUaTA7Zv.png`</sub>

#### Q5. code output.

```python
class Shape:
    def area(self):
        pass

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side * self.side

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def area(self):
        return 3.14 * self.radius * self.radius

shapes = [Square(4), Circle(2)]
for s in shapes:
    print(round(s.area(), 2))
```
What does this code print?

- **a)** 16 and 12.56
- **b)** 16 and 12.6
- **c)** 8 and 6.28
- **d)** An error, because Shape has no area logic

<sub>Screenshot: `msedge_zvDdtlFnz2.png`</sub>

#### Q6. debug the code

```python
class Notifier:
    def notify(self, message):
        pass

class EmailNotifier(Notifier):
    def notify(self, message):
        print("Email: " + message)

class App:
    def __init__(self):
        self.notifier = EmailNotifier()

    def send(self, message):
        self.notifier.alert(message)

app = App()
app.send("Server is down")
```

What is wrong with this code?

- **a)** EmailNotifier does not inherit from Notifier
- **b)** The send method never calls a notifier at all
- **c)** send() calls alert(), but EmailNotifier only has a notify() method, so this will throw an error
- **d)** print() cannot be used inside a class method

<sub>Screenshot: `msedge_IA0bSKC1mL.png`</sub>

#### Q7. [Scenario]

A photo editing app lets users choose between three ways to compress an image: high quality, balanced, or high compression. The user picks one option at a time, and the app runs only that one compression method. Which design idea best fits this situation?

- **a)** Print the same message repeatedly
- **b)** Keep all compression logic in one long if-else chain
- **c)** Use a database table for every image
- **d)** Give each compression option its own class behind a shared interface, and let the app use whichever one the user picked

<sub>Screenshot: `msedge_11CZSiYRsT.png`</sub>

#### Q8. [Theory]

Why is it usually a bad idea to check if type == "x" inside a class that's supposed to work with many different types generically?

- **a)** It ties that class to knowing specific details it shouldn't need to know about, making it harder to add new types later
- **b)** It makes the code run faster
- **c)** It is required by every programming language
- **d)** It automatically creates new classes for you

<sub>Screenshot: `msedge_KSRWxhSIq1.png`</sub>

#### Q9. [Code Output]

```python
class Listener:
    def update(self, value):
        pass

class Printer(Listener):
    def update(self, value):
        print(f"Got: {value}")

class Doubler(Listener):
    def update(self, value):
        print(f"Doubled: {value * 2}")

class Source:
    def __init__(self):
        self.listeners = []

    def add(self, listener):
        self.listeners.append(listener)

    def fire(self, value):
        for l in self.listeners:
            l.update(value)

source = Source()
source.add(Printer())
source.add(Doubler())
source.fire(5)
```

What does this code print?

- **a)** Got: 5
- **b)** Doubled: 10
- **c)** Got: 5 followed by Doubled: 10
- **d)** Nothing, because fire() was never called correctly

<sub>Screenshot: `msedge_zBt4xadGel.png`</sub>

#### Q10. [Scenario].

A news app lets many different screens (Home screen, Widget, Push Notification service) know whenever a new headline is published. The app doesn't need to know how many screens exist or what each one does with the headline — it just announces that a new headline arrived. What best describes this setup?

- **a)** Each screen must edit the app's main publishing code to add itself
- **b)** One publisher announces an event, and every interested party reacts on its own without the publisher knowing details about them
- **c)** The app must pick exactly one screen to update at a time
- **d)** The app needs a factory to create new headlines

<sub>Screenshot: `msedge_yXbMJsfd61.png`</sub>

### Additional Problems

#### Q4. Identify Problem

When many unrelated parts of a system need to react to the same event, what problem shows up if that event source calls each one of them by name directly inside its own code?

- **a)** The code becomes faster
- **b)** The event source needs less memory
- **c)** Every time a new reactor is added, the event source's code must be edited again
- **d)** The reactors stop working entirely

<sub>Screenshot: `msedge_BejxrB4Ap4.png`</sub>

#### Q5. [Code Output].

```python
class Discount:
    def apply(self, price):
        return price

class PercentDiscount(Discount):
    def __init__(self, percent):
        self.percent = percent
    def apply(self, price):
        return price - (price * self.percent / 100)

class FlatDiscount(Discount):
    def __init__(self, amount):
        self.amount = amount
    def apply(self, price):
        return price - self.amount

def checkout(price, discount):
    return discount.apply(price)

print(checkout(200, PercentDiscount(10)))
print(checkout(200, FlatDiscount(30)))
```

What is printed?

- **a)** 200 and 200
- **b)** 180.0 and 170
- **c)** 20 and 30
- **d)** An error, since Discount has no real apply logic

<sub>Screenshot: `msedge_jd1B0Flnod.png`</sub>

#### Q6. [Debug the Code].

```python
class Shipper:
    def ship(self, order):
        pass

class ExpressShipper(Shipper):
    def ship(self, order):
        return f"Shipping {order} quickly"

class StandardShipper(Shipper):
    def ship(self, order):
        return f"Shipping {order} normally"

class OrderService:
    def __init__(self, shipper):
        self.shipper = shipper

    def process(self, order):
        return self.shipper.ship(order)

service = OrderService(Shipper())
print(service.process("Book"))
```

What will happen when this code runs?

- **a)** It prints "Shipping Book quickly"
- **b)** It prints "Shipping Book normally"
- **c)** It prints "Shipping Book" with nothing else
- **d)** It prints None, because Shipper's ship() method has no real logic and simply returns nothing

<sub>Screenshot: `msedge_MBpGvbS8oo.png`</sub>

#### Q7. .[Scenario].

A music app wants to let users pick between three ways to sort their playlist: by song name, by artist, or by most recently added. Only one sorting method runs at a time, based on what the user picked. What is the best way to design this?

- **a)** Give each sorting method its own class behind a shared interface, and let the app use whichever class matches the user's choice
- **b)** Write one function with three separate if-else blocks that never change
- **c)** Create a new playlist every time the user changes the sort option
- **d)** Store every possible sorted order in advance

<sub>Screenshot: `msedge_ZWkSmS7Ko0.png`</sub>

#### Q8. [Theory]

What is the key difference between choosing one way to do something and letting many things react to the same event?

- **a)** There is no real difference between the two
- **b)** Choosing one way runs exactly one piece of logic; letting many things react means every registered piece of logic runs, one after another
- **c)** Choosing one way always runs slower
- **d)** Letting many things react only works with numbers

<sub>Screenshot: `msedge_gc2bsWdWhx.png`</sub>

#### Q9. [Code Output].

What is printed, in order?
```python
class Alert:
    def notify(self, msg):
        pass

class SmsAlert(Alert):
    def notify(self, msg):
        print(f"SMS: {msg}")

class EmailAlert(Alert):
    def notify(self, msg):
        print(f"Email: {msg}")

class System:
    def __init__(self):
        self.alerts = []

    def subscribe(self, alert):
        self.alerts.append(alert)

    def trigger(self, msg):
        for a in self.alerts:
            a.notify(msg)

notify_system = System()
notify_system.subscribe(SmsAlert())
notify_system.trigger("Low battery")
notify_system.subscribe(EmailAlert())
notify_system.trigger("Battery critical")
```

- **a)** SMS: Low battery only
- **b)** Email: Battery critical only
- **c)** SMS: Low battery, then SMS: Battery critical, then Email: Battery critical
- **d)** SMS: Low battery, then Email: Low battery, then SMS: Battery critical, then Email: Battery critical

<sub>Screenshot: `msedge_HjeqyDnfbL.png`</sub>

#### Q10. [Scenario]#2

An online store wants three different systems — inventory, accounting, and marketing — to each react on their own whenever a sale happens, without the checkout code needing to know anything about what each system does. What fits best?

- **a)** The checkout code must call each system by name every time a new one is added
- **b)** Only one system should be allowed to react to a sale
- **c)** The checkout code should stop working until all three systems are ready
- **d)** The checkout code should just announce that a sale happened, and let each interested system register itself and react independently

<sub>Screenshot: `msedge_oYv4AsEs3y.png`</sub>

## MCQs for lesson: Backend LLD: UML Diagrams

_Class date: Fri, 21 Aug 2026_

### Assignment

#### Q1. SCALER QUESTION 39900 f6d0

In a car manufacturing simulation, there's a class for generic vehicle properties. You have to create classes for a car, truck and motorcycle. What is the nature of the relationship between the vehicle class and the car, truck, and motorcycle classes?

- **a)** Association
- **b)** Composition
- **c)** Aggregation
- **d)** Inheritance

<sub>Screenshot: `msedge_oCT9wEy7pS.png`</sub>

#### Q2. SCALER QUESTION 39902 2f7c

In a drawing application, there's a class for a generic shape called Shape . You have to create classes for Circle , Rectangle , and Triangle . What is the nature of the relationship between the Shape class and the Circle, Rectangle, and Triangle classes?

- **a)** Association
- **b)** Composition
- **c)** Aggregation
- **d)** Inheritance

<sub>Screenshot: `msedge_3rp5tO7Tz8.png`</sub>

#### Q3. SCALER QUESTION 39904 29a3

In a software application, there's a class called Animal with properties and methods common to all animals. You have to create classes for Dog, Cat, and Bird. What is the nature of the relationship between the Animal class and the Dog, Cat, and Bird classes?

- **a)** Association
- **b)** Composition
- **c)** Aggregation
- **d)** Inheritance

<sub>Screenshot: `msedge_0trMmB1DSE.png`</sub>

#### Q4. SCALER QUESTION 39930 e2e3

In a library management system, there's a class for a library and a class for a book. What is the nature of the relationship between the library class and the book class?

- **a)** Association
- **b)** Composition
- **c)** Aggregation
- **d)** Inheritance

<sub>Screenshot: `msedge_nLmpBczJGC.png`</sub>

#### Q5. SCALER QUESTION 39931 206c

In a university system, there's a class for a department and a class for a professor. What is the nature of the relationship between the department class and the professor class?

- **a)** Association
- **b)** Composition
- **c)** Aggregation
- **d)** Inheritance

<sub>Screenshot: `msedge_tNcFBGWee3.png`</sub>

#### Q6. SCALER QUESTION 39932 d121

In a social media application, there's a class for a user and a class for a post.
What is the nature of the relationship between the user class and the post class?

- **a)** Association
- **b)** Composition
- **c)** Aggregation
- **d)** Inheritance

<sub>Screenshot: `msedge_3ZVVlq8hw1.png`</sub>

#### Q7. SCALER QUESTION 39933 1e99

Imagine a school enrollment system where a class represents a course. The course class contains objects representing enrolled students. However, if the course is closed or removed, the students still exist in the system and may be enrolled in other courses. What type of relationship exists between the course class and the student objects, where the student class is independent of the lifecycle of the course class?

- **a)** Composition
- **b)** Aggregation
- **c)** Inheritance

<sub>Screenshot: `msedge_mwK3rfcCeS.png`</sub>

#### Q8. SCALER QUESTION 39934 633d

In a music streaming application, a class represents a playlist. The playlist class contains objects representing songs. If the playlist is deleted, the songs still exist in the system and may be part of other playlists. What type of relationship exists between the playlist class and the song objects, where the song class is independent of the lifecycle of the playlist class?

- **a)** Composition
- **b)** Aggregation
- **c)** Inheritance

<sub>Screenshot: `msedge_dzfp2uXEbV.png`</sub>

#### Q9. SCALER QUESTION 39935 da79

In a social media application, a class represents a user. The user class contains objects representing posts. If the user account is deleted, the posts still exist in the system. What type of relationship exists between the user class and the post objects, where the post class is independent of the lifecycle of the user class?

- **a)** Composition
- **b)** Aggregation
- **c)** Inheritance

<sub>Screenshot: `msedge_Qgc28QhLIH.png`</sub>

#### Q10. SCALER QUESTION 39937 c101

In a car manufacturing simulation, a class represents a car. The car class contains objects representing the engine, wheels, and other parts. If the car object is destroyed, the engine, wheels, and other parts are also destroyed. What type of relationship exists between the car class and the engine, wheels, and other parts, where the parts are dependent on the lifecycle of the car?

- **a)** Composition
- **b)** Aggregation
- **c)** Inheritance

<sub>Screenshot: `msedge_e7tuIv7Pig.png`</sub>

#### Q11. SCALER QUESTION 39938 f45b

In a drawing application, there is a Canvas class. The canvas class contains objects representing shapes such as circles, rectangles, and triangles. If the canvas object is destroyed, the shapes are also destroyed. What type of relationship exists between the canvas class and the shapes, where the shapes are dependent on the lifecycle of the canvas?

- **a)** Composition
- **b)** Aggregation
- **c)** Inheritance

<sub>Screenshot: `msedge_LZL8ga3Ci4.png`</sub>

#### Q12. SCALER QUESTION 39939 8f4f

Imagine a class for a notebook. The notebook class contains objects representing pages. If the notebook object is destroyed, the pages are also destroyed. What type of relationship exists between the notebook class and the pages, where the pages are dependent on the lifecycle of the notebook?

- **a)** Composition
- **b)** Aggregation
- **c)** Inheritance

<sub>Screenshot: `msedge_l1uCYzRlun.png`</sub>

#### Q13. Primary Key Core Purpose

What is the primary purpose of a PRIMARY KEY in a database table?

- **a)** To uniquely identify each row in the table
- **b)** To link one table to another
- **c)** To make queries run faster automatically
- **d)** To enforce a fixed number of columns

<sub>Screenshot: `msedge_tXs0OAMTWL.png`</sub>

#### Q14. Modeling Joint Account Ownership

A banking app allows joint accounts — one account can have multiple owners, and one person can be an owner on multiple accounts. How should this be modeled in the schema?

- **a)** Add an owner_id column directly inside accounts
- **b)** Create a separate junction table (e.g. account_owners) holding account_id and owner_id
- **c)** Add an account_id column directly inside owners
- **d)** Store all owner names as a comma-separated list inside accounts

<sub>Screenshot: `msedge_MGZU8ZUCzi.png`</sub>

#### Q15. Counting Employees By Department

Given this schema and data:
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    department_id INT
);
```
Rows: (1, 'A', 1), (2, 'B', 2), (3, 'C', 2), (4, 'D', 3)
What does SELECT COUNT(*) FROM employees WHERE department_id = 2; return?

- **a)** 1
- **b)** 2
- **c)** 3
- **d)** 4

<sub>Screenshot: `msedge_GkUXN3ej6u.png`</sub>

#### Q16. Duplicated Customer Data Fix

A teammate wrote this schema for an orders system:

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    product VARCHAR(255)
);
```

There's already a separate customers table storing customer details. What's wrong with this design, and what's the fix?

- **a)** Nothing is wrong — storing the name and email directly avoids extra joins
- **b)** product should be split into product_name and product_price
- **c)** id should not be declared as a primary key since orders can repeat
- **d)** customer_name and customer_email duplicate data that already lives in customers — replace both with a single customer_id foreign key instead

<sub>Screenshot: `msedge_s6ffjFaVHJ.png`</sub>

#### Q17. Composite Primary Key Definition

In a many-to-many junction table like enrollments, some teams skip a separate surrogate id column entirely and instead make the combination of both foreign keys (student_id + course_id together) the primary key. What is this called?

- **a)** A composite primary key
- **b)** A duplicate key
- **c)** A foreign primary key
- **d)** A static key

<sub>Screenshot: `msedge_7BkQadrifx.png`</sub>

### Additional Problems

#### Q1. Dashed Hollow Triangle Meaning

In a Class Diagram, what does a dashed line with a hollow triangle arrowhead represent?

- **a)** A class implementing an interface
- **b)** A class extending another class
- **c)** Aggregation between two classes
- **d)** Composition between two classes

<sub>Screenshot: `msedge_WrjLwEj5be.png`</sub>

#### Q2. Foreign Key Placement Rule

One instructor teaches many courses, but each course has only one instructor. Where should the foreign key go?

- **a)** In the instructors table
- **b)** In the courses table
- **c)** In both tables at once
- **d)** In a separate junction table

<sub>Screenshot: `msedge_WlQWH9dkQ1.png`</sub>

#### Q3. Fixed Columns Cap Relationship

A teammate wrote this schema for a blog, where one post can have many comments:

```sql
CREATE TABLE posts (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    comment_1 VARCHAR(500),
    comment_2 VARCHAR(500),
    comment_3 VARCHAR(500)
);
```

What is the main problem, and what's the correct fix?

- **a)** A fixed number of comment columns caps the relationship — create a separate comments table with a post_id foreign key instead
- **b)** id should not be declared as a primary key
- **c)** title should be split into two columns
- **d)** The comments should be merged into one column separated by commas

<sub>Screenshot: `msedge_JYr9cABHGT.png`</sub>

#### Q4. Restaurant Menu Items Composition

A Restaurant class has a List<MenuItem>. If the restaurant shuts down permanently, its menu items (like "Paneer Butter Masala") have no meaning anywhere else in the system — they only existed as part of that restaurant's menu. What relationship is this?

- **a)** Inheritance
- **b)** Composition
- **c)** Aggregation
- **d)** An interface implementation

<sub>Screenshot: `msedge_iVPEReSRDk.png`</sub>

#### Q5. Includes Vs Extends Relationship

In a Use Case Diagram, "Enroll in Course" always triggers "Make Payment" — there's no scenario where enrollment happens without it. What relationship connects these two use cases?

- **a)** Extends
- **b)** Actor
- **c)** System Boundary
- **d)** Includes

<sub>Screenshot: `msedge_SZvJoL2YW8.png`</sub>

#### Q6. Junction Table Enrollment Count

Given this SQL:

```sql
CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(255));
CREATE TABLE courses (id INT PRIMARY KEY, title VARCHAR(255));

CREATE TABLE enrollments (
    id INT PRIMARY KEY,
    student_id INT,
    course_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

Current rows in enrollments: (1, 1, 1), (2, 1, 2), (3, 2, 1) (columns: id, student_id, course_id)
How many courses is the student with id = 1 enrolled in?

- **a)** 3
- **b)** 0
- **c)** 2
- **d)** 1

<sub>Screenshot: `msedge_WZh4zjuJvM.png`</sub>

#### Q7. Doctor-Department Aggregation And FK

A hospital has a Department class and a Doctor class. A doctor belongs to one department at a time, but if a department is dissolved, doctors continue to exist and can be reassigned elsewhere. Which pair correctly identifies the relationship type AND the foreign key placement?

- **a)** Aggregation, with department_id placed inside the doctors table
- **b)** Composition, with department_id placed inside the doctors table
- **c)** Aggregation, with doctor_id placed inside the departments table
- **d)** Composition, with doctor_id placed inside the departments table

<sub>Screenshot: `msedge_GJ22HdnToX.png`</sub>

#### Q8. Purpose Of Database Normalization

What is the main purpose of normalization in database schema design?

- **a)** To duplicate frequently-used data across tables for faster reads
- **b)** To store each fact only once and reference it elsewhere with a foreign key, avoiding out-of-sync copies
- **c)** To ensure every table has exactly the same number of columns
- **d)** To turn every relationship into a many-to-many relationship

<sub>Screenshot: `msedge_SYCQ0U2hDZ.png`</sub>

#### Q9. Trip Route Coordinates Composition

A ride-sharing app's Trip class has a List<RouteCoordinate> — the GPS points making up that specific trip's path. If the trip record is deleted, those exact coordinates have no meaning anywhere else in the system. Which combination correctly describes the relationship and its notation?

- **a)** Association without ownership — plain line, no diamond
- **b)** Inheritance — hollow triangle
- **c)** Aggregation — hollow diamond
- **d)** Composition — filled diamond

<sub>Screenshot: `msedge_moHzzhcLBA.png`</sub>

