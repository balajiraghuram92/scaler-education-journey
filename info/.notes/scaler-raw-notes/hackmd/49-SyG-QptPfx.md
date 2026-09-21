Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/SyG-QptPfx

Post Read - Machine Coding - 6.2: Code Parking Lot 2
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Aug 24, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 6.2: Code Parking Lot 2
Introduction

Post-Read 6 finished the schema and wrote every model class for the Parking Lot system, but left TicketController holding its logic directly, with no Service layer behind it, and left the concurrency problem named but unsolved. This document finishes the system as a working MVP, not a fully polished product. It adds the missing Repository layer, builds a real Service layer for the first time (fixing TicketController along the way), finishes the remaining controllers, and solves the race condition named since Post-Read 5's design session: two gates, one spot.

Running example: the same multi-level Parking Lot system carried from Post-Reads 5 and 6, now reaching a genuinely runnable state.
Several things are deliberately simplified today to keep this an MVP; each simplification is named explicitly as it happens, and becomes homework rather than a silent gap.
The end-to-end walkthrough (Section 6) deliberately uses only one gate for simplicity, while the concurrency proof (Section 5) deliberately uses two real, separate gates, because that is literally the scenario being tested. These two choices serve two different purposes and are not inconsistent with each other.
This session contains six embedded animations, each narrated in full below at the point where the lecture places it.
Section 1: Quick Recap
What It Means
Finished in Post-Read 6: the full schema, and every model class (ParkingLot, Gate, ParkingSpot, Vehicle, Ticket, Bill, Payment, and all the enum/lookup classes).
Started but incomplete: TicketController, which had all its logic sitting directly inside it, with no Service behind it yet.
Still open going into this document: controllers for ParkingLot, Bill, Payment, a real Service layer, and the two-gates-one-spot race condition.
Done last class:
- Full schema
- Every model class, extending BaseModel
- TicketController — but with all its logic still INSIDE it,
  not yet moved into a Service (we'll fix this today)

Still open, going into today:
- A real Service layer (only ever named, never built)
- ParkingLotController, BillController, PaymentController
- The race condition flagged all the way back in the Design lecture

Before writing any code, several deliberate MVP simplifications are named upfront, so nothing gets quietly skipped:
MVP simplifications for TODAY (all named on purpose):

1. Status/type fields we said deserve a full lookup-table class
   (VehicleType, ParkingSpotStatus, BillStatus, PaymentStatus)
   stay as plain Java enums today.
   Why: we have no real database today — everything is
   in-memory. The lookup-table reasoning matters once you're
   persisting to a real DB. Today we just need correct, working
   code, fast.

2. We build ONE working version of each strategy (one fee
   strategy, one spot-assignment strategy), to prove the SHAPE
   works. We will NOT build a second version of each and swap
   between them live — that's real homework, not a silent cut.

3. Online payments will use a real PaymentGateway INTERFACE, but
   a fake/simulated implementation — not an actual third-party
   integration. That's expected and normal for an MVP.

4. For our main end-to-end WALKTHROUGH (Section 6), we skip
   Operator assignment and use just ONE floor and ONE gate, to
   keep that specific walkthrough simple.

   BUT — important — for the CONCURRENCY test (Section 5), we
   will use TWO separate gates on purpose. The entire problem
   we're solving IS "two gates, one spot." Testing it with only
   one gate wouldn't actually prove anything about that real
   scenario. So: simple demo = 1 gate. Concurrency proof = 2
   gates, because that's literally what we're testing.

Hidden Pitfalls
Treating "MVP" as a license for silent shortcuts: every simplification in this document is explicitly named and turned into homework; this discipline is what separates a legitimate MVP from a codebase quietly pretending to be complete.
Assuming the one-gate demo and the two-gate test contradict each other: they serve deliberately different purposes, proving the happy path works end to end versus proving a specific named race condition is actually fixed, and neither one substitutes for the other.
Section 2: The Repository Layer
What It Means

Before a real Service can be written, somewhere to actually store things is needed. Models exist, but nothing currently holds onto them anywhere.

Recalling the MVC lecture (Post-Read 2): Controller → Service → Repository. The Repository's one job: saving and fetching data. Nothing about business rules, just storage.
Since there's no real database today, the Repository just holds things in a List, in memory.
Several model types exist, Gate, ParkingSpot, Ticket, Bill. Should four almost-identical classes be written, each with their own save() and findById()? No, this is the same "same logic, different type" problem seen before. Generics can solve this with one shared class.
Practical Mechanics: InMemoryRepository
public class InMemoryRepository<T extends BaseModel> {
    private final List<T> items = new ArrayList<>();
    private long nextId = 1;

    public T save(T item) {
        if (item.getId() == null) {
            item.setId(nextId++);
            item.setCreatedAt(new Date());
        }
        item.setLastModifiedAt(new Date());
        items.add(item);
        return item;
    }

    public Optional<T> findById(Long id) {
        return items.stream()
                .filter(i -> i.getId().equals(id))
                .findFirst();
    }

    public List<T> findAll() {
        return new ArrayList<>(items);
    }
}

Why does T extends BaseModel matter here, what would break if it were removed? Without it, the repository wouldn't know that every T has an id, createdAt, and lastModifiedAt, so item.getId() and item.setId() wouldn't even compile. extends BaseModel guarantees every type this repository stores has those fields.

What the Animation Shows: Generic Type Bound Constraint, Bounded vs Unbounded

Two versions of the generic class sit side by side, one declared as InMemoryRepository<T> (unbounded) and one as InMemoryRepository<T extends BaseModel> (bounded).
On the unbounded side, an attempt to call item.getId() is shown failing, because as far as the compiler knows, T could be any Object, and plain Object has no getId() method.
On the bounded side, the same call to item.getId() succeeds, because the compiler now knows every T is guaranteed to have BaseModel's full API (getId(), setId(), getCreatedAt(), and so on).
A closing summary reinforces the core rule directly: without the bound, T is treated as plain Object; with the bound, the compiler guarantees T has BaseModel's methods, which is exactly why generic code can safely call them.
This makes concrete exactly why the compiler would reject item.getId() without extends BaseModel, not just as a rule to memorize, but as a visible before-and-after compiler behavior. It directly answers "what would break if we removed it," reinforcing that extends BaseModel isn't decoration, it's what makes the whole generic repository trick legal in the first place.
Answering the paired instructor question ("If we changed the bound to T extends Comparable instead, would item.getId() compile?"): no, it would not compile. Comparable only guarantees a compareTo() method exists; it says nothing about getId(), setId(), getCreatedAt(), or setCreatedAt(). The bound must specifically be (or extend) BaseModel, since that is the type that actually declares the fields and methods the repository needs to call.

Every specific repository becomes just one line:

public class GateRepository extends InMemoryRepository<Gate> {}
public class ParkingSpotRepository extends InMemoryRepository<ParkingSpot> {}
public class TicketRepository extends InMemoryRepository<Ticket> {}
public class BillRepository extends InMemoryRepository<Bill> {}

Hidden Pitfalls
Writing a separate repository class per model with duplicated save/findById logic: this repeats the exact "same logic, different type" problem generics exist to solve, and multiplies maintenance effort every time a bug fix or new method is needed across all repositories.
Removing or weakening the extends BaseModel bound to make the generic "more flexible": this silently breaks the ability to call getId(), setId(), or the timestamp methods inside InMemoryRepository, since the compiler can no longer guarantee those methods exist on an unconstrained type parameter.
Section 3: The Service Layer, Coded for Real
What It Means
Recalling Post-Read 6's AI Corner, TicketController was fixed to look like this:
public class TicketController {
    public IssueTicketResponseDTO issueTicket(IssueTicketRequestDTO request) {
        Gate gate = fetchGate(request.getGateId());

        if (gate.getGateType() == GateType.EXIT) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }

        Ticket ticket = buildTicket(request, gate);
        return toResponseDTO(ticket);
    }
}

At the time, this wasn't questioned further. But fetchGate() and buildTicket() are private methods sitting directly inside the Controller. Given what's now known about layering, where should this logic actually live? fetchGate() is a storage lookup, that's the Repository's job. buildTicket() contains real business logic, checking the gate type, finding a spot, creating the ticket, that's the Service's job. The Controller should just translate the DTO into a Service call, and translate the result back into a DTO. Nothing else. This is the exact gap being closed here: TicketController has been "incomplete" since Post-Read 6, and is fixed properly now.
Controller  → talks to whoever is calling the system.
              Converts DTO ↔ model. No business logic here.

Service     → the actual brain. Validation, decisions,
              coordinating repositories, applying strategies.

Repository  → pure storage. Save, find. Nothing else.

Practical Mechanics: Building TicketService
What issueTicket actually needs to do, step by step: fetch the gate, check it's an ENTRY gate; build a Vehicle from the request; use the allotment strategy to find a matching spot; mark that spot occupied; build and save the Ticket.
public class TicketService {
    private final GateRepository gateRepository;
    private final ParkingSpotRepository parkingSpotRepository;
    private final TicketRepository ticketRepository;
    private final AllotmentStrategy allotmentStrategy;

    public TicketService(GateRepository gateRepository,
                          ParkingSpotRepository parkingSpotRepository,
                          TicketRepository ticketRepository,
                          AllotmentStrategy allotmentStrategy) {
        this.gateRepository = gateRepository;
        this.parkingSpotRepository = parkingSpotRepository;
        this.ticketRepository = ticketRepository;
        this.allotmentStrategy = allotmentStrategy;
    }

