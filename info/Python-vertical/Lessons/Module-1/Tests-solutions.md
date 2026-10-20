# Module 1 — Tests: Questions and Their Solution Zips

Each entry lists the lesson (taken from the header of the question screenshot), the question, and the solution zip that holds its answer. Zip files live in `info/Python-vertical/Lessons/Module-1/Tests/`. The folder name inside each zip identifies its problem. Where several zips show a generic `test-solution/` folder, the zip was matched by the code and README inside it.

Source: 28 unique questions, 32 screenshots. Four screenshots are second views of a question already listed (noted under each entry).

---

## Backend LLD: Concurrency-1: Processes, Threads and the GIL

### Q1. Multi-threaded Addition Program (Adder / Client)
- **Screenshot:** `msedge_YshYWlHFih.png`
- **Question:** Create an `Adder` class that inherits from `threading.Thread` and whose `run()` calculates and prints the sum of `num1` and `num2`. Create a `Client` class with a static `main()` that asks the user for two numbers, creates an `Adder`, starts it, and waits for it to finish.
- **Solution zip:** `1773391917_5c8abab669d1955b.zip` (folder `Adder_Python_LLD-solution`)

### Q1. Multithreaded Class Demonstration Challenge (Adder / Subtractor / Client)
- **Screenshot:** `msedge_QtXrXhH21V.png`
- **Question:** Create `Adder` and `Subtractor` classes, both inheriting from `threading.Thread`. `Adder.run()` prints `I am the Adder class` and `Subtractor.run()` prints `I am the Subtractor class`. Create a `Client` class with a static `main()` that prints `I am the main class`, starts one instance of each thread, and makes sure `main` waits for both to finish.
- **Solution zip:** `1773391943_4cc366d31e497bdd.zip` (folder `Threads_Python_L-solution`)

### Q2. Factorial Python LLD
- **Screenshot:** `msedge_14ci1COwum.png`
- **Question:** Create `FactorialThread(threading.Thread)` whose `__init__(n)` sets `result = None`, and whose `run()` computes `math.factorial(n)` and stores it in `result`. Write `compute_large_factorial(n)` that creates a `FactorialThread`, starts it, waits for it, and returns its result.
- **Solution zip:** `1773391936_de0e2e8ab31b2ee0.zip` (folder `Factorial_Python-solution`)

### Q3. Multithreaded Table Creator
- **Screenshot:** `msedge_XgwD3ybzIe.png`
- **Question:** Create `TableCreator(threading.Thread)` whose `__init__(num)` stores the number. Its `run()` prints the multiplication table from 1 to 10 in the format `<num> times <i> is <result>`. Several instances must run concurrently.
- **Solution zip:** `1773391939_f4fd50b7204e7e6b.zip` (folder `Table_Creator_Py-solution`)

---

## Backend LLD: Concurrency-2: Executors and Futures

### Q1. ImagePainter Python LLD (Parallel Matrix Painting)
- **Screenshot:** `msedge_33VEo77iJn.png`
- **Question:** Write `paint_quadrant`, which takes the matrix, start and end row indices, start and end column indices and a colour, and paints that quadrant. Write `divide_and_paint`, which takes the matrix and a list of colours, splits the matrix into four quadrants (top-left, top-right, bottom-left, bottom-right) and paints each one in parallel using `concurrent.futures.ThreadPoolExecutor`, waiting for all tasks. The example uses a 4x4 matrix and four colours.
- **Solution zip:** `1773391920_56eb6e7dca0510e5.zip` (folder `ImagePainter_Pyt-solution`)

---

## Backend LLD: Concurrency-3: Synchronization and Async Intro

### Q1. Foo Bar Python LLD (Foo Bar Printer Challenge)
- **Screenshot:** `msedge_EHBMC8RQ8h.png`
- **Question:** Create a class `FooBar(n)`, with methods `foo()` and `bar()` run by two separate threads. The threads must print `foo` and `bar` alternately so that `foobar` is printed `n` times, using synchronisation such as semaphores.
- **Solution zip:** `1773391944_bfe364a9709bba0f.zip` (folder `Foo_Bar_Python_L-solution`)

