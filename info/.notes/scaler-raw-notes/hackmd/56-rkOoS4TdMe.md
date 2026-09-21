Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/rkOoS4TdMe

Post Read : Machine Coding - 11: Code BookMyShow 3
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Sep 8, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 11: Code BookMyShow 3
Section 1: Finishing bookMovie(), One Continuous Build
What It Means

Recalling exactly where bookMovie() was left, as a plan of comments only:

@Transactional(isolation = Isolation.SERIALIZABLE)
public Booking bookMovie(Long userId, List<Long> seatIds, Long showId) {
    // 1. Get user  2. Get show
    // ---- LOCK ----
    // 3. Get ShowSeats  4. Check available  5. Throw if not
    // 6. Mark BLOCKED  7. Save
    // ---- END LOCK ----
    // 8. Create Booking  9. Return
}

Steps 1 and 2 are pure recall, the same shape already used throughout this project:

User bookedBy = userRepository.findById(userId)
        .orElseThrow(() -> new RuntimeException("User not found"));

Show bookedShow = showRepository.findById(showId)
        .orElseThrow(() -> new RuntimeException("Show not found"));

Some codebases redeclare inherited repository methods like findById/save with @Override, purely for readability. This is a no-op, JpaRepository already provides these for free. A method only gets declared on a repository interface when it's genuinely new, like findByEmail later in this session.

Practical Mechanics: The Expiry Gap

Last session's availability check was simple: is the seat AVAILABLE? Working through what this misses directly. User A selects seat C4, it gets marked BLOCKED, then the tab gets closed, no payment ever completes. Twenty minutes later, User B tries to book that same seat. With last session's plain check, what happens to User B?

User B gets rejected. The seat still says BLOCKED, even though the hold should have expired. The seat is stuck, unbookable by anyone, indefinitely.

Post-Read 10's homework named a scheduled background job sweeping expired seats as one fix. Today's approach shows the other common real-world shortcut: don't sweep proactively, check for expiry lazily, exactly at the moment someone else tries to book that seat.

List<ShowSeat> showSeats = showSeatRepository.findAllById(seatIds);

for (ShowSeat showSeat : showSeats) {
    boolean isAvailable = showSeat.getShowSeatStatus() == ShowSeatStatus.AVAILABLE;

    boolean isExpiredBlock = showSeat.getShowSeatStatus() == ShowSeatStatus.BLOCKED
            && Duration.between(showSeat.getBlockedAt().toInstant(), new Date().toInstant())
                    .toMinutes() > 15;

    if (!(isAvailable || isExpiredBlock)) {
        throw new RuntimeException("Seat " + showSeat.getId() + " is not available");
    }
}

What this deliberately does not do is worth stating directly: it writes nothing back to the database just because 15 minutes have passed. The row can literally say BLOCKED in MySQL for hours, nobody proactively fixes it, until the exact moment someone else's booking attempt reads that row and re-evaluates the rule for itself.

Quiz Recap

Seat C4 was BLOCKED at 2:00 PM. At 2:20 PM, User B tries to book it using the expiry check above. What does the showSeatStatus column literally say at 2:19 PM, and what happens to User B's request?

A) The column already auto-flipped to AVAILABLE once 15 minutes passed, via @Temporal
B) At 2:19 PM it still says BLOCKED, nothing reset it. User B's request at 2:20 PM passes anyway, because the check treats "BLOCKED for over 15 minutes" as available, then overwrites the row under User B's booking
C) User B's request is rejected, a scheduled cleanup job is required first
D) User B's request fails, the same ShowSeat can never be linked to two different users, even at different times
Correct answer: B. The whole point of a lazy check is that the stale row is never proactively rewritten, only re-evaluated on demand. At 2:19 PM, nothing has touched the row at all; it still literally says BLOCKED. Once User B's request arrives at 2:20 PM and re-evaluates the rule, the isExpiredBlock condition becomes true, and the request proceeds.
Why A is wrong: it invents automatic behavior that doesn't exist; @Temporal is only a data-type annotation clarifying how a Date field maps to a column, it has no effect on scheduling or automatic updates.
Why C is wrong: it wrongly assumes the scheduled job is mandatory for expiry to work at all; it's an alternative or a complement, not a requirement, exactly as demonstrated by this lazy check working on its own.
Why D is wrong: it contradicts what was already proven in Post-Read 10, Booking and ShowSeat are genuinely many-to-many over time, the same physical seat can legitimately be linked to different bookings across different time periods.

An honest limitation worth naming directly: a seat abandoned during a dead period, 3 AM, nobody checking that particular show, sits BLOCKED indefinitely with nobody around to trigger the re-check. Real systems usually run both this lazy check and an occasional background sweep as a safety net. This is exactly why Post-Read 10's scheduled-job homework stays open, it isn't redundant with today's fix, it's belt-and-suspenders alongside it.