    public Ticket issueTicket(IssueTicketRequestDTO request) {
        Gate gate = gateRepository.findById(request.getGateId())
                .orElseThrow(() -> new IllegalArgumentException("Gate not found"));

        if (gate.getGateType() != GateType.ENTRY) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }

        Vehicle vehicle = new Vehicle();
        vehicle.setNumber(request.getVehicleNumber());
        vehicle.setVehicleType(request.getVehicleType());
        vehicle.setOwnerName(request.getOwnerName());

        ParkingSpot assignedSpot = allotmentStrategy.findSpot(
                parkingSpotRepository.findAll(), request.getVehicleType());

        if (assignedSpot == null) {
            throw new ParkingFullException("No available spot for this vehicle type");
        }

        assignedSpot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);
        parkingSpotRepository.save(assignedSpot);

        Ticket ticket = new Ticket();
        ticket.setNumber(UUID.randomUUID().toString());
        ticket.setEntryTime(new Date());
        ticket.setVehicle(vehicle);
        ticket.setAssignedSpot(assignedSpot);
        ticket.setGeneratedAt(gate);

        return ticketRepository.save(ticket);
    }
}

AllotmentStrategy and two small exceptions are needed for this to compile:

public interface AllotmentStrategy {
    ParkingSpot findSpot(List<ParkingSpot> spots, VehicleType vehicleType);
}

public class NearestSpotStrategy implements AllotmentStrategy {
    @Override
    public ParkingSpot findSpot(List<ParkingSpot> spots, VehicleType vehicleType) {
        for (ParkingSpot spot : spots) {
            if (spot.getParkingSpotStatus() == ParkingSpotStatus.EMPTY
                    && spot.getSupportedVehicleTypes().contains(vehicleType)) {
                return spot;
            }
        }
        return null;
    }
}

public class ParkingFullException extends RuntimeException {
    public ParkingFullException(String message) { super(message); }
}

public class InvalidGateException extends RuntimeException {
    public InvalidGateException(String message) { super(message); }
}

NearestSpotStrategy checks spot.getSupportedVehicleTypes().contains(vehicleType). Why does this one line directly depend on the spot-size decision made in Post-Read 6? Because supportedVehicleTypes is a list, not one fixed type, a TRUCK spot's list includes CAR and BIKE too. So this single line of matching logic correctly handles a bike getting a truck spot, without any extra code. Good design earns simple code later; that's not an accident.
An honest note: R8 from Post-Read 5 said spot assignment should be configurable, auto-pick, or let the user choose. Only NearestSpotStrategy (the auto-pick version) is built here. The AllotmentStrategy interface is genuinely swappable, but a second version isn't built and swapped live today. That's real homework, not something pretended to be done.
Practical Mechanics: Fixing TicketController for Real
public class TicketController {
    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    public IssueTicketResponseDTO issueTicket(IssueTicketRequestDTO request) {
        Ticket ticket = ticketService.issueTicket(request);

        IssueTicketResponseDTO response = new IssueTicketResponseDTO();
        response.setTicketId(ticket.getId());
        response.setTicketNumber(ticket.getNumber());
        response.setEntryTime(ticket.getEntryTime());
        response.setAssignedSpotId(ticket.getAssignedSpot().getId());
        return response;
    }
}

Comparing this to Post-Read 6's version, what actually moved, and what's left? All the real logic, fetching the gate, checking gate type, finding a spot, building the ticket, moved into TicketService. What's left in the Controller is just: call the Service, then convert the result into a DTO. Nothing else. This is the same "constructor injection" idea, the Controller receives its Service through the constructor, instead of creating logic itself or building a new Service on every call.
One field is added to IssueTicketResponseDTO, since the ticket's actual ID is needed later to generate a bill:
public class IssueTicketResponseDTO {
    private Long ticketId;        // <-- added today
    private String ticketNumber;
    private Date entryTime;
    private Long assignedSpotId;  // simplified for the MVP
    // getters and setters
}

Practical Mechanics: BillService
What does generating a bill actually need to do? Fetch the ticket, calculate the fee using the fee strategy, and save a new Bill.
public interface FeeCalculationStrategy {
    int calculateFee(Ticket ticket, Date exitTime);
}

public class HourlyRateStrategy implements FeeCalculationStrategy {
    private static final int RATE_PER_HOUR = 20;

    @Override
    public int calculateFee(Ticket ticket, Date exitTime) {
        long millisParked = exitTime.getTime() - ticket.getEntryTime().getTime();
        long hoursParked = (long) Math.ceil(millisParked / (1000.0 * 60 * 60));
        hoursParked = Math.max(hoursParked, 1);
        return (int) (hoursParked * RATE_PER_HOUR);
    }
}

public class BillService {
    private final TicketRepository ticketRepository;
    private final BillRepository billRepository;
    private final FeeCalculationStrategy feeCalculationStrategy;

    public BillService(TicketRepository ticketRepository,
                        BillRepository billRepository,
                        FeeCalculationStrategy feeCalculationStrategy) {
        this.ticketRepository = ticketRepository;
        this.billRepository = billRepository;
        this.feeCalculationStrategy = feeCalculationStrategy;
    }

    public Bill generateBill(Long ticketId) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new IllegalArgumentException("Ticket not found"));

        int amount = feeCalculationStrategy.calculateFee(ticket, new Date());

        Bill bill = new Bill();
        bill.setTicket(ticket);
        bill.setExitTime(new Date());
        bill.setAmount(amount);
        bill.setBillStatus(BillStatus.UNPAID);
        bill.setPayments(new ArrayList<>());

        return billRepository.save(bill);
    }
}

A minimum of 1 hour is charged, even for a 5-minute stay. Is that a bug? No, that's a real, common pricing rule in actual parking lots. It's a deliberate business decision, not a mistake.
Same honest note as before: R5 said fee calculation should be dynamic and swappable. FeeCalculationStrategy genuinely IS swappable, since BillService only depends on the interface. Only HourlyRateStrategy is built today; a second strategy, and actually proving the swap live, is homework.
Practical Mechanics: PaymentService and a Real Gateway Interface
Recalling R6 from Post-Read 5: online payments go through a third-party gateway. If "Redirecting to gateway..." were just printed directly inside PaymentService, what problem does that repeat, from Post-Read 6's very first AI Corner? That was the exact "no real abstraction, just a print statement" mistake caught there. A real interface should exist, even if the actual implementation is fake for now.
public interface PaymentGateway {
    boolean processOnlinePayment(int amount, String referenceNumber);
}

public class FakePaymentGateway implements PaymentGateway {
    @Override
    public boolean processOnlinePayment(int amount, String referenceNumber) {
        // MVP note: this is a stand-in for a real third-party
        // gateway call. A real version would make an actual
        // network call here.
        System.out.println("Simulating online payment of " + amount
                + " with reference " + referenceNumber);
        return true;
    }
}

Recalling R4: once a bill is fully paid, the spot must be freed. Where does that logic belong? Inside PaymentService, right after a payment fully covers the bill.
public class PaymentService {
    private final BillRepository billRepository;
    private final ParkingSpotRepository parkingSpotRepository;
    private final PaymentGateway paymentGateway;

    public PaymentService(BillRepository billRepository,
                           ParkingSpotRepository parkingSpotRepository,
                           PaymentGateway paymentGateway) {
        this.billRepository = billRepository;
        this.parkingSpotRepository = parkingSpotRepository;
        this.paymentGateway = paymentGateway;
    }

    public Payment makePayment(MakePaymentRequestDTO request) {
        Bill bill = billRepository.findById(request.getBillId())
                .orElseThrow(() -> new IllegalArgumentException("Bill not found"));

        Payment payment = new Payment();
        payment.setPaymentMode(request.getMode());
        payment.setAmount(request.getAmount());
        payment.setTime(new Date());

        if (request.getMode() == PaymentMode.ONLINE) {
            String referenceNumber = UUID.randomUUID().toString();
            boolean success = paymentGateway.processOnlinePayment(request.getAmount(), referenceNumber);
            payment.setReferenceNumber(referenceNumber);
            payment.setPaymentStatus(success ? PaymentStatus.SUCCESS : PaymentStatus.FAILED);
        } else {
            payment.setPaymentStatus(PaymentStatus.SUCCESS);
        }

        bill.getPayments().add(payment);

        int totalPaid = bill.getPayments().stream()
                .filter(p -> p.getPaymentStatus() == PaymentStatus.SUCCESS)
                .mapToInt(Payment::getAmount)
                .sum();

        if (totalPaid >= bill.getAmount()) {
            bill.setBillStatus(BillStatus.PAID);
            ParkingSpot spot = bill.getTicket().getAssignedSpot();
            spot.setParkingSpotStatus(ParkingSpotStatus.EMPTY);
            parkingSpotRepository.save(spot);
        }

        billRepository.save(bill);
        return payment;
    }
}