### Q1. Counter Python LLD (Concurrent Counter Management)
- **Screenshot:** `msedge_JIJTsvdIqs.png`
- **Question:** Implement `Counter` with `__init__(initial_count)`, `incValue(offset)`, `decValue(offset)` and `getValue()`. Implement `concurrent_inc()` and `concurrent_dec()`, which run several threads that update the counter. Print the final value after all threads finish.
- **Solution zip:** `1773391960_0f31f3df5fd71010.zip` (folder `Counter_Python_L-solution`)

### Q2. Print in Order Python LLD (Print in Order Challenge)
- **Screenshot:** `msedge_imrrSDvNHE.png`
- **Question:** Modify class `Foo` so that `first()`, `second()` and `third()` always print `first`, `second`, `third` in that order, whatever order they are called in. Initialise the semaphores in `__init__`. The `output` list must record the strings in execution order.
- **Solution zip:** `1773391949_73abaa349dfde86e.zip` (folder `Print_in_Order_P-solution`)

### Q2. Movie Ticket Booking
- **Screenshot:** `msedge_rn3SDOZmtD.png`
- **Question:** Implement `MovieTicketBookingSystem` for a single movie. It has `available_seats`, `total_seats` and a `ReentrantLock`. `reserve_seats(num_seats)` acquires the lock, reserves the seats if enough are free and returns `True`, otherwise returns `False`. `get_available_seats()` returns the current count. The system must prevent overbooking under concurrent requests.
- **Solution zip:** `1773391964_8fb66837d3b17de5.zip` (folder `Movie_Booking_Py-solution`)

### Q3. Printing Zeros Even Odd Python LLD (Zero Even Odd Challenge)
- **Screenshot:** `msedge_CiWBCTpG4e.png`
- **Question:** Implement `ZeroEvenOdd(n)` with three methods, `zero(printNumber)`, `even(printNumber)` and `odd(printNumber)`, each run by its own thread. The output must be `0102030405` for `n = 5`, with semaphores from `threading` controlling the order.
- **Solution zip:** `1773391951_a35508a06f41f7fc.zip` (folder `Printing_Zeros_E-solution`)

### Q3. Train reservation Python LLD (Train Reservation System, Assignment)
- **Screenshot:** `msedge_LWtDBiE2dL.png`
- **Question:** Implement `ReservationSystem` for Indian train seat types `1AC`, `2AC`, `3AC` and `Sleeper`. `available_seats` maps each seat type to a count, and a `lock` (ReentrantLock) guards it. `reserve_seats(seat_type, num_seats)` returns `True` and decrements the count if enough seats exist, otherwise `False`. `get_available_seats(seat_type)` returns the count for that type.
- **Solution zip:** `1773391966_1fa470fb2a1b0880.zip` (folder `Train_reservatio-solution`)

---

## Backend LLD: OOP-3: Inheritance, MRO and Polymorphism

### Q6. Fare Hierarchy with Overriding
- **Screenshot:** `msedge_4TYuqHACjQ.png`
- **Question:** Create a `Vehicle(reg_number)` base class with `is_available = True` and `calculate_fare(distance_km)` returning `10 × distance_km`. `Car(reg_number, seats)` overrides the fare to `15 × distance_km`. `Bike` overrides it to `7 × distance_km`. `Auto` is also a subclass of `Vehicle`. Use runtime polymorphism to compute fares for a mixed list in a single loop.
- **Solution zip:** `1783488806_0bd178fea4ba2479.zip` (folder `Fare_Hierarchy`)

### Q7. Cooperative Multiple Inheritance (Diamond)
- **Screenshots:** `msedge_NVX84Beq28.png` (question start) and `msedge_pix9ELYHdL.png` (second view, same question)
- **Question:** Model `ElectricCab(reg_number, battery_capacity, license_type)`, which inherits from `ElectricVehicle` and `CommercialVehicle`. Both inherit from `Vehicle(reg_number, **kwargs)`, and each calls `super().__init__(**kwargs)` cooperatively, so `Vehicle.__init__` runs once. `ElectricVehicle.get_priority_score()` returns 20 and `CommercialVehicle.get_priority_score()` returns 30. `ElectricCab(...).get_priority_score()` must return 20 because `ElectricVehicle` comes first in the MRO.
- **Solution zip:** `1783496519_a104dfda049cabd7.zip` (folder `Cooperative_Multiple`)