Practical Mechanics: The Finished Method
@Transactional(isolation = Isolation.SERIALIZABLE)
public Booking bookMovie(Long userId, List<Long> seatIds, Long showId) {

    User bookedBy = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
    Show bookedShow = showRepository.findById(showId)
            .orElseThrow(() -> new RuntimeException("Show not found"));

    // -------------- TAKE LOCK ---------------
    List<ShowSeat> showSeats = showSeatRepository.findAllById(seatIds);

    for (ShowSeat showSeat : showSeats) {
        boolean isAvailable = showSeat.getShowSeatStatus() == ShowSeatStatus.AVAILABLE;
        boolean isExpiredBlock = showSeat.getShowSeatStatus() == ShowSeatStatus.BLOCKED
                && Duration.between(showSeat.getBlockedAt().toInstant(), new Date().toInstant())
                        .toMinutes() > 15;

        if (!(isAvailable || isExpiredBlock)) {
            throw new RuntimeException("Seat " + showSeat.getId() + " is not available");
        }
    }

    List<ShowSeat> savedShowSeats = new ArrayList<>();
    for (ShowSeat showSeat : showSeats) {
        showSeat.setShowSeatStatus(ShowSeatStatus.BLOCKED);
        showSeat.setBlockedAt(new Date());
        savedShowSeats.add(showSeatRepository.save(showSeat));
    }
    // --------------- END LOCK -----------------

    Booking booking = new Booking();
    booking.setBookingStatus(BookingStatus.PENDING);
    booking.setShowSeats(savedShowSeats);
    booking.setUser(bookedBy);
    booking.setBookedAt(new Date());
    booking.setShow(bookedShow);
    booking.setAmount(priceCalculator.calculatePrice(bookedShow, savedShowSeats));
    booking.setPayments(new ArrayList<>());

    return bookingRepository.save(booking);
}

Two things worth pointing at directly:

Every showSeatRepository.save(showSeat) inside that loop is an update, not an insert, since each ShowSeat already has an ID from being fetched, Spring Data JPA recognizes the row already exists and updates it in place.
blockedAt gets reset to new Date() on every lock, including seats being reclaimed from an expired block. This resets the 15-minute clock for the new attempt, exactly the intended behavior.
Hidden Pitfalls
Proactively rewriting a seat's status the moment 15 minutes pass: a lazy expiry check deliberately does no such thing; the row stays BLOCKED in the database until something else actually reads and re-evaluates it, which is a design choice, not an oversight.
Treating a lazy expiry check as a complete replacement for a scheduled sweep: a seat abandoned during a low-traffic period can sit BLOCKED indefinitely if nobody happens to attempt booking it again; a background sweep remains a genuine safety net alongside, not instead of, the lazy check.
Forgetting to reset blockedAt when reclaiming an expired block: without resetting the timestamp, a newly reclaimed seat would immediately appear expired again to the very next check, rather than starting a fresh 15-minute window for its new holder.
Section 2: PriceCalculator, Quick Reuse, Not a Rebuild
What It Means

A different way of writing PriceCalculator surfaces in today's material than the one already built in Post-Read 10, fetching all of a show's pricing rows and loop-matching, instead of a direct lookup. Checking directly whether there's any reason to replace the existing, working version: not really. The direct lookup (findByShowAndSeatType(show, seatType)) is simpler and avoids unnecessary work. Rebuilding it differently would only be inconsistent with what already exists, for no actual benefit.

The existing version from Post-Read 10 is kept exactly as-is. The one thing worth double-checking is the call site:

// Already exists, from last class — reused as-is:
public int calculatePrice(Show show, List<ShowSeat> showSeats) { ... }

// Call it in bookMovie() matching THIS exact parameter order:
booking.setAmount(priceCalculator.calculatePrice(bookedShow, savedShowSeats));

A small, easy-to-miss trap worth naming directly: if an AI-generated snippet ever reverses the parameter order (showSeats, show instead of show, showSeats), that is exactly the kind of "looks right, compiles wrong" mistake this series has been training the habit of catching all along, always check against the method signature actually declared, not the one that "feels natural" to write at the call site.

Hidden Pitfalls
Rebuilding a working implementation just because a different approach exists: consistency with an already-correct, already-tested piece of code has real value; replacing it with a structurally different but functionally equivalent version introduces risk for no benefit.
Reversing parameter order at a call site without checking the actual method signature: two parameters of similar or related types (Show and List<ShowSeat>) are especially easy to swap by mistake, and such a swap can compile cleanly while producing incorrect behavior.
Section 3: Wiring the Controllers
What It Means

This is a recall applied directly, not a new derivation: @Controller alone would try to render a view instead of returning JSON; a real REST endpoint needs @RestController combined with @PostMapping and @RequestBody.

Practical Mechanics
@RestController
@RequestMapping("/booking")
public class BookingController {

    private BookingService bookingService;

    @Autowired
    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @PostMapping("/book")
    public BookMovieResponseDto bookMovie(@RequestBody BookMovieRequestDto request) {
        BookMovieResponseDto response = new BookMovieResponseDto();

        try {
            Booking booking = bookingService.bookMovie(
                    request.getUserId(), request.getShowSeatIds(), request.getShowId());

            response.setResponseStatus(ResponseStatus.SUCCESS);
            response.setBookingId(booking.getId());
            response.setAmount(booking.getAmount());
        } catch (Exception e) {
            response.setResponseStatus(ResponseStatus.FAILURE);
        }

        return response;
    }
}

An honest gap worth naming directly: catching a bare Exception and reporting a generic FAILURE hides why something failed, a bad seat ID, a bad user ID, the R10 seat cap being exceeded, all look identical to the client. This is exactly what Post-Read 10's homework (real custom exceptions plus @ControllerAdvice) was meant to address, and it remains open here, not solved in this session.

Hidden Pitfalls
Catching a bare Exception and returning only a generic failure status: this hides the actual cause of failure from the client, making it impossible to distinguish "seat unavailable" from "user not found" from "too many seats requested" without inspecting server logs.
Treating this generic error-handling pattern as acceptable for a production system: it's an explicitly named, deliberate simplification carried over from Post-Read 10 as unfinished homework, not a pattern to keep indefinitely.
Section 4: User Signup and Login
What It Means

New territory: real user accounts. The same layered shape already used for booking applies here too: DTO → Repository → Service → Controller. Two genuine mistakes surface live in this section, caught exactly where they'd happen in a real review.

A question worth answering directly: what does a signup request need to carry, and what should the response carry back? Email and password in; success or failure plus the new user's ID out.