Only payments where paymentStatus == SUCCESS are summed, not every payment ever attempted. Why does that matter? A failed online payment shouldn't count toward the total paid, otherwise someone could "pay" with a failed transaction and still get the spot freed.
totalPaid >= bill.getAmount() sums across the whole payments list, instead of just this one payment. Why does it have to be a sum? Because of partial payments from Post-Read 5, someone might pay 200 cash and 300 online, as two separate Payment records. Only the total tells whether the bill is fully paid. That decision from the design session finally pays off in real code.
Hidden Pitfalls
Leaving business logic (gate checks, spot finding, ticket building) directly inside the Controller: this was precisely the incomplete state TicketController was left in at the end of Post-Read 6; the fix demonstrated here is exactly what moving that logic into a proper Service accomplishes.
Summing every payment attempted, including failed ones, toward the total paid: this would allow a failed online payment to incorrectly count toward freeing the spot, a real correctness bug hiding in what looks like simple arithmetic.
Checking only the most recent payment against the bill amount instead of the running total: given that partial payments were an explicit design decision in Post-Read 5, checking only the latest payment would break the bill-is-fully-paid logic the moment more than one payment record exists for a bill.
Skipping the PaymentGateway interface and printing directly inside PaymentService: this repeats the exact abstraction-skipping mistake identified in Post-Read 6's first AI Corner, and would make it much harder to later swap in a real third-party integration without touching PaymentService itself.
Section 4: Finishing the Other Controllers
What It Means

BillController, PaymentController, and ParkingLotController follow the exact same shape just fixed in TicketController: DTO in, call the Service, DTO out.

Practical Mechanics: Bill Request/Response DTOs and Controller
public class GenerateBillRequestDTO {
    private Long ticketId;
    // getters and setters
}

public class GenerateBillResponseDTO {
    private Long billId;
    private int amount;
    private String status;
    // getters and setters
}

public class BillController {
    private final BillService billService;

    public BillController(BillService billService) {
        this.billService = billService;
    }

    public GenerateBillResponseDTO generateBill(GenerateBillRequestDTO request) {
        Bill bill = billService.generateBill(request.getTicketId());

        GenerateBillResponseDTO response = new GenerateBillResponseDTO();
        response.setBillId(bill.getId());
        response.setAmount(bill.getAmount());
        response.setStatus(bill.getBillStatus().toString());
        return response;
    }
}

Practical Mechanics: Payment Request/Response DTOs and Controller
public class MakePaymentRequestDTO {
    private Long billId;
    private PaymentMode mode;
    private int amount;
    // getters and setters
}

public class MakePaymentResponseDTO {
    private String paymentStatus;
    // getters and setters
}

public class PaymentController {
    private final PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    public MakePaymentResponseDTO makePayment(MakePaymentRequestDTO request) {
        Payment payment = paymentService.makePayment(request);

        MakePaymentResponseDTO response = new MakePaymentResponseDTO();
        response.setPaymentStatus(payment.getPaymentStatus().toString());
        return response;
    }
}

Practical Mechanics: ParkingLot, a Simple, Real Read Use Case
What's something a real client of this system, say, a mobile app showing "spots available," would actually want to ask? How many spots are currently free for a given vehicle type.
public class AvailableSpotCountRequestDTO {
    private VehicleType vehicleType;
    // getters and setters
}

public class AvailableSpotCountResponseDTO {
    private int availableCount;
    // getters and setters
}

public class ParkingLotService {
    private final ParkingSpotRepository parkingSpotRepository;

    public ParkingLotService(ParkingSpotRepository parkingSpotRepository) {
        this.parkingSpotRepository = parkingSpotRepository;
    }

    public int getAvailableSpotCount(VehicleType vehicleType) {
        return (int) parkingSpotRepository.findAll().stream()
                .filter(spot -> spot.getParkingSpotStatus() == ParkingSpotStatus.EMPTY)
                .filter(spot -> spot.getSupportedVehicleTypes().contains(vehicleType))
                .count();
    }
}

public class ParkingLotController {
    private final ParkingLotService parkingLotService;

    public ParkingLotController(ParkingLotService parkingLotService) {
        this.parkingLotService = parkingLotService;
    }

    public AvailableSpotCountResponseDTO getAvailableSpotCount(AvailableSpotCountRequestDTO request) {
        int count = parkingLotService.getAvailableSpotCount(request.getVehicleType());

        AvailableSpotCountResponseDTO response = new AvailableSpotCountResponseDTO();
        response.setAvailableCount(count);
        return response;
    }
}

Quiz Recap

TicketService.issueTicket() has the gate-type check (if (gate.getGateType() != GateType.ENTRY)). A teammate suggests moving this check into TicketController instead, saying "it's a simple check, no harm keeping it near the entry point." What's the strongest reason to keep it in the Service?

A) Controllers are not allowed to contain if statements in Java
B) If another Controller (say, a future admin tool) also needs to issue tickets, it would have to duplicate this exact validation, keeping it in Service means every caller gets the same guaranteed rule, automatically (correct)
C) Moving it would cause a compile error, since GateType is only visible inside Service classes
D) It doesn't matter, Controller and Service are interchangeable as long as the check exists somewhere
Correct answer: B. This is the actual reason Service exists as its own layer: business rules need to be enforced consistently no matter which Controller, or which future caller, ends up invoking them. If validation lived in the Controller, every new entry point would need to remember to repeat it, a real, common source of bugs in larger systems.
Why A is wrong: this is factually false; Java places no such restriction on Controllers, and the reasoning for the layering choice is architectural, not a language rule.
Why C is wrong: GateType is a regular enum with no access restriction tying it to Service classes specifically; it would compile fine referenced from a Controller too. The reason to avoid this isn't a compile error, it's the duplication risk.
Why D is wrong: this ignores the entire point of layered architecture; Controller and Service have distinct responsibilities, and treating them as interchangeable defeats the consistency guarantee that placing business rules in the Service provides.
Hidden Pitfalls
Duplicating a validation rule across multiple Controllers instead of keeping it in one Service: every additional entry point that needs the same rule becomes another place that rule could be forgotten or implemented slightly differently, exactly the risk the Service layer is meant to eliminate.
Treating ParkingLotController's read-only use case as needing less DTO discipline than the write use cases: even a simple count-lookup benefits from the same Request/Response DTO pattern, keeping the contract explicit and stable regardless of how ParkingSpot might change internally later.
Section 5: The Concurrency Problem
What It Means
The exact problem named since Post-Read 5's design AI Corner: two different entry gates could both try to assign the same empty spot to two different vehicles, at almost the same moment.
Why this actually happens, in simple terms: many requests can arrive and get handled at the same time, not one after another. Each request usually runs on its own thread. If two threads both read shared data, then both write to it, without any coordination, their actions can overlap in a way that breaks correctness.
Thread A (Gate 1)                Thread B (Gate 2)
------------------                ------------------
1. Look at all spots
                                   2. Look at all spots
                                      (sees the SAME empty spot A saw)
3. Sees Spot #7 is EMPTY
                                   4. Also sees Spot #7 is EMPTY
5. Marks Spot #7 OCCUPIED
                                   6. Also marks Spot #7 OCCUPIED

Result: TWO tickets both point to Spot #7. One real spot,
two vehicles told it's theirs. Notice: this is TWO DIFFERENT
GATES, not one gate handling two requests — that's the exact
scenario we're about to test for real.

What the Animation Shows: Two-Gate Race Condition Timeline

Spot #7 starts out EMPTY, with two lanes on screen representing Thread A (Gate 1) and Thread B (Gate 2), both about to run the same tryPark(7) function.

Thread A reads Spot #7 and sees EMPTY, storing that in its own local variable, nothing in shared memory has changed yet.

Before Thread A writes anything, Thread B also reads Spot #7 and also sees EMPTY, highlighted as the dangerous "interleaving gap," where both threads now believe the spot is free.

Thread A then writes OCCUPIED to Spot #7, believing it succeeded, then Thread B also writes OCCUPIED to the same spot, overwriting Thread A's work without knowing it happened.

A final "COLLISION" frame shows both threads believing they successfully parked in the same physical spot, with the root cause spelled out: Thread B read before Thread A wrote, so both saw EMPTY at the same time.

This turns the board diagram's abstract "Thread A / Thread B" steps into a literal, line-by-line interleaving that can be watched happening, making the exact danger window (read-read-write-write) impossible to miss. It sets up the motivation for the synchronized fix precisely, by showing why simply "checking if it's empty" isn't safe without some form of coordination between threads.

Answering the paired instructor question ("At which exact step in this animation would a lock have needed to already be held, to prevent this outcome?"): a lock would have needed to already be held by Thread A starting from the very first read (step 1, "Thread A reads Spot #7 and sees EMPTY"), and would need to remain held all the way through Thread A's write. If Thread B attempted to acquire the same lock during that window, it would be forced to wait until Thread A released it, at which point Thread B's own read would correctly see OCCUPIED instead of EMPTY, preventing the collision entirely.

Looking at the current TicketService.issueTicket(), which exact lines are the dangerous ones, the ones where this clash can actually happen?

ParkingSpot assignedSpot = allotmentStrategy.findSpot(...);    // READ
...
assignedSpot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);  // WRITE
parkingSpotRepository.save(assignedSpot);

The gap between reading "is this spot empty?" and writing "mark it occupied" is exactly where two threads can slip in. This is called a critical section, a piece of code that must never be entered by two threads at the same time.