### Q8. Coverage Zones with Operator Overloading
- **Screenshots:** `msedge_AxMrqKJIlW.png` and `msedge_8JrujaJqyd.png` (same question, two views)
- **Question:** Implement `Zone(name)`, whose `area()` raises `NotImplementedError`. `CircularZone(name, radius)` returns `π × radius²`. `RectangularZone(name, width, height)` returns `width × height`. `TriangularZone(name, base, height)` returns `0.5 × base × height`. Overload `__eq__` (equal area), `__lt__` (smaller area, so `sorted(zones)` works) and `__add__` (returns a new `Zone` whose area is the sum of both operands).
- **Solution zip:** `1783499036_b2b5fea341aa5dab.zip` (folder `Coverage_Zones`)

### Q9. @singledispatch Fare Estimator
- **Screenshot:** `msedge_FuIRP7YlT1.png`
- **Question:** Implement `estimate_fare(x)` with `functools.singledispatch`. The base implementation raises `NotImplementedError`. The `float` implementation returns `15 × distance`. The `str` implementation looks up fixed routes: `HSR-AIRPORT` → 600 and `MG-AIRPORT` → 550, and returns 0 for unknown codes. The `Trip` implementation returns `15 × trip.distance_km`. `Trip(distance_km)` stores the distance in `distance_km`.
- **Solution zip:** `1783500852_eebc89443dddf37f.zip` (folder `Fare_Soln`)

### Q10. Uber Pricing Plugin System
- **Screenshots:** `msedge_IXTxXkrnvb.png` and `msedge_ucRCbkV2ZM.png` (same question, two views)
- **Question:** Build fare mixins that cooperate through `super().calculate_fare(distance)` along the MRO. `BaseFare` returns `10 × distance`. `SurgeMixin(multiplier)` returns `super() × multiplier`. `DiscountMixin(percent)` subtracts the percentage. `TaxMixin(rate)` adds the percentage. `FinalFare(TaxMixin, DiscountMixin, SurgeMixin, BaseFare)` takes `multiplier, percent, rate`. For distance 10, multiplier 2, percent 10 and rate 5, the expected fare is 189.
- **Solution zip:** `1783502541_598b1341a43b8d91.zip` (folder `Uber_Pricing`)

---

## Backend LLD: OOP-4: ABCs, Protocols and Mixins

### Q1. Notification ABC with Self-Registration
- **Screenshot:** `msedge_XAcpmyBkor.png`
- **Question:** Create an abstract base class `NotificationChannel` with abstract `send(user, message)` and `get_status(message_id)`, and a class-level `registry = {}`. Implement `__init_subclass__(channel_name=None)` so that a subclass with a `channel_name` registers itself as `registry[channel_name] = subclass`. Implement `SMSChannel`, `EmailChannel` and `PushChannel`, registered as `sms`, `email` and `push`.
- **Solution zip:** `1783661036_c175ae40f59fbcc5.zip` (contains `notification.py`; the folder is named `test-solution`)

### Q2. Protocol for Third-Party ETA Providers
- **Screenshot:** `msedge_cDEddu0CtP.png`
- **Question:** Define `ETAProvider` as a `typing.Protocol` with `@runtime_checkable` and `estimate_minutes(origin, destination) -> float`. `InternalETAProvider` (does not inherit `ETAProvider`) returns `abs(hash(origin) - hash(destination)) % 60`. `VendorMapETA` (also does not inherit it) always returns `42.0`. `get_eta(provider, origin, destination)` checks the protocol with `isinstance()`, raises `TypeError` if it fails, and otherwise returns the estimate.
- **Solution zip:** `1783664751_9a413a3bf87cdb44.zip` (contains `eta_protocol.py`, `eta_service.py`, `vendor_map.py`; the folder is named `test-solution`)

