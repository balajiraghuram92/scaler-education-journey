# Python Vertical: Answer Keys to Review

The source screenshots had no answer keys, so every reference MCQ below carries an answer the content agents proposed. Each one was reasoned through, and code-trace questions were run where possible. Questions an agent was unsure about are marked **⚠ REVIEW**.

To correct an answer: edit the question's `isCorrect` flags (and its `explanation`) in **both** `api/Data/mcq-migration-data.json` and `scripts/mcq-migration-data.json`, then re-run the seeder. For the `python-engineering` course the seeder re-syncs existing rows, so corrections reach the database.

Total reference questions: 356. Flagged: 21.

Skipped as exact duplicates of a question in an earlier lesson (the source course re-used them): python-engineering/py-16/additional/q04 (duplicate of python-engineering/py-15/additional/q05); python-engineering/py-16/additional/q05 (duplicate of python-engineering/py-15/additional/q06); python-engineering/py-16/additional/q07 (duplicate of python-engineering/py-15/additional/q08); python-engineering/py-16/additional/q08 (duplicate of python-engineering/py-15/additional/q09); python-engineering/py-16/additional/q10 (duplicate of python-engineering/py-15/additional/q11); python-engineering/py-16/assignment/q03 (duplicate of python-engineering/py-15/assignment/q04); python-engineering/py-16/assignment/q06 (duplicate of python-engineering/py-15/assignment/q07); python-engineering/py-16/assignment/q07 (duplicate of python-engineering/py-15/assignment/q08); python-engineering/py-16/assignment/q08 (duplicate of python-engineering/py-15/assignment/q09); python-engineering/py-16/assignment/q09 (duplicate of python-engineering/py-15/assignment/q10).


## py-01-inheritance-mro-polymorphism: Inheritance, MRO and Polymorphism

- `python-engineering/py-01/additional/q01`: **(c)** For class D(B, C) where B and C both inherit from A, in what order does Python search for a method called on a D() instance?
- `python-engineering/py-01/additional/q02`: **(b)** super() in a multiple-inheritance chain refers to:
- `python-engineering/py-01/additional/q03`: **(b)** Given class A: pass, class B(A): pass, an object b = B(). Which is True?
- `python-engineering/py-01/additional/q04`: **(b)** Uber's dispatch(vehicle) calls vehicle.start(). If a totally unrelated Drone class (not inheriting from Vehicle) has a .start() method, what
- `python-engineering/py-01/additional/q05`: **(c)** What will be the output:
- `python-engineering/py-01/additional/q06`: **(d)** A Zone class defines __lt__ by area. Which of these will NOT work out of the box? **⚠ REVIEW:** Ambiguous: with only __lt__ defined, all four operations run; (d) is chosen because it is the only one that does not behave by value (membership uses identity hash and equality, not area).
- `python-engineering/py-01/additional/q07`: **(b)** In cooperative multiple inheritance with **kwargs-passing super().__init__ calls, the shared top-most ancestor's __init__:
- `python-engineering/py-01/additional/q08`: **(b)** Which best distinguishes Java overloading from Python's @singledispatch?
- `python-engineering/py-01/additional/q09`: **(b)** What will be the output:
- `python-engineering/py-01/additional/q10`: **(b)** Defining __eq__ on a class without also defining __hash__ causes:
- `python-engineering/py-01/assignment/q01`: **(b)** Given the hierarchy class A: pass, class B(A): pass, class C(A): pass, class D(B, C): pass, what does D.__mro__ show (ignoring object)? Appl
- `python-engineering/py-01/assignment/q02`: **(b)** In Uber's dispatch code, a function dispatch(vehicle) calls vehicle.start(). A colleague passes in an EmailNotification object (unrelated to
- `python-engineering/py-01/assignment/q03`: **(c)** What will be the output:
- `python-engineering/py-01/assignment/q04`: **(b)** In the diamond class EC(EV, CV) where EV and CV both define get_priority_score() differently (20 and 30), and EC defines nothing, what does 
- `python-engineering/py-01/assignment/q05`: **(c)** What will be the output:

## py-02-abcs-protocols-mixins: ABCs, Protocols and Mixins