Given that two threads must be stopped from being inside that section at once, what's the simplest tool Java gives for this? The synchronized keyword, it lets only one thread execute a block of code at a time; any other thread has to wait its turn.
A real design choice: Option 1, mark the entire issueTicket() method synchronized. Option 2, only wrap the small critical section, the find-spot-and-mark-it part, in a synchronized block. What's the difference in cost? Option 1 locks the whole method, including building the Vehicle, generating the ticket number, everything, even though most of that doesn't need protecting. Every gate waits in line for the entire process. Option 2 only blocks other threads during the tiny risky part, so gates wait less overall. Smaller critical sections mean less unnecessary waiting.

What the Animation Shows: Synchronized Critical Section Protection

Two threads both call parkVehicle(), with only the assign-and-save portion marked as synchronized, everything else runs freely.
Both threads validate at the same time and both read from the database concurrently, with no locking at all needed for those steps.
Thread 1 enters the synchronized(spotLock) block first, Thread 2 is blocked, but only for this narrow section, since it already finished its validation and DB read beforehand.
Thread 1 saves its spot and exits the lock, immediately followed by Thread 2 entering the critical section right after.
A final summary counts total time units used, showing that three separate phases (validation, DB read, and post-work) ran in parallel rather than serially, for a real measured speedup.
This gives a concrete, watchable answer to "what's the difference in cost" between locking the whole method versus a narrow block, showing exactly which phases overlap and which don't. It reinforces that the goal of narrowing a synchronized block isn't just style, it's letting independent, safe work (validation, reads) run in parallel instead of queueing unnecessarily.
Answering the paired instructor question ("Which specific lines of our issueTicket() code correspond to the green 'lock-free' segments in this animation?"): the lock-free segments correspond to the gate lookup and validation (gateRepository.findById(...) and the GateType check), the Vehicle object construction, and, after the lock is released, the Ticket construction and ticketRepository.save(ticket) call. Only the portion between finding a candidate spot and marking it OCCUPIED sits inside the synchronized block.
Practical Mechanics: The First Locking Fix
public class TicketService {
    private final GateRepository gateRepository;
    private final ParkingSpotRepository parkingSpotRepository;
    private final TicketRepository ticketRepository;
    private final AllotmentStrategy allotmentStrategy;
    private final Object spotLock = new Object();

    public TicketService(GateRepository gateRepository,
                          ParkingSpotRepository parkingSpotRepository,
                          TicketRepository ticketRepository,
                          AllotmentStrategy allotmentStrategy) {
        this.gateRepository = gateRepository;
        this.parkingSpotRepository = parkingSpotRepository;
        this.ticketRepository = ticketRepository;
        this.allotmentStrategy = allotmentStrategy;
    }

    public Ticket issueTicket(IssueTicketRequestDTO request) {
        Gate gate = gateRepository.findById(request.getGateId())
                .orElseThrow(() -> new IllegalArgumentException("Gate not found"));

        if (gate.getGateType() != GateType.ENTRY) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }

        Vehicle vehicle = new Vehicle();
        vehicle.setNumber(request.getVehicleNumber());
        vehicle.setVehicleType(request.getVehicleType());
        vehicle.setOwnerName(request.getOwnerName());

        ParkingSpot assignedSpot;
        synchronized (spotLock) {
            assignedSpot = allotmentStrategy.findSpot(
                    parkingSpotRepository.findAll(), request.getVehicleType());

            if (assignedSpot == null) {
                throw new ParkingFullException("No available spot for this vehicle type");
            }

            assignedSpot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);
            parkingSpotRepository.save(assignedSpot);
        }

        Ticket ticket = new Ticket();
        ticket.setNumber(UUID.randomUUID().toString());
        ticket.setEntryTime(new Date());
        ticket.setVehicle(vehicle);
        ticket.setAssignedSpot(assignedSpot);
        ticket.setGeneratedAt(gate);

        return ticketRepository.save(ticket);
    }
}

private final Object spotLock = new Object(); is used as a dedicated lock, instead of just writing synchronized on the whole method. Why bother with a separate object just to lock on? Because only the spot-finding section should be locked, not the whole method; synchronized(spotLock) { ... } marks exactly which lines are protected.
spotLock is one single object, shared across the whole TicketService. If Gate A and Gate B both call issueTicket() on the SAME TicketService instance, does it matter that they're different Gate objects, for this lock to actually work? No, the lock doesn't care which gate is calling. As long as both requests go through the same TicketService instance, they'll both hit the same spotLock, and only one can be inside the critical section at a time, no matter which gate they came from. That's actually the whole point. This lock protects the shared spot data, regardless of how many different gates are trying to reach it.

What the Animation Shows: Synchronized Block Scope vs Whole-Method Lock

Six concurrent threads are queued up to request parking spots, run twice, once with the whole method marked synchronized, once with only the narrow critical section locked.
In the whole-method version, each new thread has to wait for the entire 3-unit method (validation plus DB lookup plus save plus response) to finish before it can even start; Thread 4 alone racks up 9 idle units, Thread 6 waits 15 units and finishes at t=18.
In the block-scope version, every thread's pre-work and post-work run in parallel (shown as overlapping green segments), and each thread only queues for the 1-unit critical section itself; Thread 6 finishes at t=8.
A running comparison of total wait time is shown building up thread by thread, side by side, so the gap between the two approaches gets visibly wider as more threads join.
The final frame states the result directly: block scope finishes all 6 threads at t=8 versus t=18 for whole-method, a 2.25x throughput improvement.
This makes the "gates wait less overall" claim into an actual measured number (2.25x faster), scaled up to something closer to a real multi-gate lot instead of just two threads. It reinforces that lock contention grows with the size of the critical section, not just its existence, a key intuition for the AI Corner's optimization discussion later.
Answering the paired instructor question ("If we had 20 gates instead of 6, would the gap between these two approaches get bigger or smaller, and why?"): the gap would get bigger. In the whole-method approach, each additional gate adds another full method's worth of waiting time to the queue, so total wait time grows roughly proportional to the square of the number of gates (each new gate waits for all prior gates' full methods). In the block-scope approach, each additional gate only adds its small critical-section wait time, so total wait time grows much more slowly. The more gates involved, the more the narrow-lock approach's advantage compounds.
Practical Mechanics: Proving the Fix with Two Real Gates

Rather than just trusting the fix, a test recreates the real scenario: two separate gates, racing for the same one spot, exactly the problem named in Post-Read 5.

public class ConcurrencyTest {
    public static void main(String[] args) throws InterruptedException {
        ParkingSpotRepository spotRepo = new ParkingSpotRepository();
        ParkingSpot spot = new ParkingSpot();
        spot.setParkingSpotStatus(ParkingSpotStatus.EMPTY);
        spot.setSupportedVehicleTypes(List.of(VehicleType.CAR));
        spotRepo.save(spot);   // only ONE spot exists

        GateRepository gateRepo = new GateRepository();

        // TWO separate, real entry gates — this is the actual
        // scenario we're testing: Gate A and Gate B, not one
        // gate handling two requests.
        Gate entryGateA = new Gate();
        entryGateA.setGateType(GateType.ENTRY);
        gateRepo.save(entryGateA);

        Gate entryGateB = new Gate();
        entryGateB.setGateType(GateType.ENTRY);
        gateRepo.save(entryGateB);

        TicketRepository ticketRepo = new TicketRepository();

        // Both gates share the SAME TicketService instance —
        // just like in a real system, both gates talk to the
        // same backend, which holds the same spotLock.
        TicketService ticketService = new TicketService(
                gateRepo, spotRepo, ticketRepo, new NearestSpotStrategy());

        Runnable tryFromGateA = () -> {
            try {
                IssueTicketRequestDTO request = new IssueTicketRequestDTO();
                request.setGateId(entryGateA.getId());
                request.setVehicleType(VehicleType.CAR);
                request.setVehicleNumber("CAR-FROM-GATE-A");

                Ticket ticket = ticketService.issueTicket(request);
                System.out.println("Gate A got spot: " + ticket.getAssignedSpot().getId());
            } catch (ParkingFullException e) {
                System.out.println("Gate A found lot full");
            }
        };

        Runnable tryFromGateB = () -> {
            try {
                IssueTicketRequestDTO request = new IssueTicketRequestDTO();
                request.setGateId(entryGateB.getId());
                request.setVehicleType(VehicleType.CAR);
                request.setVehicleNumber("CAR-FROM-GATE-B");

                Ticket ticket = ticketService.issueTicket(request);
                System.out.println("Gate B got spot: " + ticket.getAssignedSpot().getId());
            } catch (ParkingFullException e) {
                System.out.println("Gate B found lot full");
            }
        };

        Thread threadForGateA = new Thread(tryFromGateA, "Gate-A-Thread");
        Thread threadForGateB = new Thread(tryFromGateB, "Gate-B-Thread");

        threadForGateA.start();
        threadForGateB.start();
        threadForGateA.join();
        threadForGateB.join();
    }
}

Running this a few times, with only ONE spot, and two genuinely different gates racing for it: one gate should always print "got spot." The other should always print "found lot full." Never both succeeding, no matter how many times it's run.
Why does this test map onto the real problem more honestly than a version using just one Gate object with two threads? Because the actual scenario discussed since Post-Read 5 is specifically "two different gates," using two real Gate objects, each with their own ID, proves the fix works for the exact situation promised to be solved, not just "two requests happened at once" in the abstract. When a test is written for a specific named problem, it should match that problem as closely as possible, not just something loosely similar.
Without the synchronized block, what would this test occasionally print instead? Both Gate A and Gate B printing "got spot" for the same spot ID, the exact bug being fixed, now made visible with the real scenario.
Quiz Recap