### Q3. Mixins + ABC + Registration (Payment Gateway Framework)
- **Screenshots:** `msedge_45y01j8pRO.png` and `msedge_GoTz43FQ4T.png` (same question, two views)
- **Question:** Build a payment gateway framework. `LoggingMixin.log_action(action)` prints `[LOG] ClassName: action`. `AuditMixin` keeps an `audit_trail` list and `record_audit(event)` appends to it. `Auditable` is a `typing.Protocol` with `@runtime_checkable` and `record_audit(event)`. `PaymentGateway` is an ABC with a class-level `registry = {}`, `__init_subclass__(gateway_name=None)`, and abstract `process_payment(amount)` and `refund(amount)`. `PhonePeGateway`, `RazorpayGateway` and `PaytmGateway` inherit from `PaymentGateway`, `LoggingMixin` and `AuditMixin`, register under `gateway_name`, and call `log_action` and `record_audit` in both methods. `run_audit_check(obj)` returns `isinstance(obj, Auditable)`.
- **Solution zip:** `1783665695_c534732dd49a265c.zip` (contains `audit_protocol.py`, `gateway.py`, `mixins.py`; the folder is named `test-solution`)

---

## Backend LLD: OOP Lab Session

### Q6. Library with Lending and Searching (lend_book / return_book)
- **Screenshot:** `msedge_I5EKQT8N5b.png`
- **Question:** Complete `Library` in `library.py` with `lend_book(member, book)` and `return_book(member, book)`. `lend_book` raises `TypeError` if the book is not `Borrowable`, `ValueError("Book not available")` if `book.is_available` is False, and `ValueError("Borrow limit reached")` if `member.can_borrow()` is False. On success it sets `book.is_available = False`, calls `member.increment_borrow()` and returns a `Loan`. `return_book` sets `book.is_available = True` and calls `member.decrement_borrow()`. Use the models in `models.py`.
- **Solution zip:** `1784097069_a99ba21ceff98847.zip` (contains `library.py`, `models.py`, `main.py`; the folder is named `test-solution`)

### Q7. Searchable Protocol and Non-Borrowable Magazine
- **Screenshot:** `msedge_B1QYn2bJxd.png`
- **Question:** Define `Searchable` as a `typing.Protocol` with `@runtime_checkable` and `matches(query: str) -> bool`. `Magazine(title, issue)` is searchable but must not inherit from `Borrowable`. Its `matches(query)` returns `True` if the query is contained in the title, case-insensitively. In `library.py`, `search(query)` returns items that satisfy `isinstance(item, Searchable)` and whose `matches(query)` is True. `lend(member, item)` raises `TypeError` if the item is not `Borrowable`, and otherwise marks it unavailable.
- **Solution zip:** `1784099004_b63b23ccf977d090.zip` (contains `library.py`, `magazine.py`, `protocols.py`; the folder is named `test-solution`)

### Q8. Full Integration: Mixin + Library (Book)
- **Screenshot:** `msedge_t1poC5eth9.png`
- **Question:** Implement `TimestampedMixin`, which sets `self.created_at = datetime.now()` in `__init__` and calls `super().__init__(*args, **kwargs)`. `Book(isbn, title)` inherits from `TimestampedMixin`, with `isbn` as a read-only property. Implement `__eq__` (compare by ISBN, return `NotImplemented` for non-books), `__hash__` (hash of ISBN) and `__repr__` (`Book('<isbn>', '<title>')`). In `library.py`, `Library` supports `add_book`, `__len__`, `__iter__`, `__contains__(isbn)` and `__getitem__`.
- **Solution zip:** `1784099919_feb714b65466943d.zip` (contains `library.py`, `models.py`, `main.py`; the folder is named `test-solution`)

---

## Backend LLD: Pythonic-1: Decorators, Iterators and Generators