Practical Mechanics: DTOs
@Getter
@Setter
public class SignUpRequestDto {
    private String email;
    private String password;
}

@Getter
@Setter
public class SignUpResponseDto {
    private ResponseStatus responseStatus;
    private Long userId;
}

Practical Mechanics: Repository, and Bug Catch #1

One genuinely new lookup is needed: finding a user by email, to check for duplicates at signup. A question worth checking before writing this: what is the correct stereotype annotation for a repository interface?

@Repository, not @Service. @Service is reserved for business-logic classes. This matters even though Spring is fairly forgiving here, using the wrong stereotype still registers as a bean in most setups, but it is semantically incorrect, and @Repository specifically enables Spring's exception-translation for database errors. The correct annotation is used deliberately, not interchangeably.

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}

Practical Mechanics: Service, and Bug Catch #2

BCryptPasswordEncoder is needed as a dependency here, its non-trivial behavior is explained fully in Section 5; for now, it is treated as the standard tool for hashing passwords.

Watching the constructor closely as it gets written: it accepts bCryptPasswordEncoder as a parameter. A question worth checking directly: what's the one easy-to-forget line here that would make this dependency completely useless?

Forgetting this.bCryptPasswordEncoder = bCryptPasswordEncoder;, accepting the parameter but never assigning it to the field. This is a real mistake sitting in this session's own material. If missed, the field stays null, and a tempting "fix" is to write new BCryptPasswordEncoder() locally inside signUp() instead, which technically works, but creates a brand-new encoder object on every single signup instead of reusing one shared instance. This alternative is explicitly rejected in favor of doing it properly.

@Service
public class UserService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    @Autowired
    public UserService(UserRepository userRepository,
                        BCryptPasswordEncoder bCryptPasswordEncoder) {
        this.userRepository = userRepository;
        this.bCryptPasswordEncoder = bCryptPasswordEncoder;
    }

    public User signUp(String email, String password) {
        Optional<User> existing = userRepository.findByEmail(email);
        if (existing.isPresent()) {
            throw new RuntimeException("User with this email already exists.");
        }

        User user = new User();
        user.setEmail(email);
        user.setPassword(bCryptPasswordEncoder.encode(password));
        user.setBookings(new ArrayList<>());

        return userRepository.save(user);
    }

    public User login(String email, String password) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        if (!bCryptPasswordEncoder.matches(password, user.getPassword())) {
            throw new RuntimeException("Incorrect password");
        }

        return user;
    }
}

For this constructor injection to actually work, BCryptPasswordEncoder needs to be a real Spring-managed bean somewhere. It is not one of this project's own classes, so @Component cannot be added to it directly. It gets registered once, explicitly, instead:

@Configuration
public class SecurityConfig {
    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {
        return new BCryptPasswordEncoder();
    }
}

Spring now creates exactly one BCryptPasswordEncoder, and hands that same instance to any class that asks for it, UserService today, anything else later.

Practical Mechanics: Controller and CLI Smoke Test
@RestController
@RequestMapping("/user")
public class UserController {

    private final UserService userService;

    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/signup")
    public SignUpResponseDto signUp(@RequestBody SignUpRequestDto request) {
        SignUpResponseDto response = new SignUpResponseDto();
        try {
            User user = userService.signUp(request.getEmail(), request.getPassword());
            response.setResponseStatus(ResponseStatus.SUCCESS);
            response.setUserId(user.getId());
        } catch (Exception e) {
            response.setResponseStatus(ResponseStatus.FAILURE);
        }
        return response;
    }
}

A quick way to smoke-test this without Postman is pure recall from Post-Read 9's R9 CLI runner: a CommandLineRunner on the main application class, the same pattern already used once before.

@SpringBootApplication
@EnableJpaAuditing   // needed shortly — Section 6
public class Bookmyshowmay23Application implements CommandLineRunner {

    @Autowired
    private UserController userController;

    @Override
    public void run(String... args) {
        SignUpRequestDto request = new SignUpRequestDto();
        request.setEmail("vivek@scaler.com");
        request.setPassword("password");
        userController.signUp(request);
    }

    public static void main(String[] args) {
        SpringApplication.run(Bookmyshowmay23Application.class, args);
    }
}

One caveat worth stating plainly: field injection (@Autowired private UserController) directly on the main application class is generally discouraged in real service code, it hides the dependency and makes testing harder. This is a throwaway test harness on the entry point, not a pattern to copy elsewhere in the codebase.

Hidden Pitfalls
Annotating a repository interface with @Service instead of @Repository: this is semantically incorrect even though Spring may still register the bean successfully; @Repository specifically enables Spring's database exception translation, which is lost with the wrong annotation.
Accepting a constructor parameter without assigning it to the corresponding field: the dependency compiles cleanly but silently remains null at runtime, a bug that only surfaces the moment the field is actually used, often far from where the mistake was made.
"Fixing" a null dependency by instantiating it locally inside the method that needs it: new BCryptPasswordEncoder() created fresh on every call technically works but abandons the benefit of a single shared, Spring-managed instance, and masks the real bug (the missing field assignment) instead of fixing it.
Using field injection directly on a production service class: this hides a class's real dependencies from its constructor signature and makes unit testing meaningfully harder; it is acceptable only as a disposable test harness, as demonstrated on the CommandLineRunner entry point here, not as a general pattern.
Section 5: BCrypt, Why Plaintext Fails, Why matches() Not equals()
What It Means

The simplest possible idea: store user.password as the exact plain string the user typed. Working through what goes wrong the day the database gets breached: every user's real password is exposed instantly, and since people commonly reuse passwords across sites, this compromises their other accounts too. Hashing the password instead is the obvious next step.