A teammate "fixes" the race condition like this — they add synchronized, but on the method itself, using a NEW lock object created fresh every time, instead of the shared spotLock field:

public Ticket issueTicket(IssueTicketRequestDTO request) {
    Object lock = new Object();   // <-- created fresh, every single call
    synchronized (lock) {
        ParkingSpot assignedSpot = allotmentStrategy.findSpot(
                parkingSpotRepository.findAll(), request.getVehicleType());
        assignedSpot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);
        parkingSpotRepository.save(assignedSpot);
    }
    // ... build and save ticket ...
}

Given our two-gate ConcurrencyTest, does this actually fix the race condition?

A) Yes, synchronized always prevents two threads from running the same block at the same time, regardless of what object is passed in
B) No, Gate A and Gate B each get their OWN separate lock object, since new Object() runs fresh on every call. Locking on two different objects provides no protection at all, it's the same as not synchronizing (correct)
C) Yes, but only for the first two calls, after that, Java reuses old lock objects automatically
D) No, this code won't even compile, since synchronized requires a static final object
Correct answer: B. synchronized(lock) only stops other threads trying to acquire the same lock object from entering at the same time. If Gate A's thread creates its own lock, and Gate B's thread creates a completely different lock, they're not actually blocking each other at all, both can enter their "critical section" simultaneously, and the exact same race condition happens. This is why spotLock in the real code is a single private final field, created once, shared by every call, so every thread checking the same lock actually has to wait its turn. Writing synchronized correctly requires locking on something truly shared, not just adding the keyword anywhere.
Why A is wrong: this misunderstands how Java's synchronized mechanism works; it doesn't prevent all concurrent execution universally, it only prevents concurrent execution by threads contending for the same specific object's monitor.
Why C is wrong: Java does not reuse or track "old" lock objects in any special way; each new Object() call creates a genuinely distinct, unrelated object every single time, with no special behavior after the first two calls.
Why D is wrong: this is factually false; synchronized can lock on any object reference, it does not require the lock to be static or final. The bug here is a logical one (using a fresh, non-shared lock), not a compilation restriction.
Hidden Pitfalls
Creating a fresh lock object inside the method being protected: as the quiz demonstrates, this produces code that looks correct and compiles fine, but provides zero actual protection, since no two calls ever contend for the same lock object.
Locking the entire method instead of just the critical section: this works correctly but unnecessarily serializes unrelated work (gate lookup, vehicle construction, ticket building), directly costing throughput as demonstrated in the Synchronized Block Scope animation.
Testing a concurrency fix with only one thread, or with two threads simulating the same gate: this doesn't actually validate the specific named scenario ("two gates, one spot"); the test needs to recreate the real scenario as closely as possible to be a meaningful proof.
Section 6: Wiring It All Into a Working Demo
What It Means

The entire system is now proven end to end, a car enters, gets billed, pays, and the spot frees up. For this walkthrough, one gate is enough, since the two-gate race condition was already proven separately in Section 5.

Practical Mechanics: The Full Demo
public class Main {
    public static void main(String[] args) {

        // 1. Repositories
        GateRepository gateRepository = new GateRepository();
        ParkingSpotRepository spotRepository = new ParkingSpotRepository();
        TicketRepository ticketRepository = new TicketRepository();
        BillRepository billRepository = new BillRepository();

        // 2. A simple lot: one entry gate, one CAR/BIKE spot
        Gate entryGate = new Gate();
        entryGate.setGateType(GateType.ENTRY);
        gateRepository.save(entryGate);

        ParkingSpot carSpot = new ParkingSpot();
        carSpot.setParkingSpotStatus(ParkingSpotStatus.EMPTY);
        carSpot.setSupportedVehicleTypes(List.of(VehicleType.CAR, VehicleType.BIKE));
        spotRepository.save(carSpot);

        // 3. Services
        TicketService ticketService = new TicketService(
                gateRepository, spotRepository, ticketRepository, new NearestSpotStrategy());
        BillService billService = new BillService(
                ticketRepository, billRepository, new HourlyRateStrategy());
        PaymentService paymentService = new PaymentService(
                billRepository, spotRepository, new FakePaymentGateway());

        // 4. Controllers
        TicketController ticketController = new TicketController(ticketService);
        BillController billController = new BillController(billService);
        PaymentController paymentController = new PaymentController(paymentService);

        // 5. A car enters
        IssueTicketRequestDTO ticketRequest = new IssueTicketRequestDTO();
        ticketRequest.setGateId(entryGate.getId());
        ticketRequest.setVehicleType(VehicleType.CAR);
        ticketRequest.setVehicleNumber("KA-01-1234");
        ticketRequest.setOwnerName("Sasi");

        IssueTicketResponseDTO ticketResponse = ticketController.issueTicket(ticketRequest);
        System.out.println("Ticket issued: " + ticketResponse.getTicketNumber());

        // 6. The car leaves — generate the bill
        GenerateBillRequestDTO billRequest = new GenerateBillRequestDTO();
        billRequest.setTicketId(ticketResponse.getTicketId());
        GenerateBillResponseDTO billResponse = billController.generateBill(billRequest);
        System.out.println("Bill generated: amount = " + billResponse.getAmount());

        // 7. Pay the bill — let's use ONLINE, to exercise the gateway
        MakePaymentRequestDTO paymentRequest = new MakePaymentRequestDTO();
        paymentRequest.setBillId(billResponse.getBillId());
        paymentRequest.setMode(PaymentMode.ONLINE);
        paymentRequest.setAmount(billResponse.getAmount());

        MakePaymentResponseDTO paymentResponse = paymentController.makePayment(paymentRequest);
        System.out.println("Payment status: " + paymentResponse.getPaymentStatus());

        // 8. Confirm the spot is free again
        System.out.println("Spot status now: " + carSpot.getParkingSpotStatus());
    }
}

Tracing the last line of output: why should carSpot.getParkingSpotStatus() print EMPTY, not OCCUPIED, by the time this line runs? Because PaymentService.makePayment() checked that the full amount was paid successfully, and freed the spot as part of that same operation, this is R4 from Post-Read 5, finally visible end to end.
Hidden Pitfalls
Assuming this single-gate walkthrough also proves the concurrency fix: it does not; this demo only exercises the sequential happy path and deliberately does not test what happens when two requests compete for the same resource at the same time. The concurrency proof lives specifically in Section 5's ConcurrencyTest.
Missing that the spot's freed status is observed on the original carSpot reference: this works correctly here because ParkingSpotRepository stores and returns the same object reference in this in-memory implementation; this detail would need re-examining if the repository were backed by a real database returning fresh copies on each read.
Section 7: AI Corner, a Real, Unfinished Optimization
What It Means

This isn't a planted mistake. The synchronized (spotLock) fix from Section 5 is correct, but genuinely leaves performance on the table, a real, honest gap in the working code, the same spirit as TicTacToe's Hard bot (Post-Read 4).

The current fix uses ONE shared spotLock for every single ticket request, no matter the vehicle type, no matter which gate. If five gates are all issuing BIKE tickets, and one gate is issuing a TRUCK ticket, at the same moment, do the bike requests actually need to wait for the truck request, or for each other? Not really, a bike request and a truck request are looking at (mostly) different spots. Forcing all of them through one single lock means unnecessary waiting, even when there's no real conflict. This is a real, unfinished optimization.
Practical Mechanics: The AI-Suggested Fix, and Why It's Unsafe

Prompt used:

"In my Java parking lot system, TicketService currently uses one
single shared lock object (`spotLock`) to protect spot assignment
from race conditions, across ALL vehicle types and ALL gates.
This means two requests for completely different vehicle types
(say, BIKE and TRUCK) still block each other unnecessarily.

Here's the current method: [paste issueTicket() from Section 5]

Can you suggest a way to make the locking more fine-grained, so
requests for different vehicle types don't block each other,
while still fully preventing two threads from ever being assigned
the exact same ParkingSpot object? Keep the same method signature
and exceptions."

A plausible AI response:

private final ConcurrentHashMap<VehicleType, Object> locksByVehicleType =
        new ConcurrentHashMap<>();

private Object getLockFor(VehicleType type) {
    return locksByVehicleType.computeIfAbsent(type, t -> new Object());
}

public Ticket issueTicket(IssueTicketRequestDTO request) {
    // ... gate check, vehicle build, same as before ...

    ParkingSpot assignedSpot;
    synchronized (getLockFor(request.getVehicleType())) {
        assignedSpot = allotmentStrategy.findSpot(
                parkingSpotRepository.findAll(), request.getVehicleType());

        if (assignedSpot == null) {
            throw new ParkingFullException("No available spot for this vehicle type");
        }

        assignedSpot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);
        parkingSpotRepository.save(assignedSpot);
    }

    // ... build and save ticket, same as before ...
}

Before accepting this, it is checked using the same checklist established earlier in this module:

1. Does it match the interface/contract? — Yes, same signature,
   same exceptions.
2. Does it follow our conventions? — Yes, still uses
   AllotmentStrategy, ParkingFullException, same style.