### Q11. Retry Decorator
- **Screenshot:** `msedge_WJUBlj04DY.png`
- **Question:** Implement `retry(times, delay=0)` in `retry.py` as a decorator factory. Raise `ValueError("times must be a positive integer")` if `times` is not a positive integer, and `ValueError("delay must be non-negative")` if `delay` is negative. The decorated function is retried on exception, up to `times` total attempts, sleeping `delay` seconds between attempts with `time.sleep`. Return the first successful result. If all attempts fail, raise `RuntimeError(f"Function failed after {times} attempts")` with `raise ... from e`. Use `functools.wraps`.
- **Solution zip:** `1785155270_988a672755130026.zip` (contains `main/retry.py`, `tests/test_retry.py`; the folder is named `test-solution`)

### Q12. Lazy Sequences
- **Screenshot:** `msedge_yp4sn5YfP4.png`
- **Question:** Implement `NumberRange(start, end)` in `main/iterators.py`, inheriting from `LazySequence`, which yields `start` to `end - 1` lazily. Raise `TypeError` if either bound is not an integer, and `ValueError` if `start >= end`. Implement `even_numbers(limit)` in `main/generators.py` as a generator that yields every even number from 0 up to, but not including, `limit`. Raise `TypeError("limit must be an integer")` and `ValueError("limit must not be negative")` for bad input. Do not build a full list.
- **Solution zip:** `1785156527_fdf0f0af03f7043d.zip` (contains `main/generators.py`, `main/iterators.py`, `main/base.py`, `tests/test_lazy_sequences.py`; the folder is named `test-solution`)

---

## Backend LLD: Pythonic-2: Collections, Dataclasses, Type Hints and Exceptions

### Q1. compare Python LLD (Generic Comparison Function)
- **Screenshot:** `msedge_nB6WbZeB3v.png`
- **Question:** Implement `compare(x, y, key=None)`, which returns `-1` if `x < y`, `0` if equal and `1` if `x > y`. If `key` is given, compare `key(x)` with `key(y)`, otherwise compare the objects directly.
- **Solution zip:** `1773391927_eda44e3cff0f7ab5.zip` (folder `compare_Python_L-solution`)

### Q1. Frequency count Python LLD (Frequency Count, Assignment)
- **Screenshot:** `msedge_ojGTmu128e.png`
- **Question:** Implement the `count_frequency` method, which takes an array of integers and returns a dictionary with each element as a key and its frequency as the value. Do not print anything. Key order does not matter.
- **Solution zip:** `1773391973_d30546c67a6f1918.zip` (folder `Frequency_count_-solution`)

### Q2. Unique Person Python LLD (Unique Persons Finder Challenge)
- **Screenshot:** `msedge_LVNMnbhYsD.png`
- **Question:** Implement `find_unique_persons(persons)` for a list of predefined `Person(name, age)` objects. Return a new list that contains only the first occurrence of each name, in input order. Do not modify the `Person` class.
- **Solution zip:** `1773391957_c2074674faba3bfa.zip` (folder `Unique_Person_Py-solution`)

### Q2. Group Anagrams Python LLD (Group Anagrams)
- **Screenshot:** `msedge_tPGzpLj5SX.png`
- **Question:** Implement the `group_anagrams` function from the provided snippet. It takes an array of strings and returns a list of lists, where each inner list holds strings that are anagrams of each other. Return an empty list if the input is empty or `None`. Use a dictionary to group the anagrams.
- **Solution zip:** `1773391974_3512c742d4366886.zip` (folder `Group_Anagrams_P-solution`)

---

## Notes

- **Duplicate screenshots (no extra zip):** `msedge_8JrujaJqyd.png`, `msedge_pix9ELYHdL.png`, `msedge_ucRCbkV2ZM.png`, `msedge_GoTz43FQ4T.png`. Each is a second view of a question listed above.
- **Zip-to-question matching:** 8 zips in Module 1 have a generic `test-solution/` root folder, so they were matched by the files and README inside them. The other 20 are named after their problem.
- **Question wording:** The summaries are condensed from the screenshots. They are not a verbatim copy of the full statements.