- `python-engineering/py-02/additional/q01`: **(b)** What does @abstractmethod on a method inside an ABC subclass guarantee?
- `python-engineering/py-02/additional/q02`: **(d)** A PaymentGateway ABC has two abstract methods. StripeGateway inherits from it and implements both. StripeGateway is then subclassed by Strip
- `python-engineering/py-02/additional/q03`: **(c)** A Protocol is defined without @runtime_checkable. What happens when you call isinstance(some_obj, MyProtocol)?
- `python-engineering/py-02/additional/q04`: **(d)** A mixin named TimestampMixin adds a created_at attribute. It is designed to be combined via multiple inheritance. Which statement is true ab
- `python-engineering/py-02/additional/q05`: **(b)** __init_subclass__ runs:
- `python-engineering/py-02/additional/q06`: **(c)** class RGW(PaymentGateway, LoggingMixin, JSONMixin) — all three parents define describe(). Whose version does RGW().describe() call?
- `python-engineering/py-02/additional/q07`: **(b)** The type() of an ordinary Python class (e.g., type(str)) is:
- `python-engineering/py-02/additional/q08`: **(a)** An ABC defines @abstractmethod def validate(self). A subclass implements validate but with a different signature (def validate(self, strict=
- `python-engineering/py-02/additional/q09`: **(d)** Which is the key difference between nominal typing (ABC) and structural typing (Protocol)?
- `python-engineering/py-02/additional/q10`: **(b)** PaymentGateway uses __init_subclass__ with gateway_name keyword. A developer writes class TestGateway(PaymentGateway) (no gateway_name). Whi
- `python-engineering/py-02/assignment/q04`: **(c)** Uber's checkout team builds a PaymentGateway ABC with @abstractmethod for process_payment and refund. A new developer writes class StripeGat
- `python-engineering/py-02/assignment/q05`: **(b)** Uber integrates a third-party VendorFraudScanner (installed via pip, not editable) that has a scan(amount, location) method. The team define
- `python-engineering/py-02/assignment/q06`: **(b)** The team rewrites the fraud contract as @runtime_checkable class FraudCheckable(Protocol) with def scan(self, amount, location) -> bool. Wit
- `python-engineering/py-02/assignment/q07`: **(a)** RazorpayGateway is declared as class RazorpayGateway(PaymentGateway, LoggingMixin, JSONSerializableMixin). Both PaymentGateway and LoggingMi
- `python-engineering/py-02/assignment/q08`: **(d)** PaymentGateway uses __init_subclass__ with a gateway_name keyword to auto-register subclasses into PaymentGateway.registry. A new developer 

## py-03-magic-methods-data-model: Magic Methods and the Python Data Model

- `python-engineering/py-03/additional/q01`: **(c)** Uber's Trip class defines __repr__ but not __str__. What is the output of print(trip)?
- `python-engineering/py-03/additional/q02`: **(b)** A Vehicle class overrides __eq__ to compare by reg_number, but never defines __hash__. A developer runs Vehicle.__hash__ in the REPL. What d
- `python-engineering/py-03/additional/q03`: **(d)** Two Driver objects d1 and d2 have the same driver_id. __eq__ compares by driver_id, and __hash__ is defined as return hash(self.driver_id). 
- `python-engineering/py-03/additional/q04`: **(b)** a + b on custom objects is secretly routed through which mechanism?
- `python-engineering/py-03/additional/q05`: **(c)** Why does Python set __hash__ to None automatically the instant a class defines __eq__ (without also defining __hash__)?
- `python-engineering/py-03/additional/q06`: **(b)** Inside a with Resource() as r: block that raises an exception, which statement is TRUE about __exit__?
- `python-engineering/py-03/additional/q07`: **(b)** A class defines __getitem__ by delegating to an internal list (return self._data[index]) but does NOT write any special slicing logic. What 
- `python-engineering/py-03/additional/q08`: **(a)** A SurgePricing object is configured with multiplier and base_fare, then used as surge(4.2). Which dunder makes this possible, and what's the
- `python-engineering/py-03/additional/q09`: **(d)** A class defines __contains__ for membership tests (x in obj). Which best describes when Python calls it?
- `python-engineering/py-03/additional/q10`: **(c)** Which of these is the most accurate summary of the "one rule" for deciding whether to add a dunder method to a class?
- `python-engineering/py-03/assignment/q01`: **(d)** Uber's Driver class originally has no custom dunders. A dispatcher writes d1 = Driver("Ramesh", 4.8, driver_id="D101") and d2 = Driver("Rame
- `python-engineering/py-03/assignment/q02`: **(b)** After adding def __eq__(self, other): return self.driver_id == other.driver_id to Driver (with no hash defined), a dispatch engineer runs on
- `python-engineering/py-03/assignment/q03`: **(c)** A class defines only __repr__, no __str__. A developer runs print(some_object). What is printed?
- `python-engineering/py-03/assignment/q04`: **(d)** Inside a with TripTimer(trip) as t: block, a ValueError is raised (not the TripCancelledError that __exit__ explicitly checks for and return
- `python-engineering/py-03/assignment/q05`: **(b)** A SurgePricing class is configured once via __init__(multiplier, base_fare) and defines __call__(self, distance). A developer then writes su

## py-04-oop-lab-session: OOP Lab: Modelling a Real Domain

- `python-engineering/py-04/additional/q01`: **(a)** User is an ABC with abstract methods display_dashboard and can_borrow. Member implements both. PremiumMember(Member) adds a loyalty field bu
- `python-engineering/py-04/additional/q02`: **(c)** user_id is stored as self._user_id with only a @property getter (no setter). What happens when code runs member.user_id = "NEW"?
- `python-engineering/py-04/additional/q03`: **(b)** Member.MAX_BORROW_LIMIT is a class attribute set to 5. At runtime, Member.MAX_BORROW_LIMIT = 2 is executed. What happens to an existing Memb
- `python-engineering/py-04/additional/q04`: **(b)** A MagazineArchive has a borrow() method (meaning "log a photocopy"). lend_item checks isinstance(item, Borrowable) before calling borrow(). 
- `python-engineering/py-04/additional/q05`: **(c)** Searchable is a @runtime_checkable Protocol. A third-party JournalDB class (uneditable) has matches(query) -> bool. Does isinstance(JournalD
- `python-engineering/py-04/additional/q06`: **(b)** Loan.__init__ calls super().__init__() where Loan inherits from TimestampedMixin. TimestampedMixin.__init__ also calls super().__init__(**kw
- `python-engineering/py-04/additional/q07`: **(c)** Library defines __contains__(self, isbn) checking against internal _books. What does "N-1" in lib do under the hood?
- `python-engineering/py-04/additional/q08`: **(d)** In the code review, Design A has Book.borrow(member) owning lending logic. Design B has Library.lend(member, book) owning it. Which statemen
- `python-engineering/py-04/additional/q09`: **(a)** Book.__eq__ compares by isbn. Two books with different titles but same isbn are added to a set. How many entries does the set contain? **⚠ REVIEW:** The stem does not say __hash__ is defined; (a) is chosen because it assumes hash is also by isbn, as the option itself states, and the other options are clearly wrong.
- `python-engineering/py-04/additional/q10`: **(b)** Library defines __getitem__ delegating to self._books[index] but writes NO slicing logic. A user runs lib[:2]. What happens?
- `python-engineering/py-04/assignment/q01`: **(b)** The User class is an ABC with two abstract methods: display_dashboard and can_borrow. A developer creates class Volunteer(User) implementing
- `python-engineering/py-04/assignment/q02`: **(b)** User._id_counter is a class attribute incremented in User.__init__. Three users are created: two Members and one Librarian. What is User._id
- `python-engineering/py-04/assignment/q03`: **(a)** lend_item checks isinstance(item, Borrowable) before lending. A third-party AudioGuide class (you can't edit it) happens to have borrow, ret
- `python-engineering/py-04/assignment/q04`: **(c)** Searchable is defined as a @runtime_checkable Protocol requiring matches(query) -> bool. Book implements matches but does NOT inherit from S
- `python-engineering/py-04/assignment/q05`: **(d)** Loan defines __eq__ (comparing by book.isbn + member.user_id) but a developer forgets __hash__. They create two Loan objects for the same me

## py-05-processes-threads-gil: Processes, Threads and the GIL

- `python-engineering/py-05/additional/q02`: **(b)** What does the GIL (Global Interpreter Lock) actually guarantee?
- `python-engineering/py-05/additional/q03`: **(c)** Two threads both run this function, then the final value is printed: **⚠ REVIEW:** On CPython 3.10+ this exact loop often prints 2,000,000, because thread switches are checked only at calls and backward jumps; option (c) is the intended answer and the race is real in older versions, with any call between read and write, and on free-threaded builds.
- `python-engineering/py-05/additional/q04`: **(a)** Why does the scenario in H2 happen even though the GIL only lets one thread run at a time? **⚠ REVIEW:** Correct in principle (LOAD, ADD, STORE are separate bytecodes) but on 3.10+ the interpreter switches threads only at calls and backward jumps, so the race for this exact loop is rarely observed.
- `python-engineering/py-05/additional/q05`: **(b)** A student wants to speed up a task that makes 5 slow network API calls (each takes 1 second, mostly spent waiting). They're deciding between
- `python-engineering/py-05/additional/q06`: **(c)** What is the key difference in output/behavior between using raw multiprocessing.Process objects versus multiprocessing.Pool.map() for runnin
- `python-engineering/py-05/assignment/q04`: **(b)** What is the main difference between concurrency and parallelism?
- `python-engineering/py-05/assignment/q05`: **(d)** What will this print?
- `python-engineering/py-05/assignment/q06`: **(c)** In Python's threading module, what does .join() do?
- `python-engineering/py-05/assignment/q07`: **(b)** A student wrote:
- `python-engineering/py-05/assignment/q08`: **(a)** Given a single CPU-bound function cpu_heavy() that takes 4 seconds to run alone, what is the most likely total time if it's run twice using 

## py-06-executors-futures: Executors and Futures

- `python-engineering/py-06/additional/q01`: **(c)** Which is the best use case for ProcessPoolExecutor over ThreadPoolExecutor?
- `python-engineering/py-06/additional/q02`: **(d)** Why doesn't ProcessPoolExecutor speed up an I/O-bound task like web scraping, compared to ThreadPoolExecutor?
- `python-engineering/py-06/additional/q03`: **(b)** True or False: Using ThreadPoolExecutor automatically protects shared variables from race conditions (like counter += 1 from multiple thread
- `python-engineering/py-06/additional/q04`: **(d)** What is results, and in what order, once this finishes?
- `python-engineering/py-06/additional/q05`: **(d)** A student benchmarks CPU-heavy work and is confused why threads didn't help. Identify the flaw in their reasoning.
- `python-engineering/py-06/additional/q06`: **(d)** You're processing 4 large video files, applying a CPU-intensive filter to each, independently. Which is the better choice and why?
- `python-engineering/py-06/additional/q07`: **(c)** You submit 10 tasks to a ThreadPoolExecutor(max_workers=3). At any given instant, what is the maximum number of tasks actually running concu
- `python-engineering/py-06/additional/q08`: **(d)** You have a ThreadPoolExecutor task that sometimes throws an exception. You use executor.map() instead of submit() + individual futures. What
- `python-engineering/py-06/assignment/q02`: **(d)** What does executor.submit(fn, arg) return?
- `python-engineering/py-06/assignment/q03`: **(a)** Which statement about .done() and .result() is correct?
- `python-engineering/py-06/assignment/q04`: **(b)** A raw threading.Thread's target function raises an exception. What happens?
- `python-engineering/py-06/assignment/q05`: **(d)** How does a Future handle an exception raised inside the worker function?
- `python-engineering/py-06/assignment/q06`: **(c)** What guarantee does executor.map(fn, iterable) give you about result order?
- `python-engineering/py-06/assignment/q07`: **(d)** What will this print?
- `python-engineering/py-06/assignment/q08`: **(d)** What is the output of this code? **⚠ REVIEW:** Option (d) lists the values "0 2 Caught: bad value 6 8", but the code actually prints 0, 2, 4, "Caught: bad value", 8 (risky(3) raises, risky(2) returns 4); (d) is still the only option describing the correct behaviour (in order, exception caught for x=3).
- `python-engineering/py-06/assignment/q09`: **(d)** A student wrote this to collect driver locations. What does it get wrong relative to what today's lecture taught?
- `python-engineering/py-06/assignment/q10`: **(c)** Find the bug: the student wants to catch the error from a failed task, but the except block never triggers, even though fetch_driver_locatio
- `python-engineering/py-06/assignment/q11`: **(d)** You're building a system that downloads 100 images from different URLs. Which executor should you use, and why?

## py-07-synchronization-async-intro: Synchronization and an Introduction to Async

- `python-engineering/py-07/additional/q04`: **(d)** In the lecture, a Semaphore(3) was used to allow only 3 threads to run at once (like a parking lot with 3 spots). If instead you initialize 
- `python-engineering/py-07/additional/q05`: **(c)** For problems like "print first, then second, then third in strict order using multiple threads," why can a semaphore be used to enforce orde
- `python-engineering/py-07/additional/q06`: **(d)** What is the guaranteed printed order?
- `python-engineering/py-07/additional/q07`: **(c)** This is meant to make "second" print only after "first," using semaphores, but it has a bug:
- `python-engineering/py-07/additional/q08`: **(d)** For the "ZeroEvenOdd" problem (three threads: one prints only 0s, one prints only evens, one prints only odds, in strict interleaved order),
- `python-engineering/py-07/assignment/q04`: **(b)** What is a "critical section" in the context of threading.Lock?
- `python-engineering/py-07/assignment/q05`: **(c)** Why does a plain threading.Lock cause a deadlock if the same thread tries to acquire it twice (e.g., a locked function calling another locke
- `python-engineering/py-07/assignment/q06`: **(d)** What will this print?
- `python-engineering/py-07/assignment/q07`: **(d)** The following code is supposed to safely reserve seats but has a bug. What is wrong?
- `python-engineering/py-07/assignment/q08`: **(c)** A function outer() acquires a lock and then calls inner(), which also tries to acquire the same lock, from the same thread. Which tool corre

## py-08-decorators-iterators-generators: Decorators, Iterators and Generators

- `python-engineering/py-08/additional/q01`: **(b)** Why does a decorator that accepts an argument, like @repeat(3), need one extra layer compared to a normal decorator?
- `python-engineering/py-08/additional/q02`: **(b)** What does this print?
- `python-engineering/py-08/additional/q03`: **(c)** You have this stacked decorator setup: **⚠ REVIEW:** The printed question text contained a stray "A) B) C) D)" line from the source rendering; it was removed.
- `python-engineering/py-08/additional/q04`: **(a)** When would you choose a class-based decorator (using __call__) over a regular function decorator?
- `python-engineering/py-08/additional/q05`: **(d)** What is printed?
- `python-engineering/py-08/additional/q06`: **(b)** In the lecture's @singleton decorator, what makes Config() always return the same object on every call?
- `python-engineering/py-08/additional/q07`: **(d)** What is the key difference between return and yield inside a function?
- `python-engineering/py-08/additional/q08`: **(a)** You need to process a 10 GB log file on a machine with only 8 GB of RAM. Based on the lecture, what's the correct approach?
- `python-engineering/py-08/additional/q09`: **(a)** What does this print?
- `python-engineering/py-08/additional/q10`: **(b)** Why is sys.getsizeof() so much smaller for a generator expression than for an equivalent list?
- `python-engineering/py-08/assignment/q01`: **(b)** In Python, what does it mean to say functions are "first-class"?
- `python-engineering/py-08/assignment/q02`: **(b)** What does this print?
- `python-engineering/py-08/assignment/q03`: **(b)** What is a closure?
- `python-engineering/py-08/assignment/q04`: **(c)** Why does this code crash?
- `python-engineering/py-08/assignment/q05`: **(b)** What is the correct relationship between @my_decorator and manual wrapping?
- `python-engineering/py-08/assignment/q06`: **(b)** What does add.__name__ print after this?
- `python-engineering/py-08/assignment/q07`: **(c)** You are writing a decorator that must work on any function, regardless of how many arguments that function takes. What should the wrapper's 
- `python-engineering/py-08/assignment/q08`: **(a)** What two special methods does an object need in order to work as an iterator?
- `python-engineering/py-08/assignment/q09`: **(b)** What is printed by this loop?
- `python-engineering/py-08/assignment/q10`: **(b)** Why does a for loop stop automatically without you writing any stopping condition?

## py-09-collections-dataclasses-typing-exceptions: Collections, Dataclasses, Type Hints and Exceptions

- `python-engineering/py-09/additional/q03`: **(a)** What is the main benefit of using @dataclass on a class instead of writing it manually?
- `python-engineering/py-09/additional/q04`: **(b)** Consider the following code snippet:
- `python-engineering/py-09/additional/q05`: **(c)** A student tries to give every Member object an empty list of borrowed books:
- `python-engineering/py-09/additional/q06`: **(a)** You're writing a borrow(book, member) function for a library system. If the book isn't available, you want the caller to know exactly why it
- `python-engineering/py-09/additional/q07`: **(b)** Consider the following code snippet:
- `python-engineering/py-09/assignment/q03`: **(d)** You need to create a Student class with name and marks attributes for the sorting problem. You want it to have __init__, __repr__, and __eq_
- `python-engineering/py-09/assignment/q04`: **(b)** Consider the following code snippet:
- `python-engineering/py-09/assignment/q05`: **(a)** A student wrote this to group anagrams but it's not grouping correctly:
- `python-engineering/py-09/assignment/q06`: **(c)** You need to count how many times each word appears in a large paragraph, and then quickly find the 3 most frequent words. Which tool is the 
- `python-engineering/py-09/assignment/q07`: **(d)** Consider the following code snippet:

## py-10-solid-principles: SOLID Principles for Extensible Systems with AI Integrations

- `python-engineering/py-10/additional/q01`: **(b)** What is the difference between DIP (Dependency Inversion Principle) and DI (Dependency Injection)?
- `python-engineering/py-10/additional/q02`: **(c)** If a bird hierarchy has 4 independent behaviours (fly, dance, swim, sing), and you try to model each combination using plain "can/cannot" su **⚠ REVIEW:** The count assumes one subclass per combination of four independent yes/no behaviours (2^4 = 16); a different modelling of the hierarchy could justify another number, but 16 is the standard combinatorial answer.
- `python-engineering/py-10/additional/q03`: **(c)** A project has one utils.py file containing 40 unrelated functions — date logic, string logic, and file logic all mixed together. Which SRP t
- `python-engineering/py-10/additional/q04`: **(b)** Why does needing a try-except block (or an isinstance check) before calling a method on a subclass count as an LSP violation?
- `python-engineering/py-10/additional/q05`: **(b)** With type hints in place, what does a static type checker like mypy do differently from Python itself when this code runs?
- `python-engineering/py-10/additional/q06`: **(c)** What is printed when this runs?
- `python-engineering/py-10/additional/q07`: **(b)** Compare these two Penguin designs. What is the key difference in the error each one produces?
- `python-engineering/py-10/additional/q08`: **(b)** This code lets a VehicleService decide how each vehicle starts. A new team wants to add "ElectricStart" next month. What needs to change, an
- `python-engineering/py-10/additional/q09`: **(b)** Spot the issue in this OrderService code and name the principle it violates:
- `python-engineering/py-10/additional/q10`: **(b)** A new team wants to add a WhatsAppChannel to a notification system, and they are told they "cannot touch NotificationService directly." If t
- `python-engineering/py-10/additional/q11`: **(b)** An AI assistant was asked to "write a NotificationService using good design principles," and it produced an if-elif chain based on a channel
- `python-engineering/py-10/additional/q12`: **(a)** A checkout system currently uses Razorpay. The business wants to add Stripe next quarter, and possibly switch the default gateway per countr
- `python-engineering/py-10/additional/q13`: **(b)** SQLAlchemy's create_engine(url) reads the prefix of a connection string (like postgresql:// or mysql://) and automatically picks the right d
- `python-engineering/py-10/assignment/q01`: **(b)** What does the Single Responsibility Principle (SRP) actually say?
- `python-engineering/py-10/assignment/q02`: **(b)** According to the Open/Closed Principle (OCP), how should you add a new feature to an existing class?
- `python-engineering/py-10/assignment/q03`: **(a)** What does the Liskov Substitution Principle (LSP) require?
- `python-engineering/py-10/assignment/q04`: **(c)** What is the core idea behind the Interface Segregation Principle (ISP)?
- `python-engineering/py-10/assignment/q05`: **(b)** What does the Dependency Inversion Principle (DIP) say about two concrete classes?
- `python-engineering/py-10/assignment/q06`: **(a)** What is the output of r.get_area() here?
- `python-engineering/py-10/assignment/q07`: **(c)** What happens when this code runs?
- `python-engineering/py-10/assignment/q08`: **(b)** Which SOLID principle does this code violate, and why?
- `python-engineering/py-10/assignment/q09`: **(c)** What's wrong with this code, and which principle does it break?
- `python-engineering/py-10/assignment/q10`: **(b)** This class was designed for birds that can both fly and dance. What's the problem when Ostrich (which can only dance) inherits from it?
- `python-engineering/py-10/assignment/q11`: **(a)** A function process_order() validates the order, charges payment, updates inventory, and sends a confirmation email — all in one function. Wh
- `python-engineering/py-10/assignment/q12`: **(b)** A team adds a 6th discount type by adding another elif inside a apply_discount() function that already handles 5 discount types. Which princ
- `python-engineering/py-10/assignment/q13`: **(a)** A Machine abstract class declares print_doc(), scan(), and fax(). A class SimplePrinter inherits from it but only really prints — it raises 
- `python-engineering/py-10/assignment/q14`: **(c)** Inside OrderService, this line exists: self.gateway = RazorpayGateway(), where RazorpayGateway is a concrete class hardcoded directly. Which

## py-11-singleton: Design Patterns: Introduction and Singleton

- `python-engineering/py-11/additional/q03`: **(a)** Which of these real-world examples does the lecture NOT list as an existing Singleton in production systems?
- `python-engineering/py-11/additional/q04`: **(d)** What does this print?
- `python-engineering/py-11/additional/q05`: **(a)** This metaclass-based Singleton is supposed to be thread-safe, but a bug was introduced. Spot it. **⚠ REVIEW:** The question says a bug was introduced, but the code is correct; it only takes the lock on every call (a performance cost), so option (a) is the only defensible answer.
- `python-engineering/py-11/additional/q06`: **(c)** Why do some engineers avoid a class-based Singleton for objects that might get pickled? **⚠ REVIEW:** Option (c) holds for metaclass and decorator singletons; for a __new__-based singleton, unpickling calls __new__ and returns the live instance but overwrites its state. It is still the best option offered.
- `python-engineering/py-11/additional/q07`: **(b)** A test suite creates a DBConnection singleton, mutates some state on it, then finishes. The next test runs and unexpectedly sees leftover st
- `python-engineering/py-11/additional/q08`: **(a)** What does this print?
- `python-engineering/py-11/additional/q09`: **(d)** What is a genuine downside (con) of using the Singleton pattern, according to the lecture?
- `python-engineering/py-11/additional/q10`: **(d)** A junior engineer wrote this thinking it's thread-safe double-checked locking. What's actually wrong with it?
- `python-engineering/py-11/additional/q11`: **(b)** Your team needs ten different classes to all become singletons, with minimal repeated code and full thread-safety. Based on the lecture's co
- `python-engineering/py-11/additional/q12`: **(b)** Given the module below, what does the second script print?
- `python-engineering/py-11/assignment/q04`: **(b)** What is the main idea behind the Singleton pattern?
- `python-engineering/py-11/assignment/q05`: **(c)** Which of the following is a valid reason to use a Singleton?
- `python-engineering/py-11/assignment/q06`: **(c)** What will this code print?
- `python-engineering/py-11/assignment/q07`: **(c)** Why can't we just put the "only one instance" check inside __init__ instead of __new__?
- `python-engineering/py-11/assignment/q08`: **(b)** This code is meant to be a Singleton but has a bug. What's wrong?
- `python-engineering/py-11/assignment/q09`: **(a)** Your team's app creates its DBConnection singleton eagerly at module import time. QA reports that app startup has become noticeably slower. 
- `python-engineering/py-11/assignment/q10`: **(d)** Two threads, A and B, run this __new__ at nearly the same time, with _instance starting as None and no lock in place:
- `python-engineering/py-11/assignment/q11`: **(d)** In double-checked locking, why is the second None check (inside the lock) necessary if we already checked None once outside the lock?
- `python-engineering/py-11/assignment/q12`: **(a)** A teammate wrote this "quick and simple" singleton after asking an AI assistant. What important detail is missing, based on the AI Corner di
- `python-engineering/py-11/assignment/q13`: **(c)** You import a module-level settings object (plain variables, no class) in five different files across your FastAPI app. How many actual objec

## py-12-builder: Design Patterns: Builder

- `python-engineering/py-12/additional/q03`: **(b)** In the homework assignments, the Builder class must be marked with @WithBuilder. What is the purpose of this annotation? **⚠ REVIEW:** The @WithBuilder annotation belongs to the Java version of the assignments and does not exist in Python; (b) is the only option consistent with how the grader was described.
- `python-engineering/py-12/additional/q04`: **(c)** In the DatabaseConfiguration homework, the config object must be immutable once built. Which design choice from the Python lecture supports 
- `python-engineering/py-12/additional/q05`: **(b)** A developer writes a QueryBuilder where with_where("age > 18") is called three times to add three different conditions. But in the final Que
- `python-engineering/py-12/additional/q06`: **(b)** Why did the problem statement for "Builder Message" say the old way (multiple overloaded constructors) was "error-prone and hard to maintain
- `python-engineering/py-12/additional/q07`: **(b)** A student writes a MessageBuilder where build() just returns new Message(this) with no checks at all, even though a text message must always
- `python-engineering/py-12/additional/q08`: **(b)** builder = DatabaseConfigurationBuilder() **⚠ REVIEW:** The snippet mixes Java idioms into Python (a `//` comment, `.add` on a list); the answer assumes the intended meaning, that `build()` copies the list so later changes to the builder's list do not reach `config1`.
- `python-engineering/py-12/additional/q09`: **(b)** Which of these is the best reason to write validation logic inside build() rather than inside each individual setter (like with_username())?
- `python-engineering/py-12/additional/q10`: **(b)** A teammate says: "I don't need the Builder pattern for my Point class with just x and y. I'll just do Point(x, y) directly." Based on the le
- `python-engineering/py-12/assignment/q04`: **(c)** What is the main reason we use the Builder pattern instead of one big constructor with many parameters?
- `python-engineering/py-12/assignment/q05`: **(b)** def add_item(cart=[]):
- `python-engineering/py-12/assignment/q06`: **(b)** In the Builder pattern, why should every setter method (like set_name()) return self?
- `python-engineering/py-12/assignment/q07`: **(b)** class Builder:
- `python-engineering/py-12/assignment/q08`: **(a)** You are building a Student object. The rule is: grad_year must not be greater than 2022. Where should this check be written, based on what w
- `python-engineering/py-12/assignment/q09`: **(c)** class Helper:
- `python-engineering/py-12/assignment/q10`: **(b)** You ask an AI tool to generate a Builder for a class that has a tags list field. After build() runs, you change the original list you passed
- `python-engineering/py-12/assignment/q11`: **(c)** Which of these is NOT a good reason to use the Builder pattern for a class?

## py-13-prototype-registry: Design Patterns: Prototype and Registry

- `python-engineering/py-13/additional/q02`: **(b)** (Theory) In the cloud VM analogy from the lecture, what does the “golden image” represent in Prototype pattern terms?
- `python-engineering/py-13/additional/q03`: **(c)** (Scenario) In the SearchAPI example, the base URL, auth token, retry settings, and timeout rarely change between calls, but the search query
- `python-engineering/py-13/additional/q04`: **(d)** (Code Output)
- `python-engineering/py-13/additional/q05`: **(a)** (Code Debug)
- `python-engineering/py-13/additional/q06`: **(b)** (Theory) Why is it usually a bad idea for client code to copy an object by manually setting each field from outside the class (e.g., copy.os
- `python-engineering/py-13/additional/q07`: **(c)** (Scenario) A registry is being used like this:
- `python-engineering/py-13/additional/q08`: **(d)** (Code Output)
- `python-engineering/py-13/additional/q09`: **(a)** (Theory) According to the lecture, when is it reasonable to skip the Prototype pattern entirely and just construct an object normally?
- `python-engineering/py-13/additional/q10`: **(b)** (Scenario) A registry needs to store several different “welcome email”, “password reset email”, and “invoice email” templates, and retrieve/
- `python-engineering/py-13/assignment/q03`: **(a)** (Theory) What problem does the Prototype pattern mainly solve?
- `python-engineering/py-13/assignment/q04`: **(b)** (Code Output)
- `python-engineering/py-13/assignment/q05`: **(c)** (Code Debug) A student writes this registry method to add a new prototype only if it doesn't already exist:
- `python-engineering/py-13/assignment/q06`: **(d)** (Scenario) A Student class has an __init__ that takes no arguments and sets default values. A developer wants to also let Student be created
- `python-engineering/py-13/assignment/q07`: **(a)** (Theory) Why must every subclass of a Prototype-based class override clone() itself, even if the parent class already has a clone() method?
- `python-engineering/py-13/assignment/q08`: **(b)** (Code Output)
- `python-engineering/py-13/assignment/q09`: **(c)** (Code Debug) How should the buggy line from Q6 be fixed so that copy.installed_packages becomes fully independent from original.installed_pa **⚠ REVIEW:** The question text says "the buggy line from Q6", which refers to the shallow-copy question that is q08 in this numbering; the intended buggy line is `self.installed_packages = source.installed_packages`.
- `python-engineering/py-13/assignment/q10`: **(d)** (Scenario) A team keeps a dictionary-based registry of reusable templates, keyed by string names like "welcome_email" and "password_reset_em
- `python-engineering/py-13/assignment/q11`: **(a)** (Theory) Which statement best describes the difference between the Prototype pattern and the Registry pattern?

## py-14-factory: Design Patterns: Factory for Service Abstraction

- `python-engineering/py-14/additional/q04`: **(d)** What problem does the Simple Factory pattern solve when a class has repeated if/elif blocks to decide which object to create?
- `python-engineering/py-14/additional/q05`: **(a)** What will this print?
- `python-engineering/py-14/additional/q06`: **(b)** What's wrong with this Simple Factory method?
- `python-engineering/py-14/additional/q07`: **(c)** Which of these is true about Abstract Factory according to the lecture?
- `python-engineering/py-14/additional/q08`: **(d)** A document processing app needs DocumentParser, DocumentProcessor, and DocumentPrinter objects that must always match the same document type
- `python-engineering/py-14/additional/q09`: **(a)** What will this print?
- `python-engineering/py-14/additional/q10`: **(b)** Why is this design flawed based on the lecture's "vendor leak" discussion?
- `python-engineering/py-14/assignment/q04`: **(a)** What is the main purpose of the Simple Factory pattern?
- `python-engineering/py-14/assignment/q05`: **(b)** What will this code print?
- `python-engineering/py-14/assignment/q06`: **(c)** What happens when this code runs?
- `python-engineering/py-14/assignment/q07`: **(d)** Your team needs AudioDecoder, AudioProcessor, and AudioPlayer objects that must always come from the same format (e.g. all MP3, never MP3 de
- `python-engineering/py-14/assignment/q08`: **(a)** In the Abstract Factory pattern, what does supports_format typically do?
- `python-engineering/py-14/assignment/q09`: **(b)** What does this print?
- `python-engineering/py-14/assignment/q10`: **(c)** Why will this code fail?

## py-15-adapter-facade: Design Patterns: Adapter and Facade

- `python-engineering/py-15/additional/q04`: **(a)** A junior developer says: “I added a wrapper class in front of our payment code, so I’ve used the Facade pattern.” Looking closer, the wrappe
- `python-engineering/py-15/additional/q05`: **(b)** Your app needs to support OpenAI, Anthropic, and Gemini LLM SDKs, each with different request shapes and parameter names. You want your app 
- `python-engineering/py-15/additional/q06`: **(c)** class ChatModel(ABC): **⚠ REVIEW:** Snippet omits `from abc import ABC, abstractmethod`; assumed present, otherwise it would raise NameError.
- `python-engineering/py-15/additional/q07`: **(d)** class YesBank:
- `python-engineering/py-15/additional/q08`: **(a)** An AI coding assistant receives one user message, then internally pulls context, plans steps, calls tools, updates memory, and returns one f
- `python-engineering/py-15/additional/q09`: **(b)** class InvoiceService:
- `python-engineering/py-15/additional/q10`: **(c)** class PhonePe:
- `python-engineering/py-15/additional/q11`: **(b)** A ride-hailing app needs to: (1) call three different maps SDKs — Google Maps, Mapbox, and OpenStreetMap — through one common MapProvider in
- `python-engineering/py-15/assignment/q04`: **(a)** A Builder class controls the step-by-step construction of a complex object. An Adapter class wraps an existing object so a client can call i
- `python-engineering/py-15/assignment/q05`: **(b)** Your app calls Yes Bank’s dopayment() and getacc_balance() directly everywhere in the codebase. Business now wants to add HDFC Bank, whose m
- `python-engineering/py-15/assignment/q06`: **(c)** class YesBank:
- `python-engineering/py-15/assignment/q07`: **(d)** class Amazon:
- `python-engineering/py-15/assignment/q08`: **(a)** A class talks to three different logging services, each with a different API, and combines their output into one log() method. According to 
- `python-engineering/py-15/assignment/q09`: **(b)** class PhonePeFacade:
- `python-engineering/py-15/assignment/q10`: **(b)** Suppose PhonePe is later refactored so it depends directly on YesBankAdapter (not on the BankAPI interface). It still works fine today. What
- `python-engineering/py-15/assignment/q11`: **(d)** Two versions of the same Facade are shown below.

## py-16-decorator-flyweight: Design Patterns: Decorator and Flyweight

- `python-engineering/py-16/additional/q03`: **(a)** A junior developer says: “I added a wrapper class in front of our payment code, so I’ve used the Facade pattern.” Looking closer, the wrappe
- `python-engineering/py-16/additional/q06`: **(d)** def open_account(self, acc_number, holder_name):
- `python-engineering/py-16/additional/q09`: **(c)** A teammate adds a new bank to the system this way:
- `python-engineering/py-16/assignment/q04`: **(b)** Your app calls Yes Bank’s do_payment() and get_acc_balance() directly everywhere in the codebase. Business now wants to add HDFC Bank, whose
- `python-engineering/py-16/assignment/q05`: **(c)** What gets printed?
- `python-engineering/py-16/assignment/q10`: **(d)** # Version 1

## py-17-behavioural-patterns: Behavioural Design Patterns

- `python-engineering/py-17/additional/q04`: **(c)** When many unrelated parts of a system need to react to the same event, what problem shows up if that event source calls each one of them by 
- `python-engineering/py-17/additional/q05`: **(b)** class Discount:
- `python-engineering/py-17/additional/q06`: **(d)** class Shipper:
- `python-engineering/py-17/additional/q07`: **(a)** A music app wants to let users pick between three ways to sort their playlist: by song name, by artist, or by most recently added. Only one 
- `python-engineering/py-17/additional/q08`: **(b)** What is the key difference between choosing one way to do something and letting many things react to the same event?
- `python-engineering/py-17/additional/q09`: **(c)** What is printed, in order?
- `python-engineering/py-17/additional/q10`: **(d)** An online store wants three different systems — inventory, accounting, and marketing — to each react on their own whenever a sale happens, w
- `python-engineering/py-17/assignment/q04`: **(b)** What is the main idea behind having one shared interface with many classes that each do a task in their own way?
- `python-engineering/py-17/assignment/q05`: **(a)** class Shape:
- `python-engineering/py-17/assignment/q06`: **(c)** class Notifier:
- `python-engineering/py-17/assignment/q07`: **(d)** A photo editing app lets users choose between three ways to compress an image: high quality, balanced, or high compression. The user picks o
- `python-engineering/py-17/assignment/q08`: **(a)** Why is it usually a bad idea to check if type == "x" inside a class that's supposed to work with many different types generically?
- `python-engineering/py-17/assignment/q09`: **(c)** class Listener:
- `python-engineering/py-17/assignment/q10`: **(b)** A news app lets many different screens (Home screen, Widget, Push Notification service) know whenever a new headline is published. The app d

## py-18-uml-diagrams: UML Diagrams for Design Interviews

- `python-engineering/py-18/additional/q01`: **(a)** In a Class Diagram, what does a dashed line with a hollow triangle arrowhead represent?
- `python-engineering/py-18/additional/q02`: **(b)** One instructor teaches many courses, but each course has only one instructor. Where should the foreign key go?
- `python-engineering/py-18/additional/q03`: **(a)** A teammate wrote this schema for a blog, where one post can have many comments:
- `python-engineering/py-18/additional/q04`: **(b)** A Restaurant class has a List<MenuItem>. If the restaurant shuts down permanently, its menu items (like "Paneer Butter Masala") have no mean
- `python-engineering/py-18/additional/q05`: **(d)** In a Use Case Diagram, "Enroll in Course" always triggers "Make Payment" — there's no scenario where enrollment happens without it. What rel
- `python-engineering/py-18/additional/q06`: **(c)** Given this SQL:
- `python-engineering/py-18/additional/q07`: **(a)** A hospital has a Department class and a Doctor class. A doctor belongs to one department at a time, but if a department is dissolved, doctor
- `python-engineering/py-18/additional/q08`: **(b)** What is the main purpose of normalization in database schema design?
- `python-engineering/py-18/additional/q09`: **(d)** A ride-sharing app's Trip class has a List<RouteCoordinate> — the GPS points making up that specific trip's path. If the trip record is dele
- `python-engineering/py-18/assignment/q01`: **(d)** In a car manufacturing simulation, there's a class for generic vehicle properties. You have to create classes for a car, truck and motorcycl
- `python-engineering/py-18/assignment/q02`: **(d)** In a drawing application, there's a class for a generic shape called Shape . You have to create classes for Circle , Rectangle , and Triangl
- `python-engineering/py-18/assignment/q03`: **(d)** In a software application, there's a class called Animal with properties and methods common to all animals. You have to create classes for D
- `python-engineering/py-18/assignment/q04`: **(c)** In a library management system, there's a class for a library and a class for a book. What is the nature of the relationship between the lib **⚠ REVIEW:** Ambiguous: the stem gives no lifecycle detail. Association and composition are also defensible; aggregation chosen because books are normally independent objects in a library system.
- `python-engineering/py-18/assignment/q05`: **(c)** In a university system, there's a class for a department and a class for a professor. What is the nature of the relationship between the dep **⚠ REVIEW:** Ambiguous: stem gives no lifecycle detail; aggregation chosen because professors exist independently of a department (they can be reassigned). Association is also defensible.
- `python-engineering/py-18/assignment/q06`: **(a)** In a social media application, there's a class for a user and a class for a post. **⚠ REVIEW:** Ambiguous: no lifecycle detail in the stem. Association chosen as the least committal correct answer; aggregation is defensible, and the later user/post stem (q09) uses aggregation explicitly.
- `python-engineering/py-18/assignment/q07`: **(b)** Imagine a school enrollment system where a class represents a course. The course class contains objects representing enrolled students. Howe
- `python-engineering/py-18/assignment/q08`: **(b)** In a music streaming application, a class represents a playlist. The playlist class contains objects representing songs. If the playlist is 
- `python-engineering/py-18/assignment/q09`: **(b)** In a social media application, a class represents a user. The user class contains objects representing posts. If the user account is deleted
- `python-engineering/py-18/assignment/q10`: **(a)** In a car manufacturing simulation, a class represents a car. The car class contains objects representing the engine, wheels, and other parts
- `python-engineering/py-18/assignment/q11`: **(a)** In a drawing application, there is a Canvas class. The canvas class contains objects representing shapes such as circles, rectangles, and tr
- `python-engineering/py-18/assignment/q12`: **(a)** Imagine a class for a notebook. The notebook class contains objects representing pages. If the notebook object is destroyed, the pages are a
- `python-engineering/py-18/assignment/q13`: **(a)** What is the primary purpose of a PRIMARY KEY in a database table?
- `python-engineering/py-18/assignment/q14`: **(b)** A banking app allows joint accounts — one account can have multiple owners, and one person can be an owner on multiple accounts. How should 
- `python-engineering/py-18/assignment/q15`: **(b)** Given this schema and data:
- `python-engineering/py-18/assignment/q16`: **(d)** A teammate wrote this schema for an orders system:
- `python-engineering/py-18/assignment/q17`: **(a)** In a many-to-many junction table like enrollments, some teams skip a separate surrogate id column entirely and instead make the combination 

## py-24-code-parking-lot-2: Code Parking Lot 2: Payments, Fees and Concurrency

- `python-engineering/py-24/assignment/q03`: **(a)** In the Controller → Service → Repository pattern used in this lecture, which statement correctly describes where responsibilities live?
- `python-engineering/py-24/assignment/q04`: **(b)** Look at this code from the lecture: **⚠ REVIEW:** The lecture code appends to a list on every save (duplicates on update); the intended answer is unaffected but the snippet is questionable.
- `python-engineering/py-24/assignment/q05`: **(c)** Foo below is a plain class that does not inherit from BaseModel, so it has no `id`, `created_at`, or `last_modified_at` attributes.
- `python-engineering/py-24/assignment/q06`: **(d)** BillController and PaymentController were left as homework, not built live. According to the lecture, why is this considered “low-risk” home
- `python-engineering/py-24/assignment/q07`: **(a)** A teammate writes this TicketService method: **⚠ REVIEW:** Answer reflects the lecture's house rule (services never touch DTOs); some codebases consider DTO-accepting services acceptable.
- `python-engineering/py-24/assignment/q08`: **(b)** A customer pays ₹200 in cash and then ₹300 online for the same bill, recorded as two separate Payment objects. Given this line from **⚠ REVIEW:** The question text has garbled formatting in the source (a code fence containing both the method name and the sum line); content kept verbatim.
- `python-engineering/py-24/assignment/q09`: **(c)** Python’s GIL (Global Interpreter Lock) ensures only one thread executes Python bytecode at any given instant. Given this, why can two gate t
- `python-engineering/py-24/assignment/q10`: **(b)** class TicketService:
- `python-engineering/py-24/assignment/q11`: **(a)** In concurrency_test.py, exactly ONE ParkingSpot exists, and two separate Gate objects (Gate A and Gate B) both call issue_ticket() on the SA
- `python-engineering/py-24/assignment/q12`: **(b)** The AI-suggested fix uses one lock per VehicleType:

## py-26-code-bookmyshow-1: Code BookMyShow 1: SQLAlchemy Models and Relationships

- `python-engineering/py-26/assignment/q02`: **(a)** In SQLAlchemy, what does setting __abstract__ = True on a base class actually do?
- `python-engineering/py-26/assignment/q03`: **(b)** Two model classes, Screen and Seat, each declare a relationship() describing the connection between them, but neither uses back_populates. W
- `python-engineering/py-26/assignment/q04`: **(c)** A SeatType table stores rows like "GOLD" and "SILVER". Both Seat and ShowSeatType reference SeatType using a foreign key rather than storing
- `python-engineering/py-26/assignment/q05`: **(d)** Consider this code, where BaseModel gives every class an auto-incrementing integer id, and a table is created fresh (it didn't exist before)
- `python-engineering/py-26/assignment/q06`: **(a)** Given this enum and column definition:
- `python-engineering/py-26/assignment/q07`: **(b)** A team defines all their 12 model classes across multiple files, correctly using `Base` and `__tablename__`, but only imports 10 of them int
- `python-engineering/py-26/assignment/q08`: **(c)** Here is a class meant to represent a Region that has many Theatres:
- `python-engineering/py-26/assignment/q09`: **(d)** A junior developer writes the ShowSeat model like this, believing a simple foreign key back to Booking is enough to track which booking a se
- `python-engineering/py-26/assignment/q10`: **(a)** A Screen can physically support both 3D and Dolby Audio (this is stored as Screen.features). However, a specific 6 PM showing of a movie on 
- `python-engineering/py-26/assignment/q11`: **(b)** A repository layer needs a method to list every Show playing in a given region. The relationships are: Show belongs to a Screen, Screen belo

## py-27-code-bookmyshow-2: Code BookMyShow 2: Booking, Transactions and Race Conditions

- `python-engineering/py-27/assignment/q02`: **(b)** A team is building a backend using SQLAlchemy. They create a model called Order. In many SQL databases, ORDER is a reserved keyword (used in
- `python-engineering/py-27/assignment/q03`: **(c)** Two application threads run the following method at nearly the same time, targeting the exact same list of seats. No database-level locking 
- `python-engineering/py-27/assignment/q04`: **(a)** Under an isolation level called REPEATABLE READ (a common default in some relational databases), a transaction is guaranteed not to see chan **⚠ REVIEW:** Answer depends on the database: MySQL Repeatable Read lets T-B's UPDATE succeed after waiting (lost update), but PostgreSQL's Repeatable Read would abort T-B with a serialization error; (a) follows the lesson's MySQL framing.
- `python-engineering/py-27/assignment/q05`: **(d)** Which of the following best defines what SERIALIZABLE isolation guarantees in a relational database?
- `python-engineering/py-27/assignment/q06`: **(b)** Two transactions run under SERIALIZABLE isolation. Transaction 1 updates Row X. Transaction 2, running at the same time, updates a completel
- `python-engineering/py-27/assignment/q07`: **(a)** A backend application runs as multiple separate server processes (for example, behind a load balancer), all connecting to the same shared da
- `python-engineering/py-27/assignment/q08`: **(c)** A Controller class in a layered backend application accepts a dedicated request object (a DTO — Data Transfer Object) as its parameter, inst
- `python-engineering/py-27/assignment/q09`: **(d)** In an application using SQLAlchemy, an object seat was fetched earlier in a session (e.g., session.query(Seat).get(seat_id)). Later in the s
- `python-engineering/py-27/assignment/q10`: **(b)** A movie-ticket booking system has a business rule: the price of a seat depends on both which specific show it belongs to and its seat type —
- `python-engineering/py-27/assignment/q11`: **(c)** In a booking system, ticket prices are stored in a table keyed on the specific (show, seat_type) pair — meaning every individual show has it

## py-28-code-bookmyshow-3: Code BookMyShow 3: Users, Passwords and Expiry

- `python-engineering/py-28/assignment/q03`: **(a)** A booking system needs to release a seat that a user reserved but never paid for, after a fixed hold time. One design checks and resets expi
- `python-engineering/py-28/assignment/q04`: **(b)** A developer writes the following method to look up a user by email so that a signup flow can check whether an account already exists:
- `python-engineering/py-28/assignment/q05`: **(c)** A developer writes the following constructor for a service class that depends on a password-hashing helper:
- `python-engineering/py-28/assignment/q06`: **(d)** A password-hashing helper is used as follows, where encode() internally generates a fresh random salt on every call before hashing:
- `python-engineering/py-28/assignment/q07`: **(a)** A Booking model has automatic timestamp columns defined roughly as:
- `python-engineering/py-28/assignment/q08`: **(b)** A system stores user passwords by running them through a plain, deterministic hash function (one where the same input always produces the sa
- `python-engineering/py-28/assignment/q09`: **(c)** A password-hashing library provides two methods: encode(raw_password), which produces a new salted hash from a plain password, and matches(r
- `python-engineering/py-28/assignment/q10`: **(d)** A seat-booking system marks a seat as "held" the moment a user selects it, and treats a held seat as available again if more than 15 minutes
- `python-engineering/py-28/assignment/q11`: **(a)** A generated Service class for adding a new Theatre under a Region looks like this:
- `python-engineering/py-28/assignment/q12`: **(b)** An ORM lets you declare a timestamp column with both a default value and an onupdate value, roughly as Column(DateTime, default=some_functio

## py-30-code-splitwise-1: Code Splitwise 1: Commands, Models and Balances

- `python-engineering/py-30/assignment/q02`: **(b)** What does the following code print? **⚠ REVIEW:** The screenshot may have been cut off after the code block; answered assuming the code shown is complete.
- `python-engineering/py-30/assignment/q03`: **(c)** What does the following code print?
- `python-engineering/py-30/assignment/q04`: **(a)** Each row below is (user, kind, amount). A "PAID" row adds the amount to that user's balance, and a "HAD_TO_PAY" row subtracts it. What does 
- `python-engineering/py-30/assignment/q05`: **(d)** In an expense-sharing app, each row records one person's part in one expense. What does the code print?
- `python-engineering/py-30/assignment/q06`: **(a)** While reading a written requirement to find the classes of a system, you spot the nouns "user", "phone number" and "password". Which conclus
- `python-engineering/py-30/assignment/q07`: **(d)** An Expense must record how much each person paid and how much each person owes. Why is keeping this as a dictionary such as dict[User, int] 
- `python-engineering/py-30/assignment/q08`: **(b)** When should a fixed set of values, such as NORMAL and PAYMENT, be modeled as an enum instead of a separate lookup table?
- `python-engineering/py-30/assignment/q09`: **(c)** A developer names a database table order (or group). Which statement is most accurate?
- `python-engineering/py-30/assignment/q10`: **(c)** A developer writes the code below and expects ExpenseType to be a normal Python enum, but it does not behave like one. What is the cause and
- `python-engineering/py-30/assignment/q11`: **(a)** This shared base class is meant to provide common columns to other models, but SQLAlchemy raises an error saying the class has no __table__ 
- `python-engineering/py-30/assignment/q12`: **(d)** A CommandExecutor should print "Invalid command" only when no command matches the input. Instead, it prints "Invalid command" after every in
- `python-engineering/py-30/assignment/q13`: **(b)** A developer has model files (for example, models/user.py) that define tables. In main.py, they run the code below, but no tables are created
- `python-engineering/py-30/assignment/q14`: **(d)** In an online store, one order can contain several products, and for each product in an order we must record the quantity bought. Where shoul
- `python-engineering/py-30/assignment/q15`: **(c)** A group-expense app calculates balances from a table of expense records. When two people settle a debt, that payment must count in all futur
- `python-engineering/py-30/assignment/q16`: **(b)** A command-line app has a main() that passes every input line to a CommandExecutor. The executor holds a list of command objects, and each co
- `python-engineering/py-30/assignment/q17`: **(a)** You are building a small app that tracks shared expenses while it is running. Nothing needs to be kept after the app is closed. Which databa

## py-31-code-splitwise-2: Code Splitwise 2: Settle-Up Strategies

- `python-engineering/py-31/assignment/q02`: **(a)** In our Splitwise models, which enum belongs on the Expense model?
- `python-engineering/py-31/assignment/q03`: **(d)** A student writes this in BaseModel:
- `python-engineering/py-31/assignment/q04`: **(c)** What is the main job of back_populates on expense.expense_users and expense_user.expense?
- `python-engineering/py-31/assignment/q05`: **(b)** Riya is a member of the "Goa Trip" group and also of the "Roommates" group. Each group has many members. Which relationship fits Group.membe
- `python-engineering/py-31/assignment/q06`: **(a)** A teammate saves expense_type with Column(SAEnum(ExpenseType)). Later they rename PAYMENT to SETTLEMENT in the Python enum. Old rows in the 
- `python-engineering/py-31/assignment/q07`: **(c)** class SettleUpController:
- `python-engineering/py-31/assignment/q08`: **(d)** Why did we use a dummy Expense with expense_type = PAYMENT for a settlement, instead of creating a new Transaction class?
- `python-engineering/py-31/assignment/q09`: **(b)** Seed data for one expense (Dinner, total 1000):
- `python-engineering/py-31/assignment/q10`: **(c)** Net balances are A = -300, B = -200, C = +500. NaiveSettleUpStrategy sorts users from the lowest balance to the highest. Then it goes throug
- `python-engineering/py-31/assignment/q11`: **(a)** A student writes _build_dummy_expense like this:
- `python-engineering/py-31/assignment/q12`: **(b)** Aman is in five groups and also has some one-on-one expenses that have no group. In settle_up_user, how do we find every expense Aman is par
- `python-engineering/py-31/assignment/q13`: **(d)** settle_up_user runs the strategy on all expenses that user P is part of. The strategy returns 3 transactions:
- `python-engineering/py-31/assignment/q14`: **(a)** cmd = SettleUpUser(controller)
- `python-engineering/py-31/assignment/q15`: **(b)** class CommandExecutor:
- `python-engineering/py-31/assignment/q16`: **(c)** You finish a new HeapSettleUpStrategy class that follows the same SettleUpStrategy interface. You want the app to use it instead of NaiveSet