3. Does it handle edge cases?
4. Does it actually perform correctly for OUR real constraints?

The real test, point 4: recalling the spot-size rule (Post-Read 6), a TRUCK spot's supportedVehicleTypes list includes TRUCK, CAR, and BIKE. Imagine Gate A is issuing a CAR ticket, and Gate B, at the exact same moment, is issuing a TRUCK ticket. With this new fix, do these two gates use the same lock, or different locks? Different locks, Gate A locks on VehicleType.CAR, Gate B locks on VehicleType.TRUCK. They're not blocked from running at the same time.
Could both gates legally end up looking at, and choosing, the exact same physical TRUCK-sized spot, since that one spot supports both CAR and TRUCK? Yes. Since they hold different locks, nothing stops them from running the "find spot" step at the same time, and both finding that same TRUCK spot as EMPTY, since neither one is blocking the other.
This is exactly the bug. AI's fix is faster, but it silently reintroduces the original race condition, between two DIFFERENT gates, using DIFFERENT vehicle types, specifically for any spot that supports more than one vehicle type, which, because of Post-Read 6's spot-size design, is most of the lot. This is exactly why AI's output always needs to be checked against real constraints, not just whether the code looks clean.

What the Animation Shows: Per-VehicleType Lock Fails on Overlapping Spot Support

Spot #3 starts EMPTY, and its supported types are shown as [TRUCK, CAR, BIKE], two separate lock objects exist on screen, one for CAR and one for TRUCK.
Gate A calls assignSpot(gateA, CAR) and acquires locks[CAR], the animation notes this lock only knows about CAR-type assignments, nothing about TRUCK.
Gate B calls assignSpot(gateB, TRUCK) and acquires locks[TRUCK], a visibly different lock object, both threads are now shown running concurrently, with no blocking between them.
Gate A reads Spot #3 as EMPTY and prepares to assign it; Gate B then also reads Spot #3 as still EMPTY, since neither gate's lock has any effect on the other.
Both gates proceed to write OCCUPIED to Spot #3, Gate A first, then Gate B overwrites it, ending with a flagged "DOUBLE ASSIGN" state where both gates believe they own the same physical spot.
This makes the AI's bug fully concrete and traceable, step by step, rather than just conceptually understood, watching the exact moment where two different locks fail to protect one shared resource. It directly visualizes the answer to "could both gates end up choosing the exact same spot," confirming yes, and showing precisely why: the locks guard the wrong thing (vehicle type) instead of the actual shared resource (the spot itself).
Answering the paired instructor question ("Looking at this exact animation, what's the minimum change to getLockFor() that would have prevented this specific collision?"): the minimum change would be to key the lock by the specific ParkingSpot being examined, rather than by VehicleType. Instead of getLockFor(VehicleType type), locking would need to happen on the actual spot object itself (synchronized(spot)), so that any two threads contending for that specific spot, regardless of what vehicle type they requested, would correctly block each other.
Practical Mechanics: The Correct Fix, Locking Per Spot

A correct fine-grained fix needs to lock per physical spot, not per requested vehicle type, since it's the spot being shared, not the type. Combining everything worked through: locking on the actual ParkingSpot object itself, re-checking status inside the lock, and falling through to the next candidate if a spot was already taken.

public class TicketService {
    private final GateRepository gateRepository;
    private final ParkingSpotRepository parkingSpotRepository;
    private final TicketRepository ticketRepository;
    private final AllotmentStrategy allotmentStrategy;

    public TicketService(GateRepository gateRepository,
                          ParkingSpotRepository parkingSpotRepository,
                          TicketRepository ticketRepository,
                          AllotmentStrategy allotmentStrategy) {
        this.gateRepository = gateRepository;
        this.parkingSpotRepository = parkingSpotRepository;
        this.ticketRepository = ticketRepository;
        this.allotmentStrategy = allotmentStrategy;
    }

    public Ticket issueTicket(IssueTicketRequestDTO request) {
        Gate gate = gateRepository.findById(request.getGateId())
                .orElseThrow(() -> new IllegalArgumentException("Gate not found"));

        if (gate.getGateType() != GateType.ENTRY) {
            throw new InvalidGateException("Cannot issue a ticket at an exit gate");
        }

        Vehicle vehicle = new Vehicle();
        vehicle.setNumber(request.getVehicleNumber());
        vehicle.setVehicleType(request.getVehicleType());
        vehicle.setOwnerName(request.getOwnerName());

        // This is the only part that needed protecting.
        // Everything above and below this line is safe to run
        // without any locking at all.
        ParkingSpot assignedSpot = claimAnySpotFor(request.getVehicleType());

        if (assignedSpot == null) {
            throw new ParkingFullException("No available spot for this vehicle type");
        }

        Ticket ticket = new Ticket();
        ticket.setNumber(UUID.randomUUID().toString());
        ticket.setEntryTime(new Date());
        ticket.setVehicle(vehicle);
        ticket.setAssignedSpot(assignedSpot);
        ticket.setGeneratedAt(gate);

        return ticketRepository.save(ticket);
    }

    /**
     * Finds an empty spot matching the given vehicle type, and
     * safely claims it — even if multiple gates call this at the
     * exact same moment.
     */
    private ParkingSpot claimAnySpotFor(VehicleType vehicleType) {
        // Step 1: read candidate spots. No lock needed here —
        // we're only reading, not claiming anything yet. This
        // list might already be slightly stale by the time we
        // act on it, which is exactly why Step 2 re-checks.
        List<ParkingSpot> candidates = parkingSpotRepository.findAll().stream()
                .filter(spot -> spot.getSupportedVehicleTypes().contains(vehicleType))
                .collect(Collectors.toList());

        for (ParkingSpot spot : candidates) {
            // Step 2: lock on THIS specific spot object. Two
            // threads only block each other here if they're
            // both trying to claim this exact same spot.
            synchronized (spot) {
                // Step 3: re-check status AFTER acquiring the
                // lock. Someone else may have claimed this exact
                // spot between our read in Step 1 and getting
                // here. This re-check is what closes that gap.
                if (spot.getParkingSpotStatus() == ParkingSpotStatus.EMPTY) {
                    spot.setParkingSpotStatus(ParkingSpotStatus.OCCUPIED);
                    parkingSpotRepository.save(spot);
                    return spot;
                }
            }
            // This spot was already taken by someone else.
            // Don't give up — just try the next candidate.
        }

        // Genuinely nothing available for this vehicle type.
        return null;
    }
}

What the Animation Shows: Per-Spot Lock with Re-Check Pattern

Two side-by-side panels run the same scenario in parallel, Spot A starts EMPTY, and both Thread 1 and Thread 2 read the candidate list without any lock, both seeing Spot A as EMPTY (a stale snapshot, taken before any locking happens).
Thread 1 enters synchronized(spot) first and acquires the lock on Spot A; Thread 2 tries to lock the same spot and must wait.
Both panels initially behave identically, Thread 1 checks status, sees EMPTY, and assigns the spot, then releases the lock.
The key moment: Thread 2 now acquires the lock. In the LEFT panel (no re-check), Thread 2 trusts its old Step 1 read of EMPTY and assigns the spot again, a duplicate assignment. In the RIGHT panel (with re-check), Thread 2 re-reads the actual current status inside the lock, sees OCCUPIED, and correctly skips the spot.
A final result frame contrasts the two outcomes directly: left panel ends with both threads owning Spot A (a bug), right panel ends with only Thread 1 owning it (correct).
This makes the purpose of the Step 3 re-check in claimAnySpotFor() completely unmissable, directly answering "why re-check status again, we already checked it in Step 1." It shows precisely why a stale read taken before acquiring a lock is dangerous, and why the check that actually matters is the one taken after the lock is held.
Answering the paired instructor question ("Point to the exact line in our real Java code that corresponds to the right panel's 're-check' step, and explain why removing that one line would silently bring back this bug."): the corresponding line is if (spot.getParkingSpotStatus() == ParkingSpotStatus.EMPTY) inside the synchronized(spot) block. Removing this check (and unconditionally marking the spot OCCUPIED after acquiring the lock) would silently bring back the bug demonstrated in the left panel: a second thread could acquire the lock after the first thread already claimed the spot, and, without re-checking, would proceed to "claim" an already-occupied spot, producing the same double-assignment collision this whole section was built to eliminate.
Quiz Recap

Given the bug we just found, which locking strategy would actually be safe for our system, where one physical spot can support multiple vehicle types?