Pushing further on the next obvious idea: suppose a plain hash function is used, one where the same input always produces the same output. Alice and Bob both pick "hunter2" as their password. What do their two stored hashes look like?

Identical. Same input, same fixed function, same output. If an attacker cracks one, they instantly know every account sharing that hash.

This is exactly the gap bcrypt closes by mixing in a salt, a random value generated fresh every single time encode() is called, even for the exact same input.

encode("hunter2") → "$2a$10$N9qo8uLOickgx2ZMRZoMy..."
encode("hunter2") → "$2a$10$abcXYZ123differentSalt..."

Same input. Different output. Every single time.

A question worth checking directly: if encode() gives a different result every time, even for the same password, how could a login attempt possibly be checked against what was stored?

Re-running encode() on the login attempt and comparing strings directly cannot work, the two results would almost never match, even when the password is correct.

Here is the actual trick that makes this work. The salt is never stored separately somewhere, and bcrypt never needs to "decrypt" anything at all. The salt is baked directly into the stored hash string itself, sitting there in plain sight.

$2a$10$N9qo8uLOickgx2ZMRZoMye.IjZAgcfl7p92ldGxad68LJZdL17lhWy
    └──────── salt ─────────┘ └────────── hash ──────────┘

matches(rawPassword, storedHash) does not reverse anything. It reads the salt back out of this stored string, re-hashes the login attempt using that exact same salt, and checks whether the result matches the hash portion sitting right next to it. One direction only, computed twice, never reversed.

WRONG: encode(loginAttempt).equals(storedHash)
       → generates a NEW random salt, hashes with THAT,
         compares against a hash made with a DIFFERENT salt.
         Almost never matches, even for the right password.

RIGHT: bCryptPasswordEncoder.matches(rawPassword, storedHash)
       → reuses the ORIGINAL salt already embedded inside
         storedHash, hashes with THAT, compares correctly.

Quiz Recap

A teammate writes if (user.getPassword().equals(bCryptPasswordEncoder.encode(password))) instead of .matches(...). Alice signed up with "hunter2", and now logs in with the exact same password. Does this work?

A) Yes, the exact same password string produces the exact same hash both times
B) No, encode() generates a brand-new random salt on every call, so it never reuses the salt embedded in Alice's stored hash. The freshly computed hash uses a different salt, so .equals() fails even though the password itself is correct
C) Yes, but only the very first login after signup
D) No, encode() isn't usable outside signUp()
Correct answer: B. This is the exact mechanism just walked through: matches() works because it re-extracts the original salt from the stored string before re-hashing; plain encode() always manufactures a fresh salt instead, so the two hashes can never agree even for a correct password.
Why A is wrong: it wrongly assumes encode() behaves like a deterministic hash function, when its entire purpose is to produce a different result every time, specifically to prevent the same-password-same-hash vulnerability demonstrated with Alice and Bob.
Why C is wrong: it invents a false exception with no basis; there is nothing about a "first login" that would make .equals() behave any differently than any subsequent login.
Why D is wrong: this is simply false; encode() is a public method usable anywhere. The actual bug is calling the wrong method for the wrong purpose, not that one method is somehow inaccessible outside a specific context.
Hidden Pitfalls
Storing passwords as plain text: an exposed database instantly reveals every user's actual password, compromising not just this system but potentially every other account where that same password was reused.
Using a deterministic hash function without a salt: identical passwords across different users produce identical stored hashes, meaning cracking one instantly reveals every account sharing that same password.
Comparing encode(input) against a stored hash using .equals(): since encode() generates a fresh random salt on every call, this comparison fails even for a correct password; .matches() must be used instead, since only it correctly reuses the original embedded salt.
Section 6: Automatic Timestamps, JPA Auditing
What It Means

So far, lines like booking.setBookedAt(new Date()) have been written manually, everywhere a timestamp was needed. Automating this properly is the next step.

@MappedSuperclass
public class BaseModel {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @LastModifiedDate
    @Temporal(TemporalType.TIMESTAMP)
    private Date lastModifiedAt;
}

@CreatedDate is meant to auto-fill on insert. @LastModifiedDate is meant to auto-update on every change. Testing this directly: starting the app right now, signing up a user, and checking the users table, will these columns actually be populated?

They will not. Both columns come back NULL. These annotations alone do nothing on their own.

@CreatedDate / @LastModifiedDate need TWO more things:
1. On BaseModel:            @EntityListeners(AuditingEntityListener.class)
2. On the main app class:   @EnableJpaAuditing

Without both of these, the two annotations are inert labels. @EntityListeners tells Hibernate "run this listener around every save on entities extending me." @EnableJpaAuditing turns the whole feature on, application-wide.

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public class BaseModel {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @LastModifiedDate
    @Temporal(TemporalType.TIMESTAMP)
    private Date lastModifiedAt;
}

@EnableJpaAuditing was already added on Bookmyshowmay23Application back in Section 4, when the CommandLineRunner was written.

Quiz Recap

A teammate adds @CreatedDate/@LastModifiedDate correctly, and even adds @EntityListeners(AuditingEntityListener.class), but forgets @EnableJpaAuditing on the main class. A user signs up. What do created_at/last_modified_at look like?