A) Lock per requested VehicleType, exactly as AI suggested, it's fast and simple
B) Lock per individual ParkingSpot object being examined or assigned, since that's the actual shared resource two gates could collide on (correct)
C) No lock at all, since spots are stored in a List, Java's list already prevents concurrent modification safely
D) A single global lock across the entire system, same as our original fix, since fine-grained locking is never worth the complexity
Correct answer: B. The actual shared resource being fought over is the specific ParkingSpot, not the requested vehicle type or which gate is asking. Locking by vehicle type, as AI suggested, only works safely if spots never overlap in what they support, which isn't true here, because of the spot-size design from Post-Read 6.
Why A is wrong: this is exactly the bug just demonstrated; locking by vehicle type fails precisely because a single spot can be a valid candidate for multiple vehicle types simultaneously.
Why C is wrong: Java's List implementations (like ArrayList, used inside InMemoryRepository) provide no built-in thread safety for concurrent reads and writes; this is a factually incorrect assumption about how Java collections behave.
Why D isn't wrong exactly, but gives up all the performance benefit: a single global lock, the original Section 5 fix, is genuinely safe and was the correct starting point, but it forces every gate through one lock regardless of vehicle type, exactly the unnecessary waiting the fine-grained optimization in this section set out to eliminate.
Hidden Pitfalls
Accepting an AI-suggested optimization based on interface compatibility and code style alone: the AI's per-vehicle-type locking fix passed checks 1 through 3 (interface match, conventions, general edge-case handling) cleanly, and still contained a serious correctness bug only surfaced by checking against point 4, the system's specific real constraints.
Locking on a value (like an enum) rather than the actual shared resource: the core lesson of this section is that a lock must protect the thing that's actually contended over; locking on VehicleType protects nothing, since multiple distinct ParkingSpot objects can share the same VehicleType, and multiple VehicleTypes can point at the same ParkingSpot.
Skipping the re-check-after-lock step: reading a value before acquiring a lock, and trusting that value after the lock is acquired, without re-reading it, reintroduces exactly the kind of staleness bug the entire per-spot locking pattern is designed to close.
Wrap-Up: Tying It Together
Built today — a working Parking Lot MVP:
- InMemoryRepository<T> — one generic class, storing everything
- Real Service layer — TicketService, BillService,
  PaymentService, ParkingLotService — holding all the business
  logic that used to sit inside Controllers
- Fixed TicketController — properly using TicketService, instead
  of holding logic directly (a real gap from last class, now closed)
- BillController, PaymentController, ParkingLotController — all
  finished, same DTO discipline throughout
- A real (fake, but properly abstracted) PaymentGateway interface
- The race condition, finally solved:
  - Found the exact critical section (read spot, write spot)
  - Chose a small, targeted synchronized block over locking the
    whole method
  - Proved it with a test using TWO REAL, SEPARATE gates — the
    exact scenario named all the way back in the Design lecture,
    not just "two requests" in the abstract
- A full working demo: car enters → gets a spot → gets billed →
  pays online → spot frees up again (closing the loop on R4)

Every idea in this document, Repository, Service, the lock, even the AI Corner bug, traces back to a decision made in an earlier lecture. Nothing here was random; it was all connected. The most important habit demonstrated here: race conditions don't announce themselves. They hide inside code that looks perfectly fine. The only way to catch them is to deliberately ask "what if two things happen at exactly the same time here?" every single time shared data is touched.

When testing a specific named problem, like "two gates, one spot," the test needs to actually recreate that exact scenario, not just something loosely similar. That distinction is exactly what the two real Gate objects in the concurrency test practiced. Naming what's NOT done, clearly, out loud, is just as much a skill as writing the code that IS done.

Honest gaps, named clearly (all homework):

1. R5 (dynamic fee calculation) — only HourlyRateStrategy exists.
   We proved the INTERFACE is swappable, but never built a
   second strategy or swapped it live.

2. R8 (configurable spot assignment) — only NearestSpotStrategy
   exists. UserChoiceStrategy, from our own class diagram, was
   never built.

3. Our end-to-end WALKTHROUGH (Section 6) used only one gate for
   simplicity — but the CONCURRENCY test (Section 5) correctly
   used two real gates, since that's the actual scenario being
   proven. These served two different purposes on purpose.

4. Enums stayed as plain Java enums today (VehicleType,
   ParkingSpotStatus, BillStatus, PaymentStatus), not the full
   lookup-table classes from Lecture 6's schema.

5. The AI Corner's fine-grained locking fix was found to be
   UNSAFE for our system — a correct per-spot lock still needs
   to be built.

None of these are secretly broken. They're clearly-named,
reasonable cuts for an MVP under time pressure — exactly the
same honesty we practiced with TicTacToe's Medium bot.

The next document in this series moves to a brand-new problem: designing BookMyShow, where an even trickier version of this same "two people, one resource" problem gets encountered, seat locking during a live booking.

Common Pitfalls Summary
1. Writing a separate repository class per model with duplicated
   save/findById logic.
   -> Repeats the "same logic, different type" problem; generics
      with a bounded type parameter solve this with one class.

2. Removing or weakening the `extends BaseModel` bound on a
   generic repository.
   -> Silently breaks the ability to call getId()/setId() and
      timestamp methods, since the compiler can no longer
      guarantee those methods exist.

3. Leaving business logic directly inside a Controller instead of
   a Service.
   -> Was exactly the incomplete state TicketController was left
      in; moving logic to Service is what actually fixes it.

4. Summing every payment attempted (including failed ones) toward
   a bill's total paid amount.
   -> Allows a failed online payment to incorrectly count toward
      freeing the spot.

5. Checking only the most recent payment against the bill amount
   instead of the running total across all payments.
   -> Breaks partial payments, since a bill can be settled across
      more than one payment record.

6. Skipping a PaymentGateway interface and printing directly
   inside PaymentService.
   -> Repeats the abstraction-skipping mistake already caught in
      an earlier AI Corner.

7. Duplicating a validation rule (like the gate-type check) across
   multiple Controllers instead of keeping it in one Service.
   -> Creates multiple places the same rule could be forgotten or
      implemented inconsistently.

8. Creating a fresh lock object inside the very method being
   protected by synchronized.
   -> Produces code that compiles and looks correct but provides
      zero actual protection, since no two calls share the lock.

9. Locking the entire method instead of just the critical section.
   -> Works correctly but unnecessarily serializes unrelated work,
      directly costing throughput.

10. Testing a concurrency fix with only one thread, or with two
    threads simulating the same gate.
    -> Doesn't actually validate the specific named scenario;
       the test must recreate the real scenario closely.

11. Locking on a value like VehicleType instead of the actual
    shared resource (the specific ParkingSpot).
    -> Fails the moment two different requested types can both
       be satisfied by the same physical spot.

12. Skipping the re-check-after-lock step in a per-resource
    locking pattern.
    -> Reintroduces staleness bugs, since a value read before
       acquiring a lock can no longer be trusted after acquiring it.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Assuming an AI-suggested performance optimization is safe simply because it passes interface and style checks: the fine-grained locking bug in Section 7 passed three of the four checklist points cleanly and still contained a serious correctness bug; only checking against the system's specific real constraints (the spot-size overlap from Post-Read 6) surfaced the actual problem.
Treating "we proved the interface is swappable" as equivalent to "we proved the swap works": both FeeCalculationStrategy and AllotmentStrategy are genuinely swappable by design, but this document is explicit that only one implementation of each was actually built and exercised; the swap itself remains unverified until a second implementation exists and is tested.
Key Terminology
Term	Meaning in Simple Words
Critical Section	A piece of code that reads and then writes shared data in a way that breaks correctness if two threads execute it at the same time; it must never be entered by more than one thread simultaneously.
synchronized (Java keyword)	A Java keyword that ensures only one thread can execute a given block of code (or hold a given lock) at a time; any other thread attempting to enter must wait.
Race Condition	A bug that occurs when the correctness of a program depends on the unpredictable timing or interleaving of multiple threads, such as two threads both reading a value as "empty" before either has written to it.
Lock Object	An object used purely as a synchronization point; threads that synchronized on the same lock object are forced to take turns, while threads locking on different objects do not block each other at all.
Stale Read	A value read from shared data that may no longer be accurate by the time it's acted upon, because another thread modified the underlying data in between the read and the action.
Fine-Grained Locking	A locking strategy that protects the smallest possible unit of shared data (such as one specific object) rather than locking broadly across an entire resource or method, aiming to allow more concurrent work to proceed safely.

Generics, DTOs, the Repository/Service/Controller layering, the Strategy pattern, and the boolean-versus-enum discipline were already defined in Post-Read 1 through Post-Read 6 and are not redefined here.

Frequently Asked Interview Questions

1. Why does InMemoryRepository<T extends BaseModel> need the extends BaseModel bound, and what would happen without it?
The bound guarantees the compiler that any type T used with this class has the fields and methods declared on BaseModel (getId(), setId(), getCreatedAt(), setCreatedAt(), setLastModifiedAt()). Without the bound, T would be treated as an unconstrained type (effectively Object), and calls like item.getId() inside the repository's methods would fail to compile, since the compiler cannot assume a plain Object has a getId() method.

2. Explain the layering responsibility split between Controller, Service, and Repository, using TicketController's original flaw as an example.
Controller should translate an incoming request (DTO) into a Service call, and translate the Service's result back into a response DTO, with no business logic of its own. Service holds the actual business logic: validation, decision-making, and coordinating repositories and strategies. Repository handles pure storage: saving and finding data, with no business rules. TicketController's original flaw was having fetchGate() (a storage concern that belongs in the Repository) and buildTicket() (a business logic concern that belongs in the Service) both implemented as private methods directly inside the Controller, collapsing all three layers into one class.

3. Why does PaymentService sum only payments with PaymentStatus.SUCCESS when checking whether a bill is fully paid?
If every payment attempt were summed regardless of status, a failed online payment (one where the third-party gateway declined or errored) would still count toward the total paid amount. This could result in a bill being incorrectly marked as paid, and the associated parking spot being freed, even though the customer never actually completed a successful payment covering that amount.