A) Both correctly populated, @EntityListeners alone is enough
B) Both remain NULL, without @EnableJpaAuditing turned on application-wide, the listener has nothing to delegate to, so neither field gets touched
C) created_at populates, last_modified_at needs a manual update() call
D) The app fails to start, this combination is invalid
Correct answer: B. This is the exact bug demonstrated live in this session. @EntityListeners marks which listener class should run around saves, but @EnableJpaAuditing is what actually activates JPA's auditing infrastructure application-wide; without it, the listener has no active auditing feature to delegate to, so it effectively does nothing.
Why A is wrong: it wrongly assumes the listener annotation alone is sufficient, when in fact both pieces are required together.
Why C is wrong: it invents a split behavior between the two annotations that doesn't exist; if one silently fails to populate, so does the other, since both depend on the same missing application-wide activation.
Why D is wrong: this combination is not invalid in any way that would prevent startup; it is simply silently non-functional, the same "silent failure" shape already seen with reserved keywords in Post-Read 10 and EnumType.ORDINAL corruption in Post-Read 9.

With both pieces correctly in place, createdAt/lastModifiedAt become genuinely automatic. Every manual setBookedAt(new Date())-style line across the codebase can now be deleted; BaseModel handles timestamping uniformly for every entity that extends it.

Hidden Pitfalls
Assuming @CreatedDate/@LastModifiedDate work on their own: these annotations are inert without both @EntityListeners(AuditingEntityListener.class) on the base class and @EnableJpaAuditing on the application's entry point; missing either one produces silently NULL columns with no error raised anywhere.
Leaving manual timestamp-setting code in place after enabling JPA auditing: once auditing is correctly wired, manual calls like setBookedAt(new Date()) become redundant; leaving them in risks confusion about which mechanism is actually responsible for populating these fields.
Section 7: AI Corner, a Parallel CRUD Stack
What It Means

One complete stack has just been hand-built for User. Consider a theatre admin needing to add a new Theatre under a Region, mechanical CRUD work, following a pattern already established by hand. This is a reasonable task to hand to AI.

Practical Mechanics

Prompt used:

"Generate a Spring Boot Controller, Service, Repository, and
Request/Response DTOs for adding a new Theatre, given a name and
a regionId. Follow the same layered pattern as our
UserController/UserService: RestController, constructor-injected
Service, Service does the real work, Repository just saves."

Before even running this, the same four-point checklist applied at every AI Corner in this series gets laid out, so it's clear exactly what to check for once a response actually comes back:

1. Match the contract?      — Did it actually generate all 4
                               pieces asked for: DTO, Repository,
                               Service, Controller?
2. Follow our conventions?  — Constructor injection? @RestController,
                               not @Controller? Same
                               try/catch → ResponseStatus pattern
                               as UserController?
3. Handle edge cases?       — What happens if regionId doesn't
                               belong to any real Region?
4. Fit OUR real constraints? — Everywhere a related entity has
                               been fetched by ID in this project
                               — userId, showId — the pattern has
                               always been
                               repository.findById(id).orElseThrow(...)
                               before using it. Does the generated
                               Service do the same for regionId, or
                               does it fabricate a Region reference
                               without checking it's real?

Point 4 is where the real discussion tends to happen. If the generated Service builds its Region reference without first calling regionRepository.findById(...).orElseThrow(...), the fix is to correct it by hand, using that exact convention already established consistently everywhere else in this codebase (userRepository.findById(userId).orElseThrow(...), showRepository.findById(showId).orElseThrow(...)). If the AI response already does this correctly on its own, no fix is needed, it simply gets confirmed and adopted.

The pattern worth internalizing here is the same one repeated throughout every AI Corner in this series: the first three checklist points are about whether the generated code is well-formed and stylistically consistent. The fourth point is the one that requires actually knowing this specific system's own established conventions, and it is exactly the point most likely to catch a foreign-key validation gap like this one, since a generic prompt has no way of knowing that this codebase has a consistent, deliberate habit of validating every foreign ID before using it.