4. Why must the total-paid check sum across the entire list of payments on a bill, rather than checking just the most recent payment?
Because of the partial-payment design decision made when Bill was modeled to hold a List<Payment> (rather than a single Payment), a single bill can be settled across multiple separate payment records, for example, part cash and part online. Checking only the most recent payment would incorrectly conclude the bill isn't fully paid even after a customer has successfully completed all required partial payments; only the sum of all successful payments correctly reflects the total amount actually paid.

5. Precisely identify the critical section in the original TicketService.issueTicket() method, and explain why it qualifies as one.
The critical section is the sequence: reading the list of parking spots and finding an empty one matching the requested vehicle type (allotmentStrategy.findSpot(...)), followed by marking that specific spot OCCUPIED and saving it. This qualifies as a critical section because it involves a read followed by a write to shared data (the spot's status), and if two threads execute this sequence concurrently without coordination, both could read the same spot as empty before either writes, resulting in both threads believing they successfully claimed the same physical spot.

6. Why was a dedicated spotLock field used, rather than marking the entire issueTicket() method synchronized?
Marking the entire method synchronized would force every gate's request to fully serialize through the entire method, including work that doesn't touch shared spot data at all (fetching the gate, validating gate type, constructing the Vehicle object). Using a dedicated lock object scoped only around the spot-finding-and-marking section allows all of that unrelated work to proceed in parallel across multiple threads, and only forces threads to wait during the small portion that actually needs protection, meaningfully reducing overall wait time as demonstrated by the throughput comparison in this document.

7. Explain, using the two-gate ConcurrencyTest, why testing with two distinct Gate objects is more rigorous than testing with two threads calling through a single Gate object.
The specific problem being solved, first named during the design phase, was described precisely as "two gates trying to grab the same parking spot at the same time," not simply "two requests happening simultaneously." Using two real, distinct Gate objects with their own IDs, both feeding into the same TicketService instance, recreates the actual named scenario exactly. A test using only one Gate object would prove something more general (concurrent access in the abstract) but would not specifically validate the exact multi-gate scenario the system was promised to handle correctly.

8. Why does creating a fresh Object as a lock inside the method being synchronized fail to prevent a race condition, even though the code compiles and appears to use synchronized correctly?
Java's synchronized mechanism only prevents concurrent execution among threads that are contending for the same specific lock object's monitor. If a new lock object is created inside the method body (Object lock = new Object();), every single invocation of that method, on every thread, creates its own distinct, unrelated lock object. Since no two threads ever actually share the same lock instance, each thread acquires its own lock trivially and none of them are ever forced to wait for another, providing no synchronization protection whatsoever, despite the code superficially looking correct.

9. What specific edge case did the AI-suggested per-vehicle-type locking fix fail to handle, and why?
It failed to handle the case where a single physical ParkingSpot supports multiple vehicle types (a direct consequence of the size-based spot design from the schema lecture, where a truck spot's supportedVehicleTypes list includes TRUCK, CAR, and BIKE). Because the fix locked based on the requested vehicle type rather than the specific spot being examined, two gates requesting different vehicle types (say, CAR and TRUCK) could acquire two entirely different locks and then both legally proceed to examine and claim the exact same physical spot, since that spot happened to support both requested types, reintroducing the original race condition for any spot supporting more than one type.

10. Describe the correct, per-spot locking strategy implemented in claimAnySpotFor(), and explain the purpose of each of its three steps.
Step 1 reads a list of candidate spots matching the requested vehicle type, without any locking, since this is a read-only operation and the list may already be slightly stale by the time it's acted on. Step 2 acquires a lock on the specific spot object currently being considered (synchronized(spot)), meaning two threads only block each other if they happen to be contending for that exact same spot. Step 3, inside that lock, re-checks the spot's current status before claiming it, since another thread might have already claimed this exact spot in the gap between Step 1's read and Step 2's lock acquisition; this re-check is what actually closes the race condition, and skipping it would silently reintroduce the bug.

11. Why does the correct per-spot locking fix loop through candidate spots and "fall through" to the next one, rather than failing immediately if the first candidate is already taken?
If the first candidate spot is found to be occupied during the re-check inside the lock (because another thread claimed it in the interim), that doesn't necessarily mean no spots are available; other candidate spots matching the vehicle type may still be free. Falling through to try the next candidate, rather than immediately throwing ParkingFullException, ensures the method only reports the lot as full when genuinely no matching spot could be claimed after checking every candidate, correctly reflecting the true state of the system rather than reacting to a single momentarily-lost race.

12. Summarize the four-point checklist used to verify AI-generated code in this document's AI Corner, and explain which point actually caught the concurrency bug.
The checklist checks whether the code matches the required interface or contract, whether it follows the codebase's existing conventions, whether it handles edge cases, and whether it actually performs correctly for the system's real, specific constraints. The AI's fine-grained locking suggestion passed the first two checks cleanly (same method signature, same exceptions, consistent style) and appeared to handle general edge cases reasonably. It was specifically the fourth check, verifying correctness against this system's real constraint that a single spot can support multiple vehicle types, that surfaced the actual race condition the fix silently reintroduced.

Self-Check Questions
In your own words, explain why InMemoryRepository<T extends BaseModel> is preferable to writing four separate, nearly identical repository classes.
Trace through: if PaymentService.makePayment() summed all payments regardless of status, describe a specific sequence of events that would incorrectly free a parking spot.
Write a snippet: implement a UserChoiceStrategy class implementing AllotmentStrategy, where the caller supplies a specific preferred spot ID rather than letting the system auto-pick the nearest one.
Compare the whole-method synchronized approach and the small-critical-section synchronized approach in terms of what work is allowed to run in parallel under each.
Explain, in your own words, why a ConcurrencyTest using two threads that both call through the same single Gate object would be a weaker proof than the one built in this document.
Trace through: walk through, step by step, what happens if the "fresh lock object" bug from the quiz in Section 5 is present, when two threads call issueTicket() for the same spot at nearly the same instant.
Write a snippet: sketch a second FeeCalculationStrategy implementation (for example, a flat rate regardless of parking duration), and explain what would need to change in BillService to use it instead of HourlyRateStrategy.
Compare the AI-suggested per-vehicle-type locking fix to the correct per-spot locking fix. Identify the exact moment in each approach's execution where their behavior diverges for two gates requesting different but overlapping vehicle types.
Explain why the re-check step (Step 3) inside claimAnySpotFor()'s synchronized(spot) block is necessary, even though Step 1 already filtered for spots matching the vehicle type.
Trace through: if a sixth, brand-new VehicleType were introduced to the system, list every file or class from this document that would need to change, and every one that would not.
In your own words, explain why this document explicitly separates its one-gate end-to-end demo (Section 6) from its two-gate concurrency test (Section 5), rather than combining them into one test.
Write a short paragraph describing, using your own words, why "the code compiles and passes review checks 1 through 3" is not sufficient evidence that AI-generated concurrent code is actually safe.
Further Reading
Post-Read 6, Machine Coding 6: Code Parking Lot 1 - this document builds directly on the model classes, the incomplete TicketController, and the spot-size design decision that later exposes the AI Corner's locking bug; revisit it for the full reasoning behind supportedVehicleTypes as a list.
Post-Read 5, Machine Coding 5: Design Parking Lot - the original source of the two-gates-one-spot race condition, first named (but not solved) in that session's AI Corner, and the original source of requirements R4, R5, R6, and R8 referenced throughout this document.
Java Concurrency in Practice (Brian Goetz et al.) - the standard reference for Java's synchronized keyword, critical sections, race conditions, and fine-grained locking strategies, directly relevant to every concept introduced in Sections 5 and 7.
Oracle Java Documentation on Generics and Bounded Type Parameters - the official reference for how <T extends BaseModel> works, relevant to InMemoryRepository in Section 2.
Oracle Java Documentation on the java.util.concurrent package - relevant to ConcurrentHashMap, used in the AI-suggested (and ultimately rejected) per-vehicle-type locking fix in Section 7.
Post-Read 4, Machine Coding 4: Code TicTacToe 2 - the original source of the "AI is good for implementing a well-specified piece, but the judgement calls remain yours" discipline applied again in this document's AI Corner.
Homework
1. Add a second FeeCalculationStrategy (for example, a flat
   rate regardless of time) and prove BOTH strategies work by
   swapping which one BillService uses, without changing
   BillService itself.

2. Implement UserChoiceStrategy for AllotmentStrategy — given a
   list of available spots, let the "user" (just a method
   parameter for now) pick which one they want, instead of
   always auto-picking the nearest one.

3. Add a real EXIT gate to Main.java, and update TicketService
   so issuing a ticket at an EXIT gate is correctly rejected
   (this logic already exists — just prove it with a real
   second gate).

4. Fix the AI Corner's locking bug for real: implement per-spot
   locking instead of per-vehicle-type locking, and update
   ConcurrencyTest to prove it — two gates competing for
   different vehicle types should now run in parallel, while two
   gates competing for the SAME physical spot should still be
   correctly blocked.

5. Convert VehicleType, ParkingSpotStatus, BillStatus, and
   PaymentStatus from plain enums into the full lookup-table-
   backed classes we originally designed in Lecture 6.

6. Push everything to GitHub — branch name: parkinglot-code-part2-complete

Last changed by 
 
Tushar Harsan·Follow
0
46
Add a comment
Published on  HackMD