Hidden Pitfalls
Trusting a generated CRUD stack because the first three checklist points pass cleanly: well-formed, conventionally-styled code can still silently skip a foreign-key existence check; only comparing directly against this system's own established pattern (findById().orElseThrow() everywhere else) reliably catches this specific class of gap.
Building a Region reference from a raw ID without verifying that ID corresponds to a real row: this allows a Theatre to be created pointing at a nonexistent Region, producing either a database-level foreign key error at save time (if constraints are enforced) or a silently broken relationship (if they aren't).
Closing the BookMyShow Arc

This is genuinely the end of BookMyShow as a class project. Taking stock of the whole arc, not just this session:

Lecture 1 (Post-Read 9): Every model, real JPA mappings, one full requirement
           (R9) end-to-end — learned to read a schema critically and
           catch real gaps (missing class body, wrong field, missing
           link).

Lecture 2 (Post-Read 10): The hardest requirement (R10/R11) — a genuine
           race condition, solved for real: naive fix → broke it →
           soft locking → SERIALIZABLE → proved it with real threads.

Lecture 3 (Post-Read 11, today): Closed the last gap (seat expiry),
           built real user accounts with properly-salted passwords,
           and caught two more live bugs by reading code critically
           instead of trusting it because it compiled.

The specific APIs, Spring, JPA, bcrypt, are not the real takeaway. The real takeaway, repeated three times now across this arc, is: build the obvious version, find exactly where it breaks, and fix it with the smallest correct tool, a status field instead of a database lock, a salt instead of a plain hash, @EnableJpaAuditing instead of assuming an annotation just works on its own. That instinct transfers directly into Splitwise, and into every real system after it.

CODE BOOKMYSHOW 3 — built today:
- bookMovie() fully implemented — every one of the 9 original
  steps is now real code, including the expiry-aware lock check
- R10/R11's last gap closed: lazy expiry check at booking time
- PriceCalculator reused as-is from last class — not rebuilt
- BookingController and UserController both real REST endpoints
- Full User signup + login: DTOs, Repository, Service, Controller,
  BCrypt hashing
- Automatic createdAt/lastModifiedAt via JPA auditing, fully wired

Real bugs caught live, not shown after the fact:
1. UserRepository wrongly annotated @Service → fixed to @Repository
2. BCryptPasswordEncoder accepted but never assigned → fixed, and
   promoted to a proper shared @Bean
3. @CreatedDate/@LastModifiedDate silently did nothing without
   @EntityListeners + @EnableJpaAuditing → added both
4. AI's TheatreService skipped validating regionId exists →
   fixed with our own findById().orElseThrow() convention

This is the last BookMyShow class. Everything below is now left
for independent extension, not something built further together
in this series:
- Custom exception hierarchy + @ControllerAdvice (still plain
  RuntimeException everywhere)
- /user/login endpoint (service method exists, not yet wired)
- Payment flow, PENDING → CONFIRMED
- The scheduled-job version of seat expiry (complements today's
  lazy check, doesn't replace it)

Common Pitfalls Summary
1. Treating "check availability" and "expire a stale block" as
   requiring a proactive database write.
   -> A lazy expiry check re-evaluates the rule on demand instead;
      the row can say BLOCKED for hours until someone else's
      request reads and re-checks it.

2. Treating a lazy expiry check as a full replacement for a
   scheduled sweep.
   -> A seat abandoned during low traffic can sit BLOCKED
      indefinitely if nobody attempts to book it again; a
      background sweep remains a real safety net.

3. Forgetting to reset blockedAt when reclaiming an expired
   block.
   -> Without the reset, a newly reclaimed seat would appear
      expired again on the very next check.

4. Rebuilding a working implementation (PriceCalculator) just
   because a different valid approach exists.
   -> Introduces inconsistency and risk for no actual benefit
      over the already-correct existing version.

5. Reversing parameter order at a call site without checking the
   declared method signature.
   -> Compiles cleanly, produces incorrect behavior; especially
      easy with parameters of related types.

6. Catching a bare Exception and returning only a generic failure
   status to the client.
   -> Hides the real cause of failure (bad seat, bad user, seat
      cap exceeded all look identical to the caller).

7. Annotating a repository interface with @Service instead of
   @Repository.
   -> Semantically incorrect even if the bean still registers;
      loses Spring's database exception-translation behavior.

8. Accepting a constructor parameter without assigning it to the
   corresponding field.
   -> Compiles cleanly; the dependency silently stays null until
      it's actually used at runtime.

9. "Fixing" a null dependency by instantiating it locally inside
   the method that needs it.
   -> Works, but abandons a single shared instance and masks the
      real bug instead of fixing it.

10. Using field injection directly on a production service class.
    -> Hides real dependencies from the constructor signature and
       makes unit testing meaningfully harder.

11. Storing passwords as plain text.
    -> A single database breach instantly exposes every user's
       real password, and any other account reusing it.

12. Using a deterministic hash function without a salt.
    -> Identical passwords produce identical stored hashes;
       cracking one reveals every account sharing that password.

13. Comparing encode(input) against a stored hash using .equals()
    instead of using .matches().
    -> encode() generates a fresh random salt every call, so this
       comparison fails even for a correct password.

14. Assuming @CreatedDate/@LastModifiedDate work without
    @EntityListeners and @EnableJpaAuditing.
    -> Both annotations are inert without both pieces of
       configuration; columns silently stay NULL, no error raised.

15. Building a foreign-key reference (like Region) from a raw ID
    without verifying that ID corresponds to a real row.
    -> Allows creating an entity pointing at a nonexistent related
       row, breaking the relationship silently or at save time.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Trusting that code is correct because it compiles and the application starts successfully: nearly every real bug caught live in this session, the wrong repository stereotype, the unassigned field, the missing auditing configuration, compiles perfectly and starts the application without error; only careful, deliberate review catches these, not the build process.
Treating "the obvious fix" as the final fix without checking what it actually breaks under real conditions: this is the single repeated pattern across all three BookMyShow lectures, plain text passwords, a single shared database lock, an unvalidated foreign key, each obvious first attempt looked reasonable until checked against the real constraint it was meant to satisfy.
Key Terminology
Term	Meaning in Simple Words
Lazy Expiry Check	A pattern where a time-based condition (like a 15-minute hold expiring) is evaluated only when something else reads the affected data, rather than being proactively swept and corrected on a schedule.
Salt	A random value mixed into a password before hashing, generated fresh on every hash operation, ensuring that identical passwords never produce identical stored hashes.
BCrypt	A password-hashing algorithm that automatically generates and embeds a fresh salt directly inside its own output string, allowing a later comparison to re-extract and reuse that same salt without ever needing to reverse the hash.
@EntityListeners(AuditingEntityListener.class)	A JPA annotation marking a class so that Hibernate runs the specified listener around every save operation on entities extending it; required for auditing annotations like @CreatedDate to have any effect.
@EnableJpaAuditing	A Spring Boot annotation placed on the application's entry point that activates JPA's auditing infrastructure application-wide; without it, @CreatedDate/@LastModifiedDate remain inert even with @EntityListeners present.
AuditingEntityListener	The specific Spring Data JPA listener class that, once enabled via @EnableJpaAuditing and referenced via @EntityListeners, automatically populates fields annotated @CreatedDate and @LastModifiedDate.

JPA, Hibernate, @Entity, @MappedSuperclass, @Temporal, Repository/Service/Controller layering, DTOs, @RestController, soft locking, Isolation.SERIALIZABLE, and @Autowired were already defined in Post-Read 8, Post-Read 9, and Post-Read 10, and are not redefined here.

Frequently Asked Interview Questions

1. Explain the lazy expiry check pattern used to close R10's remaining gap, and contrast it with a scheduled background sweep.
A lazy expiry check re-evaluates whether a BLOCKED seat's hold has expired only at the moment another request actually reads that seat's status, treating a seat blocked for more than 15 minutes as if it were AVAILABLE for the purposes of that new request, without ever proactively writing anything back to the database just because time has passed. A scheduled sweep, by contrast, actively scans for and corrects expired holds on a fixed interval, regardless of whether anyone is currently trying to book those seats. The two are complementary: the lazy check handles active contention correctly with zero wasted background work, while the sweep catches seats abandoned during low-traffic periods that nobody else happens to request again.

2. Why is showSeatRepository.save(showSeat) inside the locking loop an update rather than an insert, and why does this distinction matter?
Each ShowSeat object being saved was originally obtained via findAllById(seatIds), meaning it already carries a real, existing primary key ID. Spring Data JPA (via Hibernate) recognizes that an entity with a populated ID likely already exists as a row, and issues an UPDATE statement rather than an INSERT. This distinction matters because inserting a duplicate row instead of updating the existing one would corrupt the data model, effectively creating a second, disconnected ShowSeat record for a seat that should only ever have one row per (show, seat) pairing.

3. Why does bcrypt need to generate a different salt on every call to encode(), even for the exact same input password?
If the same password always produced the same hash, any two users who happened to choose the same password would end up with identical stored hash values. An attacker who cracked one such hash (through any means) would then immediately know every other account sharing that same password, without needing to crack each one individually. Generating a fresh, random salt on every call ensures that identical passwords always produce different stored hashes, eliminating this cross-account exposure entirely.

4. Explain precisely how bCryptPasswordEncoder.matches(rawPassword, storedHash) is able to correctly verify a password without ever reversing or decrypting the stored hash.
The salt used to originally hash a password is not stored separately anywhere; it is embedded directly within the stored hash string itself, as a distinguishable segment at the start of that string. matches() extracts that embedded salt from the stored hash, uses it to hash the freshly supplied rawPassword using the exact same salt, and then compares the newly computed hash against the hash portion of the stored string. This works entirely in one direction, hashing is never reversed, only recomputed under identical conditions and compared.

5. What specifically goes wrong if user.getPassword().equals(bCryptPasswordEncoder.encode(password)) is used instead of .matches() for login verification, and why does this bug not manifest as an obvious crash?
encode(password) generates a brand-new, randomly chosen salt every time it is called, entirely independent of whatever salt was used when the password was originally stored. Comparing this newly generated hash against the previously stored hash via .equals() compares two hash values computed with two different salts, which will almost never match, even when the supplied password is genuinely correct. This does not manifest as a crash or exception; it simply causes every login attempt to fail with "incorrect password," even for users entering their correct credentials, a subtle, silent behavioral bug rather than an obvious failure.

6. Why does using the wrong Spring stereotype annotation (@Service instead of @Repository) on a repository interface not necessarily cause the application to fail at startup, and why is it still a real bug worth fixing?
Spring's component scanning is fairly permissive; in many configurations, a class annotated @Service still gets registered as a bean and injected wherever needed, so the application may start and even function correctly on the surface. The real problem is semantic and functional: @Repository specifically enables Spring's exception-translation mechanism, converting low-level database exceptions into Spring's own consistent DataAccessException hierarchy. Without the correct annotation, this translation does not happen, meaning error handling around database operations behaves inconsistently with the rest of the codebase, a bug that surfaces later, in exception-handling behavior, rather than immediately at startup.

7. Trace through exactly what happens if a constructor accepts a dependency parameter but never assigns it to the corresponding instance field.
The class compiles without error, since accepting a constructor parameter without using it is syntactically valid Java. The instance field that was meant to hold that dependency remains at its default value, null for any object reference. The application itself may even start successfully, since Spring still successfully resolves and passes in the dependency to the constructor call. The bug only becomes visible the first time any method on that class attempts to actually use the field, at which point a NullPointerException (or equivalent failure) occurs, potentially far removed in time and code location from where the actual mistake was made.

8. Explain what @CreatedDate and @LastModifiedDate require beyond simply being present on a field, and what happens if only one of the two required supporting pieces is added.
Both annotations require two additional pieces of configuration to function: @EntityListeners(AuditingEntityListener.class) on the base entity class, and @EnableJpaAuditing on the application's entry point class. If only @EntityListeners is added but @EnableJpaAuditing is missing, the listener is correctly attached to entity lifecycle events, but JPA's auditing feature itself was never activated application-wide, so the listener has no active auditing infrastructure to actually delegate the timestamp-population work to. The result is that both createdAt and lastModifiedAt remain NULL, with no error or warning raised anywhere, exactly the kind of silent failure mode seen elsewhere in this series with reserved keywords and EnumType.ORDINAL.

9. Why is checklist point 4 (fitting the system's own real constraints) typically the one that catches AI-generated code gaps that the other three points miss?
The first three checklist points, contract matching, convention following, and general edge-case handling, are all things that can be verified simply by reading the generated code in isolation and comparing it against generic good practices. Point 4 requires comparing the generated code against a convention that is specific to this particular codebase's history and design decisions, such as the established habit of validating every foreign key ID via findById().orElseThrow() before using it. A generic AI prompt has no way of inferring this system-specific convention on its own, since it was never stated in the prompt; only a reviewer who already knows the codebase's own established patterns can catch a gap like a missing regionId validation.

10. What real, concrete risk does skipping foreign-key existence validation (as in the AI-generated TheatreService example) introduce into a system?
Building a Region reference directly from a raw regionId without first confirming that ID corresponds to an actual existing row allows a Theatre to be created pointing at a Region that does not exist. Depending on whether the database enforces referential integrity constraints, this either fails at the database level with a foreign key constraint violation (a confusing, low-level error surfacing far from its actual cause), or, if constraints aren't enforced, silently creates a Theatre with a broken, dangling reference that will cause null-pointer-style failures or missing data anywhere that relationship is later navigated.

11. Why does the finished BookMovieRequestDto-to-Booking flow still leave the PENDING-to-CONFIRMED transition unimplemented, and what does this mean for the state of the system at the end of this session?
The scope of this three-lecture BookMyShow arc was deliberately bounded to modeling, the core booking race condition, and user account fundamentals; an actual payment integration, and the logic to move a booking from PENDING to CONFIRMED upon successful payment, was never part of that scope and is explicitly named as work left for independent extension. This means that, as the series ends, every successfully created Booking remains permanently in the PENDING state; no code path in this project currently transitions it further, which is an honestly named limitation rather than an oversight.

12. Summarize the recurring habit demonstrated across all three BookMyShow code lectures (Post-Reads 9, 10, and 11), and explain why it is described as more valuable than knowledge of any specific API.
The recurring habit is: build the obvious version of a solution first, deliberately find exactly where and why it breaks under real conditions, and then fix it using the smallest correct tool available, rather than the most powerful or most complex one. This played out with a status field replacing a full database lock, a salt replacing a plain deterministic hash, and an explicit auditing configuration replacing an assumption that an annotation would "just work." This habit is described as more valuable than familiarity with Spring, JPA, or bcrypt specifically because it transfers directly to any future system or unfamiliar toolset, including Splitwise, the very next system in this course, whereas specific API knowledge only helps within the exact tools it was learned on.

Self-Check Questions
In your own words, explain why the lazy expiry check never writes anything back to the database just because 15 minutes have passed, and describe the exact moment a write does eventually happen for an expired seat.
Trace through: describe a specific sequence of events where a seat gets stuck BLOCKED forever even with today's lazy expiry check correctly in place, and explain what additional mechanism would prevent that outcome.
Write a snippet: implement a scheduled job (using Spring's @Scheduled) that sweeps all ShowSeat rows with showSeatStatus = BLOCKED and blockedAt older than 15 minutes, resetting them to AVAILABLE.
Compare the reused PriceCalculator from Post-Read 10 against the alternative "fetch-all-and-loop" version mentioned in this session. Explain, in your own words, why reuse was the correct choice even though both versions would produce the same final price.
Explain, in your own words, why @Repository and @Service might appear functionally interchangeable in casual testing, but are not actually interchangeable in a real system.
Trace through: describe exactly what state bCryptPasswordEncoder is in, at the moment signUp() is first called, if the constructor accepts the parameter but never assigns it to the field, and what exception (and message) would result.
Write a snippet: implement the /user/login endpoint (LoginRequestDto, LoginResponseDto, and a controller method), calling the existing UserService.login() method, following the same DTO and try/catch pattern already used in signUp().
Compare storing a password with a deterministic hash function versus storing it with bcrypt. Describe a specific attack scenario where the deterministic version fails and the bcrypt version succeeds.
Explain, in your own words, why @EntityListeners(AuditingEntityListener.class) alone is not sufficient for @CreatedDate to populate correctly, tracing exactly what role @EnableJpaAuditing plays that the listener annotation alone cannot provide.
Trace through: if a new entity, Review, were added to this system, list every annotation and configuration step it would need to carry in order for its own createdAt/lastModifiedAt fields to populate automatically, assuming BaseModel is extended correctly.
In your own words, explain why checklist point 4 (fitting the system's own real constraints) is described as requiring different knowledge than points 1 through 3, using the TheatreService example from this session's AI Corner.
Write a short paragraph, in your own words, summarizing the single habit repeated across all three BookMyShow code lectures (obvious version, find where it breaks, fix with the smallest correct tool), and describe one place you'd expect this same habit to apply in Splitwise, the next system in this course.
Further Reading
Post-Read 8, Machine Coding 8: Design BookMyShow - the original source of R10, R11, and every requirement referenced throughout this three-lecture code arc.
Post-Read 9, Machine Coding 9: Code BookMyShow 1 - the source of every entity mapping, the original CLI-runner pattern reused for the signup smoke test, and the original 11 AI-generated repositories.
Post-Read 10, Machine Coding 10: Code BookMyShow 2 - the full derivation of soft locking and Isolation.SERIALIZABLE, directly extended in this document's completed bookMovie() method, and the source of the scheduled-job homework this session's lazy check complements rather than replaces.
Spring Security Official Documentation, Password Storage - the official reference for BCryptPasswordEncoder, encode(), and matches(), directly relevant to Section 5.
Spring Data JPA Official Documentation, Auditing - the official reference for @CreatedDate, @LastModifiedDate, @EntityListeners, and @EnableJpaAuditing, directly relevant to Section 6.
OWASP Password Storage Cheat Sheet - a broader, practical reference on password hashing best practices beyond bcrypt specifically, useful context for why salting and slow hashing algorithms matter in real systems.
Homework
1. Wire up a real /user/login endpoint: LoginRequestDto,
   LoginResponseDto, and a controller method calling
   UserService.login(). Test it against today's signed-up user.

2. Replace every plain RuntimeException in BookingService and
   UserService with real custom exceptions, and add a
   @ControllerAdvice for clean HTTP responses.

3. Build the scheduled-job version of seat expiry alongside
   today's lazy check. Confirm both coexist without conflicting.

4. Using today's TheatreController as a template, build one more
   CRUD stack by hand — adding a new Screen to a Theatre —
   including the "validate the foreign ID exists" convention.

5. Push everything to GitHub — branch: bookmyshow-code-part3-complete

Last changed by 
 
Tushar Harsan·Follow
0
38
Add a comment
Published on  HackMD
