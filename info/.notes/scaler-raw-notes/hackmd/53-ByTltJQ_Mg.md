Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/ByTltJQ_Mg

Post Read : Machine Coding - 9: Code BookMyShow 1
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Aug 31, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 9: Code BookMyShow 1
Introduction

Post-Read 8 finished designing BookMyShow: a complete class diagram (City, Theatre, Screen, Seat, Movie, Show, ShowSeat, ShowSeatType, User, Ticket, Payment), plus a primer on JPA and Spring Boot preparing for exactly this session. This document is where design stops and code starts. Every model gets built in real Java, wired to a real MySQL database through JPA and Hibernate, and one full requirement (R9, listing movies playing in a region) runs end to end against that real database.

Running example: the same BookMyShow system carried from Post-Read 8, now becoming a genuinely running Spring Boot project.
Two names change between the Design lecture and this actual codebase, and both are called out explicitly rather than silently: City becomes Region (a broader area than a single city), and Ticket becomes Booking (the same concept, renamed to an action-based name). From this point forward in the series, Region and Booking are the names used.
This session contains six embedded animations, each narrated in full below at the point where the lecture places it: the ddl-auto schema lifecycle, the JPA/Hibernate mapping pipeline, the many-to-many Booking-ShowSeat relationship over time, the EnumType.STRING vs ORDINAL risk, the full entity relationship graph, and Spring Data's derived query name parsing.
This session also deliberately catches and fixes several real bugs sitting in the lecture's own cue card (a stray self-referencing field on Region, a missing Theatre class body, a missing Payment-to-Booking link, and several missing mappedBy attributes). Each one is treated as a genuine "review someone else's code" moment, not smoothed over.
Only one AI Corner appears today, not two, consistent with how this course treats code lectures differently from design lectures.
Section 1: Quick Recall, Spring Boot and JPA
What It Means
This is a recall, not a re-teaching. JPA, Hibernate, ORM, Spring, and Spring Boot were all taught in full in Post-Read 8, Section 5, and are not redefined here.
The one-line summary carried forward: real persistence is needed for BookMyShow, not in-memory lists. JPA is the tool that maps Java objects to real database tables. Hibernate is the actual implementation doing that work. Spring Boot wires JPA and Hibernate together with almost no manual setup.
If any of those five names (ORM, JPA, Hibernate, Spring, Spring Boot) still feel shaky, the correct move is to revisit Post-Read 8, Section 5, before continuing here, since this document builds directly on top of that foundation without re-deriving it.
Hidden Pitfalls
Treating today's session as a good moment to re-learn what JPA or Hibernate are: that ground was already covered in full in Post-Read 8; spending time relearning definitions here instead of building is the wrong use of this document's focus.
Section 2: Setting Up the Project
What It Means
Today's setup follows the exact same Spring Initializr flow already walked through in Post-Read 8, Section 5.5, just with BookMyShow's real project details instead of a throwaway test project.
Group:        com.scaler
Artifact:     bookmyshowmay23
Package name: com.scaler.bookmyshowmay23
Dependencies: Spring Boot DevTools, Lombok,
              Spring Configuration Processor,
              Spring Data JPA, MySQL Driver

The package name here, com.scaler.bookmyshowmay23, matches the artifact name exactly. Keeping this spelling consistent for the rest of the project matters concretely: a mismatched package name is a real, common source of "why won't my import resolve" confusion.
Of the five dependencies, Spring Data JPA is the one doing the real work described in Post-Read 8: it brings in JPA and Hibernate, pre-wired by Spring Boot. MySQL Driver is what lets that connection specifically talk to MySQL.
Hidden Pitfalls
Letting the package name drift from the artifact name partway through the project: this is a common, avoidable source of unresolved imports; keeping the two in sync from the very first file avoids the problem entirely.
Section 3: Building the Models
What It Means

The same rule from Parking Lot applies here: models come first, before any real logic. Today, models are built in two passes:

Pass 1 (this section): plain classes with Lombok's @Getter @Setter, no ORM or database annotations at all.
Pass 2 (Section 5): the JPA annotations that turn these plain classes into real tables and relationships get added, once each relationship has actually been reasoned about.

@Getter/@Setter and @Entity/@ManyToOne/etc. solve two completely different problems. Lombok's job is only "stop me from hand-writing getters and setters," it has nothing to do with the database. JPA's annotations are the ones that actually talk to Hibernate and MySQL. This is exactly why Lombok gets added to every single class today, from Pass 1 onward, while JPA annotations wait until Section 5.

This distinction has a concrete, compile-breaking consequence worth stating directly: later, ShowService calls show.getMovie().getName(). If Movie or Show doesn't carry its own @Getter, that line will not compile, because BaseModel's @Getter only generates getters for BaseModel's own fields (id, createdAt, lastModifiedAt), not for anything declared on a subclass. So the rule applied without exception in this section is: every model class gets its own @Getter @Setter.

Reconciling Names with the Design Lecture

Two names differ between Post-Read 8's Design lecture and this actual codebase, exactly the kind of naming drift a real engineer runs into constantly when joining an existing project:

Design lecture called it   →   This codebase calls it
------------------------------------------------------
City                       →   Region  (broader than one city)
Ticket                     →   Booking (same concept, action-named)

From this point forward, the codebase's names are adopted, the same discipline followed on a real team joining an existing project rather than fighting its conventions.

Practical Mechanics: BaseModel
package com.scaler.bookmyshowmay23.models;

import lombok.Getter;
import lombok.Setter;
import java.util.Date;

@Getter
@Setter
public class BaseModel {
    private Long id;
    private Date createdAt;
    private Date lastModifiedAt;
}

Every model extends this, the same pattern already established in Parking Lot.

Practical Mechanics: The Rest of the Models, Plain

These are mostly direct translations of Post-Read 8's class diagram into Java. Every class below carries its own @Getter @Setter, for the reason stated above.

@Getter
@Setter
public class Region extends BaseModel {
    private String name;
}

Region has no theatres list yet, even though one Region clearly has many Theatres. This is deliberate, not a mistake: the rule being followed is that a "give me all my children" list only gets declared once a real requirement actually needs that direction of navigation. Section 5 revisits exactly when and how to add it.

@Getter
@Setter
public class Screen extends BaseModel {
    private String name;
    private List<Seat> seats;
    private List<Feature> features;
}

public enum Feature {
    THREE_D, TWO_D, DOLBY, HD, DOLBY_AUDIO,
}

@Getter
@Setter
public class Seat extends BaseModel {
    private String num;
    private SeatType seatType;
    private int rowVal;
    private int colVal;
}

SeatType needs its own real class here, not a Java enum, for the exact reason already established in Post-Read 8: different theatre chains can define their own seat-tier names, GOLD/SILVER/PLATINUM at one theatre, RECLINER/EXECUTIVE at another. A single shared enum cannot hold two different sets of values at once. So SeatType gets a minimal real body today:

@Getter
@Setter
public class SeatType extends BaseModel {
    private String name;   // e.g. "GOLD" — or a theatre's own label
}

@Getter
@Setter
public class User extends BaseModel {
    private String name;
    private String email;
    private List<Booking> bookings;
    private String password;
}

@Getter
@Setter
public class Movie extends BaseModel {
    private String name;
}

Post-Read 8's Movie had cast, genre, languages, and features. This session's codebase keeps Movie to just a name, an honest simplification made to stay buildable in one lecture. Extending it back out to the richer version is homework.

@Getter
@Setter
public class Show extends BaseModel {
    private Movie movie;
    private Date startTime;
    private Date endTime;
    private Screen screen;
    private List<Feature> features;
}

@Getter
@Setter
public class ShowSeat extends BaseModel {
    private Show show;
    private Seat seat;
    private ShowSeatStatus showSeatStatus;
    private Date blockedAt;
}

public enum ShowSeatStatus {
    AVAILABLE, UNAVAILABLE, BOOKED, BLOCKED,
}

Post-Read 8's Design lecture only ever discussed a seat being "booked" or "free." Here, ShowSeatStatus has four states, and it's worth reasoning through why BLOCKED exists as its own state, separate from BOOKED:

BLOCKED is the temporary hold described by R10 in Post-Read 8, a seat someone has selected and is currently paying for, but has not yet confirmed.
BOOKED is the final, paid, confirmed state.
UNAVAILABLE covers a different case entirely: a seat a theatre has switched off for a specific show, for example, a broken seat.

This is R10's "seat held during payment" idea, finally getting a real, concrete status value in code, rather than remaining an abstract requirement.

@Getter
@Setter
public class ShowSeatType extends BaseModel {
    private Show show;
    private SeatType seatType;
    private int price;
}

public enum BookingStatus {
    CONFIRMED, CANCELLED, PENDING,
}

@Getter
@Setter
public class Booking extends BaseModel {
    private BookingStatus bookingStatus;
    private List<ShowSeat> showSeats;
    private User user;
    private Date bookedAt;
    private Show show;
    private int amount;
    private List<Payment> payments;
}

@Getter
@Setter
public class Payment extends BaseModel {
    private String refNo;
    private int amount;
    private PaymentProvider paymentProvider;
    private PaymentStatus paymentStatus;
}

public enum PaymentProvider {
    PAYU, RAZORPAY,
}

public enum PaymentStatus {
    SUCCESS, FAILURE, REFUNDED,
}

Post-Read 8's Payment tracked mode (card versus wallet). This codebase instead tracks which gateway processed the payment (PayU versus Razorpay), a reasonable evolution of the original design, since that is literally what a real checkout screen shows a user ("Redirecting to Razorpay…").

One real gap surfaces here, caught by inspection rather than glossed over: the Theatre class body was never actually shown, even though both Region and Screen depend on it existing. This gets filled in directly:

@Getter
@Setter
public class Theatre extends BaseModel {
    private String name;
    private Region region;
    private List<Screen> screens;
}

Running tally — everything built so far:
BaseModel, Region, Theatre, Screen, Feature(enum), Seat, SeatType,
Movie, Show, ShowSeat, ShowSeatStatus(enum), ShowSeatType,
BookingStatus(enum), Booking, Payment, PaymentProvider(enum),
PaymentStatus(enum), User
= 18 files total (12 real entities + BaseModel + 5 enums)
Every one of the 13 real classes already carries its own
@Getter @Setter — that part won't need revisiting later.

Hidden Pitfalls
Adding a "give me all my children" list before any requirement needs it: Region.theatres is deliberately left off in Pass 1; adding navigation lists speculatively, rather than when a real requirement needs that direction, adds unused complexity and unnecessary coupling.
Forgetting @Getter/@Setter on a subclass, assuming BaseModel's Lombok annotations cover it: BaseModel's @Getter only generates getters for its own fields; every subclass needs its own Lombok annotations, or later calls like show.getMovie() simply will not compile.
Treating a missing class body (like Theatre's) as someone else's problem to fix later: in a real codebase, gaps like this get caught by actually trying to compile and use the code, exactly as demonstrated here, not by assuming everything referenced elsewhere must already exist correctly.
Section 4: Connecting to a Real Database, the Practical Config
What It Means

Eighteen model files now exist as plain Java classes. Checking a natural question directly: if the app started right now and MySQL were inspected, how many real tables would exist?

Zero. Nothing written so far tells the database "this is a real table." They remain plain Java classes with no connection to persistence at all. Closing that gap needs two things: a config file telling Spring how to reach MySQL, and, in Section 5, the @Entity annotations themselves.

Practical Mechanics: application.properties
application.properties

spring.jpa.hibernate.ddl-auto=update
spring.datasource.url=jdbc:mysql://127.0.0.1:3306/bookmyshow?createDatabaseIfNotExist=true
spring.datasource.username=root
spring.datasource.password=password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.show-sql=true

ddl-auto=update means whenever the model classes change, Hibernate updates the real tables to match, with no manual ALTER TABLE needed.
That is not the same as creating the database itself. The bookmyshow schema has to exist before Hibernate can put tables inside it. createDatabaseIfNotExist=true on the URL handles that automatically; without it, CREATE DATABASE bookmyshow; would need to be run manually in MySQL first. Either approach works, skipping both does not.
What the Animation Shows: Hibernate ddl-auto Schema Lifecycle

The animation opens with an empty MySQL database and a plain Java Movie class carrying three fields: id, name, duration. In create mode, it runs an actual CREATE TABLE statement, then flags a clear warning that this mode destroys all existing data on every single restart, a serious risk if ever run against real data. Three rows of movie data get inserted next, representing real information worth keeping, and then a developer adds a brand-new field, rating, to the Movie class. Switching to update mode, Hibernate compares Java's current field list against the database's existing column list, spots that rating is missing, and runs an ALTER TABLE ... ADD COLUMN statement, all three existing rows survive this change intact, simply picking up NULL in the new column. Finally, the animation shows validate mode: Hibernate only checks whether the schema matches what Java expects, and when a genre column turns out to be missing, the application fails to start outright rather than silently modifying anything.

This makes concrete exactly what update does under the hood: it only adds what is missing, and it never drops anything, which is precisely the behavior just described in the application.properties walkthrough above. It also shows the real risk of create (data loss on every restart) and the real safety of validate (failing loudly instead of silently changing a production schema), giving direct context for why update is the practical middle choice used throughout this class.

Answering the paired instructor question directly ("Why would we never want create mode running against a production database?"): because create mode destroys and recreates the schema from scratch every time the application restarts, which means every real row of production data, every booking, every user, every payment, would be permanently deleted the next time the server restarted for any reason, a deployment, a crash recovery, a routine reboot. It is only ever safe for a fresh, disposable development environment.

Hidden Pitfalls
Assuming ddl-auto=update also creates the database schema itself: update only manages tables inside an already-existing database; createDatabaseIfNotExist=true (or a manual CREATE DATABASE) is what actually creates the schema itself.
Running ddl-auto=create or create-drop against any environment holding real data: both modes destroy the entire schema on every restart, an acceptable risk only in a throwaway development setup, never anywhere data needs to persist.
Section 5: Deciding the Mappings
What It Means

Every class becomes a real database table through @Entity. Every relationship between classes needs a cardinality decision, the same rule already applied to Parking Lot's schema, just expressed today as annotations instead of a hand-drawn diagram.

Two annotations always travel together from this point forward, and the difference between them is worth stating precisely: @Entity tells Hibernate "this class is a real database table, manage it." @Id (already present inside BaseModel, arriving properly below) tells Hibernate which specific field is the primary key. Skipping @Entity on any class means Hibernate simply never creates a table for it, the class silently stays a plain Java object, and any repository built on top of it (JpaRepository<Region, Long>, for instance) fails to start up with a "not a managed type" error. @Entity is not optional decoration, it is the one line that actually makes a class a table at all.

What the Animation Shows: JPA / Hibernate ORM Mapping Pipeline

The animation starts with a plain Java Movie class carrying three fields, and walks through exactly what each annotation does to it, one at a time. @Entity and @Table(name="movies") appear first, and the table name "movies" is pulled directly from the annotation to generate a CREATE TABLE movies statement. @Id and @GeneratedValue light up on the id field next, showing Java's Long type turning into SQL's BIGINT PRIMARY KEY AUTO_INCREMENT. @Column(name="title") and @Column(name="duration") then map the remaining two fields to real columns, Java's String becoming VARCHAR(255) and Java's Integer becoming INTEGER, completing the full CREATE TABLE statement. A second phase then shows entityManager.persist(movie) turning into an actual INSERT INTO statement, with the object's real values (id=1, title="Inception", duration=148) flowing directly into the generated SQL.

This makes the abstract idea "annotations become SQL" completely concrete: the exact CREATE TABLE and INSERT statements Hibernate would generate become visible, column by column, rather than staying an abstract claim. It also reinforces directly why @Entity is "the one line that actually makes the class a table at all," since the entire rest of the pipeline shown, table name, primary key, columns, inserts, only happens in the first place because that one annotation exists.

Answering the paired instructor question directly ("If we deleted just the @Entity line here, which of these steps would still happen?"): none of them. Without @Entity, Hibernate never registers Movie as a managed entity at all, so it never generates the CREATE TABLE statement, never processes @Id or @GeneratedValue, never maps any @Column, and entityManager.persist(movie) would fail outright rather than producing an INSERT. Every subsequent step in the pipeline depends entirely on @Entity having registered the class first.

Practical Mechanics: BaseModel Gets Its ID
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.util.Date;

@Getter
@Setter
@MappedSuperclass
public class BaseModel {
    @Id
    private Long id;

    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Temporal(TemporalType.TIMESTAMP)
    private Date lastModifiedAt;
}

@MappedSuperclass tells Hibernate that every class extending this one carries these columns too, but that BaseModel itself is not a table of its own.
@Temporal(TemporalType.TIMESTAMP) appears on both date fields because Java's plain Date type is ambiguous to JPA on its own, it does not know whether a calendar date, a clock time, or a full date-and-time stamp is intended. @Temporal spells that out explicitly. TIMESTAMP is used everywhere in this session since both the date and the time matter for every use case here (when a show starts, when a seat got blocked, when a booking happened). Skipping this is not merely sloppy, depending on the Hibernate version in use, it can throw a mapping error outright at startup, so it is treated as required on every Date field written from here forward.
A practical note on imports: a Spring Boot 3.x project uses jakarta.persistence.*; a Spring Boot 2.x project uses javax.persistence.* instead. Whichever Spring Initializr actually generated needs to be used consistently, mixing the two will not compile.
The Rule Applied All Section: Pair Every "Many" with Its "One"

A small mistake is easy to make here, and it quietly creates an extra, unwanted table if not caught. Consider writing two facts separately: on Screen, "I have many seats," and on Seat, "I belong to one screen." These two statements are, to a human, obviously describing the same single relationship. Hibernate does not know that on its own.

Nothing has actually told Hibernate these two lines are connected, so Hibernate may treat them as two completely separate relationships. If it does, it ends up creating two things instead of one: the normal foreign key column for "belongs to one screen," plus an entire second, extra table just to track "has many seats." Only one simple connection between Screen and Seat was ever wanted; without fixing this, two accidentally exist.

The fix is one small addition:

// On Seat — this side holds the actual foreign key.
@ManyToOne
private Screen screen;

// On Screen — this side just says "look at the field
// called 'screen' over on Seat. That's the same
// relationship. Don't create anything new for me."
@OneToMany(mappedBy = "screen")
private List<Seat> seats;

The string inside the brackets, "screen", is simply the exact name of the field written on Seat. That is the entire fix. It tells Hibernate: this list is not a new relationship, it is only the other side of the relationship that already exists. The end result is one single column, screen_id, sitting on the seat table, with no second table created by accident. This exact pattern, one side gets @ManyToOne, the other gets @OneToMany(mappedBy = "...") naming the first side's field, repeats through the rest of this session and does not need re-explaining once recognized.

Practical Mechanics: Region and Theatre, Fixing a Real Bug

A real bug surfaces here worth catching explicitly: an early draft of Region had a strange field sitting on it, @ManyToOne private String region;, a Region referencing itself, as a plain String. That is not a real relationship at all, it is almost certainly a copy-paste leftover that actually belongs on Theatre, exactly where a "belongs to one Region" field should live.

@Getter
@Setter
@Entity
public class Region extends BaseModel {
    private String name;

    @OneToMany(mappedBy = "region")
    private List<Theatre> theatres;
}

@Getter
@Setter
@Entity
public class Theatre extends BaseModel {
    private String name;

    @ManyToOne
    private Region region;

    @OneToMany(mappedBy = "theatre")
    private List<Screen> screens;
}

@Entity here does exactly what was described earlier: it is the line that turns Region and Theatre into real tables the moment the application starts.

Practical Mechanics: Screen and Seat
@Getter
@Setter
@Entity
public class Screen extends BaseModel {
    private String name;

    @ManyToOne
    private Theatre theatre;

    @OneToMany(mappedBy = "screen")
    private List<Seat> seats;
    // features handled in Section 6
}

@Getter
@Setter
@Entity
public class Seat extends BaseModel {
    private String num;
    private int rowVal;
    private int colVal;

    @ManyToOne
    private Screen screen;
}

Considering Seat.seatType directly: Screen 3 has 40 GOLD seats, 30 SILVER seats, and 10 PLATINUM seats, all sharing just three actual SeatType rows. Given the same "many things share one shared row" shape already applied to Theatre and Region, the correct annotation is @ManyToOne: many Seat rows all point to the same one SeatType row (all 40 GOLD seats point to the same "GOLD" row), the same shape as many Theatres pointing to one shared Region.

@Getter
@Setter
@Entity
public class Seat extends BaseModel {
    private String num;
    private int rowVal;
    private int colVal;

    @ManyToOne
    private Screen screen;

    @ManyToOne
    private SeatType seatType;
}

SeatType itself only needs @Entity. It does not need a back-reference list to Seat or ShowSeatType, because nothing built in this session ever needs to ask "give me every seat of this type." This is the same rule already applied to Region at the very start: only add the "many" side of a relationship when a real requirement needs that direction of navigation.

@Getter
@Setter
@Entity
public class SeatType extends BaseModel {
    private String name;
}

Quiz Recap

ShowSeatType also has a seatType field, pointing to the same shared SeatType class. Suppose a theatre admin renames their "GOLD" SeatType row to "Premium Gold." How many rows actually need to be updated for every Seat and every ShowSeatType that uses GOLD to now show the new name?

A) Every affected Seat row and every affected ShowSeatType row, since each one stores its own copy of the type name
B) Just ONE row, the shared SeatType row itself, since every Seat and ShowSeatType only holds a foreign key pointing to it, not a copy of the name
C) Two rows, one in seat_type, and one cached copy on seat, since Seat also stores the name directly for faster reads
D) None, SeatType names are effectively enum values once created, so renaming isn't possible without a schema migration
Correct answer: B. This is the exact same payoff already seen with ShowSeatType and price back in the Design lecture: because Seat and ShowSeatType both reference SeatType through a foreign key rather than storing a copy of its name, changing the one shared row instantly reflects everywhere that row is referenced.
Why A is wrong: it assumes data got duplicated somewhere, it did not, because SeatType was deliberately given its own table instead of being allowed to remain a plain enum with copied values.
Why C is wrong: it invents a caching mechanism that was never built; Seat never stores a copy of the type name directly.
Why D is wrong: it confuses SeatType, a real, editable database entity, with a fixed Java enum, which is precisely the thing this design deliberately rejected SeatType becoming.
Practical Mechanics: Booking and ShowSeat, the Genuinely Tricky One

The relationship between Booking and ShowSeat needs real thought. One booking clearly covers many seats, up to 10, per R10 from Post-Read 8. The harder direction: can one ShowSeat ever be linked to more than one Booking?

Reasoning it through: at any single moment, a ShowSeat should only have one active booking. But over time, a booking can get cancelled and refunded, and someone else can then book that same seat for that same show later. So across time, the same ShowSeat really can end up linked to more than one Booking.

This is a genuinely important distinction worth stating precisely: a schema's cardinality describes what CAN be linked structurally over time. It is not the same as what is allowed to be true right now, that is a business rule, enforced by BookingStatus and ShowSeatStatus at the application level, not by the schema itself.

@Getter
@Setter
@Entity
public class Booking extends BaseModel {
    @Enumerated(EnumType.STRING)
    private BookingStatus bookingStatus;

    @ManyToMany
    private List<ShowSeat> showSeats;

    @ManyToOne
    private User user;

    @Temporal(TemporalType.TIMESTAMP)
    private Date bookedAt;

    @ManyToOne
    private Show show;

    private int amount;

    @OneToMany(mappedBy = "booking")
    private List<Payment> payments;
}

What the Animation Shows: Many-to-Many Booking · ShowSeat Over Time

The animation starts with ShowSeat A1 for the 7 PM show, and an empty booking_show_seat mapping table, zero rows, zero active bookings. User A books Seat A1, and a new row (id=1) gets inserted into booking_show_seat with status CONFIRMED, the counter reading "1 active booking, 1 total row." User A's booking then gets cancelled and refunded, and row id=1 is updated, not deleted, to status CANCELLED, the counter changing to "0 active bookings, but 1 total row," and the seat becomes available again. User B then books that same Seat A1 for that same 7 PM show, and a brand-new row (id=2) gets inserted with status CONFIRMED. The final state shows two total rows in booking_show_seat for this one ShowSeat, but only one of them active, visually proving the "many-to-many over time" pattern described above.

This makes the abstract distinction between schema cardinality and business rule concrete, by actually watching rows persist through a cancellation instead of disappearing. It directly sets up the quiz that follows by showing exactly what the mapping table looks like at each step of the User A cancels, User B books scenario.

Answering the paired instructor question directly ("If we'd used a plain one-to-one link instead of many-to-many here, what would have happened to row id=1 the moment User B booked the seat?"): a one-to-one link would only allow a single Booking reference to exist for that ShowSeat at the schema level, so User B's booking would have had to either overwrite row id=1's link entirely (destroying the historical record that User A ever booked and cancelled that seat) or fail outright, since a genuinely one-to-one relationship cannot hold two separate booking references, past and present, for the same seat at once. The many-to-many design is exactly what allows the historical row to remain intact while a new, independent row gets created for User B.

Practical Mechanics: EnumType.STRING vs ORDINAL

@Enumerated(EnumType.STRING) appears on every status field in this session, and it is worth naming what it actually does: it tells Hibernate to store the enum's name, "CONFIRMED", "CANCELLED", as text in the column, rather than its position number. The alternative, EnumType.ORDINAL, stores 0, 1, 2, and so on instead. That looks harmless until someone adds a new status in the middle of the enum, or reorders it, months later; every existing row silently starts pointing at the wrong status, with no error anywhere. STRING costs a few extra bytes per row and is completely immune to that failure mode, which is why it is the one actually used in a real system.

What the Animation Shows: EnumType.STRING vs ORDINAL Risk

The animation reads Bob's booking status back from the database using ORDINAL mode, where the stored value is simply the number 1. With ORDINAL, JPA maps that stored 1 to PENDING instead of the CANCELLED status Bob's booking actually had, flagged directly as silent data corruption, with no error or exception thrown anywhere in the process. Side by side, the STRING version reads back the literal text "CANCELLED", which maps correctly every time, regardless of how the enum's internal ordering may have changed since the row was written. A closing lesson banner reinforces the rule directly: always use EnumType.STRING to avoid this exact failure mode.

This makes the abstract warning about ORDINAL fully concrete by showing an actual wrong status appearing with zero errors, the scariest part of this particular bug being that nothing about it looks broken at all. It cements exactly why every status field in this session's codebase (BookingStatus, ShowSeatStatus, PaymentStatus, PaymentProvider) uses @Enumerated(EnumType.STRING) without exception.

Answering the paired instructor question directly ("What would it take for us to even notice this bug happened, if no exception is ever thrown?"): since ORDINAL corruption produces no error, no crash, and no log entry, catching it requires either a manual data audit (comparing what a status field says against what business logic or a user report says actually happened), a deliberate test that specifically adds a new enum constant mid-list and checks whether existing rows still map correctly, or noticing downstream symptoms, like a cancelled booking's seat never actually freeing up because the system now reads its status as something other than CANCELLED. None of these are automatic; the bug can persist silently for a long time before anyone notices.

Quiz Recap

User A books seat A1 for the 7 PM show. That booking is later CANCELLED and refunded. User B then successfully books that same seat A1, for that same 7 PM show. How many rows now exist in the booking_show_seat mapping table referencing that one ShowSeat?

A) Zero, cancelling a booking deletes its row from the mapping table
B) One, User B's booking overwrites User A's row, since a seat can only have one active booking
C) Two, one row per booking that ever referenced this ShowSeat, since Booking:ShowSeat is genuinely many-to-many over time
D) The schema doesn't allow this at all, ShowSeatStatus already blocks any booking after a cancellation
Correct answer: C. This is exactly why many-to-many was chosen. Cancelling a booking does not delete its historical row, it only changes BookingStatus to CANCELLED. A fresh booking for the same seat creates a brand-new row.
Why A is wrong: it assumes cancellation deletes data; it does not, it only updates the existing row's status, preserving the historical record.
Why B is wrong: it assumes rows get overwritten; a many-to-many relationship does not overwrite existing rows when a new link is created, it adds a new one alongside the old.
Why D is wrong: it confuses a business rule ("only one ACTIVE booking allowed right now," enforced by status checks in the Service layer) with a schema-level restriction; the schema itself never blocks the second row from existing at all.
Practical Mechanics: Movie, Show, ShowSeat, ShowSeatType, User
@Getter
@Setter
@Entity
public class Movie extends BaseModel {
    private String name;
}

@Getter
@Setter
@Entity
public class Show extends BaseModel {
    @ManyToOne
    private Movie movie;

    @Temporal(TemporalType.TIMESTAMP)
    private Date startTime;

    @Temporal(TemporalType.TIMESTAMP)
    private Date endTime;

    @ManyToOne
    private Screen screen;
    // features handled in Section 6
}

@Getter
@Setter
@Entity
public class ShowSeat extends BaseModel {
    @ManyToOne
    private Show show;

    @ManyToOne
    private Seat seat;

    @Enumerated(EnumType.STRING)
    private ShowSeatStatus showSeatStatus;

    @Temporal(TemporalType.TIMESTAMP)
    private Date blockedAt;
}

@Getter
@Setter
@Entity
public class ShowSeatType extends BaseModel {
    @ManyToOne
    private Show show;

    @ManyToOne
    private SeatType seatType;

    private int price;
}

@Getter
@Setter
@Entity
public class User extends BaseModel {
    private String name;
    private String email;
    private String password;

    @OneToMany(mappedBy = "user")
    private List<Booking> bookings;
}

A second real gap surfaces here: Payment never actually linked back to Booking, even though Booking.payments already expects that link to exist. This gets added directly:

@Getter
@Setter
@Entity
public class Payment extends BaseModel {
    private String refNo;
    private int amount;

    @Enumerated(EnumType.STRING)
    private PaymentProvider paymentProvider;

    @Enumerated(EnumType.STRING)
    private PaymentStatus paymentStatus;

    @ManyToOne
    private Booking booking;
}

What the Animation Shows: Entity Relationship Graph, BookMyShow Schema

The animation displays every entity just annotated, Region, Theatre, Screen, Seat, SeatType, Movie, Show, ShowSeat, ShowSeatType, Booking, Payment, User, as nodes in one connected graph. It draws a line between every pair of entities that reference each other, matching exactly the @ManyToOne/@OneToMany(mappedBy = ...) pairs just written: Region↔Theatre, Theatre↔Screen, Screen↔Seat, Seat↔SeatType, Booking↔ShowSeat, Booking↔Payment, Booking↔User, and so on across the full schema. This lets the entire shape of the schema be seen at once, which entities sit at the "center" with many connections (Show, Booking) versus which sit at the edges with few (SeatType, Payment).

This gives one consolidated, birds-eye view of every mapping decision made across the whole of this section, instead of only ever seeing one relationship in isolation at a time. It makes it easy to sanity-check for accidental gaps or duplicate relationships, exactly the kind of mistake (a missing mappedBy, a stray field) this section spent real time catching by hand.

Answering the paired instructor question directly ("Trace, with your eyes only, the full path from User to Region through the graph, and name every entity the path passes through"): the path runs User → Booking → Show → Screen → Theatre → Region. User connects to Booking (one user has many bookings), Booking connects to Show (each booking is for one show), Show connects to Screen (each show runs on one screen), Screen connects to Theatre (each screen belongs to one theatre), and Theatre connects to Region (each theatre belongs to one region). This is the exact same chain of hops later written out as a single derived query method name in Section 8.

Hidden Pitfalls
Writing @ManyToOne and @OneToMany on two sides of the same relationship without mappedBy: without mappedBy, Hibernate treats the two declarations as unrelated, silently creating an extra join table instead of the single foreign key column that was actually intended.
Leaving a stray, incorrectly-typed field on the wrong class: the @ManyToOne private String region; bug on Region is exactly this kind of mistake, a copy-paste leftover that both uses the wrong type (String instead of a real entity reference) and sits on the wrong class entirely.
Assuming a class referenced by other classes must already have its own body written correctly: Theatre was referenced by both Region and Screen before its own class body had ever actually been shown; catching this required actually checking, not assuming.
Forgetting to link a class back to the class that expects a reference to it: Booking.payments expected a Payment.booking field to exist; without it, mappedBy = "booking" on Booking.payments would fail to find a matching field on Payment at all.
Confusing schema cardinality with a business rule: Booking and ShowSeat are many-to-many at the schema level because that reflects everything that can ever be true across time; whether only one booking may be active at once is enforced separately, by status fields and Service-layer logic, not by the schema's cardinality.
Using EnumType.ORDINAL instead of EnumType.STRING: ORDINAL stores a fragile position number that silently breaks the moment an enum's constants are reordered or a new constant is inserted mid-list, with no error raised anywhere when it happens.
Section 6: Handling Enums
What It Means

The single-enum pattern has already been used several times in Section 5, and is worth naming explicitly here:

@Enumerated(EnumType.STRING)
private PaymentProvider paymentProvider;

@Enumerated(EnumType.STRING)
private PaymentStatus paymentStatus;

A list of enums needs one additional annotation on top of this: @ElementCollection. Two fields in this model need exactly this treatment: Screen.features and Show.features.

Practical Mechanics
@Getter
@Setter
@Entity
public class Screen extends BaseModel {
    private String name;

    @ManyToOne
    private Theatre theatre;

    @OneToMany(mappedBy = "screen")
    private List<Seat> seats;

    @ElementCollection
    @Enumerated(EnumType.STRING)
    private List<Feature> features;
}

@Getter
@Setter
@Entity
public class Show extends BaseModel {
    @ManyToOne
    private Movie movie;

    @Temporal(TemporalType.TIMESTAMP)
    private Date startTime;

    @Temporal(TemporalType.TIMESTAMP)
    private Date endTime;

    @ManyToOne
    private Screen screen;

    @ElementCollection
    @Enumerated(EnumType.STRING)
    private List<Feature> features;
}

Both Screen and Show get their own separate features list deliberately, not just Screen. This is the exact capability-versus-snapshot pattern already established in Post-Read 8: a screen might physically support 3D and Dolby, but a specific 6 PM showing of a movie might only actually be running in 2D that day. Screen.features describes capability; Show.features describes what is actually turned on for that particular show. These are two different questions, and they need two different lists.

A reconciliation worth flagging directly: it might feel natural to instinctively reach for @ManyToMany on a list like this, since many screens (or shows) can share the same feature value. But Feature is a plain enum, not a full entity with its own table, @ManyToMany is for relating two real entities to each other. For a list of plain values like this, @ElementCollection is correct; it quietly creates a small support table behind the scenes (screen_feature, show_features), not a real join between two entity tables.

Hidden Pitfalls
Reaching for @ManyToMany for a list of enum values: @ManyToMany is for relationships between two real entities, each with their own table; a plain enum has no table of its own, and @ElementCollection with @Enumerated is the correct tool for a list of enum values.
Giving Show the same features reference as its Screen instead of its own independent list: this would collapse the capability-versus-snapshot distinction entirely, making it impossible to represent a show running in 2D on a screen that is physically capable of 3D.
Section 7: Deciding the ID Strategy
What It Means
@Getter
@Setter
@MappedSuperclass
public class BaseModel {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Temporal(TemporalType.TIMESTAMP)
    private Date lastModifiedAt;
}

GenerationType.IDENTITY means the database itself increments the ID by one on every insert; IDs are never assigned manually in application code.

This is a natural moment to actually start the application and check MySQL directly, effectively today's schema verification step, done by inspection instead of a hand-drawn diagram. All 12 entity tables should appear, plus the screen_feature, show_features, and booking_show_seat support tables created automatically by the @ElementCollection and @ManyToMany mappings from earlier sections. If any table is missing, the fastest thing to check is whether that specific class is missing @Entity.

Hidden Pitfalls
Assigning IDs manually anywhere in application code when using GenerationType.IDENTITY: the database is solely responsible for generating IDs under this strategy; manually setting an ID value before an insert can conflict with the database's own auto-increment counter.
Assuming a missing table means a bug in the relationship annotations rather than a missing @Entity: the single most common cause of a missing table, as demonstrated repeatedly in Section 5, is simply forgetting @Entity on that specific class, checked first before investigating anything more complex.
Section 8: Repositories and AI Corner
What It Means

A way to actually save and fetch each entity is still needed. With Spring Data JPA, this is close to trivial:

public interface MovieRepository extends JpaRepository<Movie, Long> {}

That single line is enough. Spring Data generates save(), findById(), findAll(), and more, entirely for free. This only works because Movie is a real @Entity; a bare JpaRepository<SomePlainClass, Long> where SomePlainClass is not annotated @Entity fails at startup, exactly the trap Section 5 spent real effort avoiding.

Practical Mechanics: Generating Repositories with AI

Eleven real entities need this exact same one-line treatment. Since this is mechanical, well-understood work, repeating the same line 11 times with different names, it is a reasonable task to hand to AI.

Prompt used:

"Generate Spring Data JPA repository interfaces for these 11
entities: Region, Theatre, Screen, Seat, SeatType, Movie, Show,
ShowSeat, ShowSeatType, Booking, Payment, User. Each should
extend JpaRepository<EntityName, Long>, package
com.scaler.bookmyshowmay23.repositories."

A plausible AI response:

public interface RegionRepository extends JpaRepository<Region, Long> {}
public interface TheatreRepository extends JpaRepository<Theatre, Long> {}
public interface ScreenRepository extends JpaRepository<Screen, Long> {}
public interface SeatRepository extends JpaRepository<Seat, Long> {}
public interface SeatTypeRepository extends JpaRepository<SeatType, Long> {}
public interface MovieRepository extends JpaRepository<Movie, Long> {}
public interface ShowRepository extends JpaRepository<Show, Long> {}
public interface ShowSeatRepository extends JpaRepository<ShowSeat, Long> {}
public interface ShowSeatTypeRepository extends JpaRepository<ShowSeatType, Long> {}
public interface BookingRepository extends JpaRepository<Booking, Long> {}
public interface PaymentRepository extends JpaRepository<Payment, Long> {}
public interface UserRepository extends JpaRepository<User, Long> {}

The same checklist applied at every AI Corner in this course gets applied here:

1. Match the contract?      — Yes, all extend JpaRepository<T, Long>,
                               matching BaseModel's Long id.
2. Follow our conventions?  — Yes, naming and package match.
3. Handle edge cases?       — Check: did it generate all 11, and
                               did it use Long consistently for every
                               one (not Integer or String)?
4. Fit OUR real requirement?

Point 4 is where this actually gets interesting. One real requirement is about to be built: listing movies playing in a given Region. Checking directly whether a plain ShowRepository extends JpaRepository<Show, Long> {}, with nothing else added, actually supports that query: it does not. A bare JpaRepository only provides basic save, find-by-id, and find-all operations. It has no way to filter shows down to "only the ones in this Region." A custom method needs to be added by hand.

This is exactly the gap point 4 exists to catch. AI's answer is completely correct in general, but it has no way to know about this system's specific requirement, so it cannot anticipate it. The one method actually needed gets added directly:

public interface ShowRepository extends JpaRepository<Show, Long> {
    List<Show> findByScreen_Theatre_Region_Name(String regionName);
}

This one line walks Show → Screen → Theatre → Region → name and writes the entire SQL join automatically. The underscores matter precisely: Spring Data reads this method name by walking actual field names on each entity, Show.screen, then Screen.theatre, then Theatre.region, then Region.name. Every one of those has to be the exact field name written back in Section 5, or this silently fails to match at startup with a "no property found" error. This is exactly what JPA and Hibernate exist to do, write complex SQL behind the scenes from a method name alone, but only if that method name is spelled correctly against the real fields.

What the Animation Shows: Spring Data, Derived Query Name Parsing

The animation starts with the full method name findByScreen_Theatre_Region_Name(String regionName), breaking it into segments one at a time. findBy lights up first, labeled as the query keyword telling Spring "this is a SELECT." Screen lights up next, with an arrow showing Spring traversing into Show.screen and adding a JOIN screen to the generated query. Theatre lights up after that, showing the hop from Screen.theatre, adding a second JOIN; then Region lights up, showing the hop from Theatre.region, adding a third JOIN, building the full chain Show → Screen → Theatre → Region piece by piece. Finally Name lights up with no further underscore following it, marked as the terminal property, Region.name, which becomes the WHERE condition tied to the regionName parameter, completing a four-table JOIN query built entirely from the method's name alone.

This turns the underscore-heavy method name into something visibly traceable, each underscore corresponds to one real entity hop, not just an arbitrary naming convention. It also reinforces exactly why field-name spelling matters: each segment in the animation matches a real field name on a real entity, which is the mechanism directly behind the "no property found" startup error described above.

Answering the paired instructor question directly ("If Theatre's field on Screen had been named venue instead of theatre, which segment of this method name would need to change?"): the second segment, Theatre, would need to change to Venue, since Spring Data parses that segment by looking for a field literally named theatre on the Screen entity; if that field were instead named venue, the method would need to read findByScreen_Venue_Region_Name to correctly match the real field name, or it would fail with a "no property found" error at startup.

Same rule, every AI Corner: generate fast, but the judgement
calls are yours — especially checking against the REAL
requirement of YOUR system, not a generic version of the problem.

Hidden Pitfalls
Trusting a mechanically-generated set of repositories without checking against the actual requirement about to be built: all 11 AI-generated repositories were structurally correct, but none of them, on their own, could satisfy R9's need to filter shows by region; only checking against the real requirement surfaced the gap.
Misspelling a segment of a derived query method name relative to the actual field name on the entity: Spring Data's derived query parsing depends entirely on exact field-name matching; any mismatch fails silently until startup, producing a "no property found" error rather than a compile-time warning.
Section 9: Coding One Requirement, R9, with CLI Input
What It Means

One requirement gets picked and built fully, end to end, the same discipline already followed for Parking Lot. The requirement chosen is R9 from Post-Read 8: "BMS lists down all the movies running in a city, and for each movie there can be multiple shows."

Post-Read 8 already established that R9 is not a new field on any class, it is a query across the hierarchy, grouped by movie. That reasoning becomes real code here.

Practical Mechanics: ShowService
@Service
public class ShowService {
    private final ShowRepository showRepository;

    public ShowService(ShowRepository showRepository) {
        this.showRepository = showRepository;
    }

    public Map<String, Long> listMoviesPlayingInRegion(String regionName) {
        List<Show> shows = showRepository.findByScreen_Theatre_Region_Name(regionName);

        return shows.stream()
                .collect(Collectors.groupingBy(
                        show -> show.getMovie().getName(),
                        Collectors.counting()));
    }
}

This line only compiles because Show and Movie both carry their own @Getter, established back in Section 3: show.getMovie() and .getName() are both Lombok-generated. This is the direct payoff of the "every class gets its own @Getter @Setter" rule established earlier: without it, this exact line would fail to compile.

Grouping by movie name and counting, rather than simply returning the raw list of shows, is deliberate: that is what R9 actually asked for, a clean list of movies (with how many shows each has), not a messy list of individual show times. The grouping is the entire point of the requirement, not an extra step layered on top of it.

Practical Mechanics: CommandLineRunner

Spring Boot's idiomatic way to run something at startup is CommandLineRunner:

@Component
public class BookMyShowCliRunner implements CommandLineRunner {
    private final ShowService showService;

    public BookMyShowCliRunner(ShowService showService) {
        this.showService = showService;
    }

    @Override
    public void run(String... args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Enter a region name to see movies playing there:");
        String regionName = scanner.nextLine();

        Map<String, Long> movieShowCounts = showService.listMoviesPlayingInRegion(regionName);

        if (movieShowCounts.isEmpty()) {
            System.out.println("No movies found playing in " + regionName);
        } else {
            movieShowCounts.forEach((movie, count) ->
                    System.out.println(movie + " — " + count + " show(s)"));
        }
    }
}

An honest MVP note: this skips the Controller/DTO layer entirely for now, going straight from CLI input to Service. That layering returns properly once real REST endpoints get built, in the next Code lecture. This is not a silent cut, it is today's deliberately named scope.

Hidden Pitfalls
Returning the raw list of shows instead of grouping by movie: R9 specifically asks for a list of movies, not individual shows; skipping the grouping step technically returns data but fails to actually satisfy the requirement as stated.
Assuming skipping the Controller/DTO layer today is a permanent architectural decision: it is explicitly a temporary MVP simplification, named as homework for the next Code lecture, not a conclusion that this system doesn't need that layer at all.
Common Pitfalls Summary
1. Letting the package name drift from the artifact name
   partway through the project.
   -> A common, avoidable source of unresolved imports; keep
      the two in sync from the first file onward.

2. Forgetting a subclass's own @Getter/@Setter, assuming
   BaseModel's Lombok annotations cover it.
   -> BaseModel's @Getter only generates getters for its own
      fields; every subclass needs its own annotations, or
      calls like show.getMovie() won't compile.

3. Adding a "give me all my children" navigation list before
   any real requirement needs it.
   -> Adds unused complexity; only add the "many" side of a
      relationship when an actual requirement needs it.

4. Assuming ddl-auto=update also creates the database schema
   itself.
   -> update only manages tables inside an already-existing
      database; createDatabaseIfNotExist=true (or a manual
      CREATE DATABASE) is what creates the schema.

5. Running ddl-auto=create or create-drop against any
   environment holding real data.
   -> Both modes destroy and recreate the schema on every
      restart, acceptable only in disposable dev environments.

6. Writing @ManyToOne and @OneToMany on two sides of the same
   relationship without mappedBy.
   -> Hibernate treats the two declarations as unrelated,
      silently creating an extra join table instead of one
      foreign key column.

7. Leaving a stray, incorrectly-typed field on the wrong class
   (like Region's self-referencing String field).
   -> A real copy-paste-style bug; caught only by actually
      reviewing the code, not by assuming it's correct.

8. Assuming a class referenced elsewhere must already have its
   own body written correctly.
   -> Theatre was referenced by Region and Screen before its
      own class body existed; this needs active checking.

9. Forgetting to link a class back to the class that expects a
   reference to it (Payment never linking to Booking).
   -> mappedBy on the other side fails to find a matching field
      if the reverse reference is never actually added.

10. Confusing schema cardinality with a business rule.
    -> Booking:ShowSeat is many-to-many at the schema level
       (what CAN be linked over time); "only one active booking
       right now" is a business rule enforced by status fields.

11. Using EnumType.ORDINAL instead of EnumType.STRING.
    -> ORDINAL stores a fragile position number that silently
       breaks the moment an enum's constants are reordered or a
       new one is inserted mid-list, with no error raised.

12. Reaching for @ManyToMany for a list of enum values.
    -> @ManyToMany is for relationships between two real
       entities; @ElementCollection with @Enumerated is correct
       for a list of plain enum values.

13. Trusting AI-generated repositories without checking them
    against the actual requirement about to be built.
    -> All 11 generated repositories were structurally correct,
       but none could satisfy R9 without a hand-added custom
       query method.

14. Misspelling a segment of a derived query method name
    relative to the real field name on the entity.
    -> Fails silently until startup with a "no property found"
       error, since Spring Data matches method segments to exact
       field names.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Assuming a codebase inherited from someone else (or from a prior lecture's cue card) is correct by default: this entire session modeled the opposite habit, catching a stray field, a missing class body, and a missing back-reference by actually reasoning through the code rather than assuming it was already right; this is a normal, valuable part of real engineering work, not a sign something went wrong with the lecture itself.
Treating annotation-driven mapping as "automatic" in a way that removes the need for the same cardinality reasoning used in schema design: every @ManyToOne/@OneToMany decision in this session required the exact same one-to-many, many-to-many reasoning already practiced with hand-drawn schema diagrams in Parking Lot; annotations changed the notation, not the underlying thinking required.
Key Terminology
Term	Meaning in Simple Words
@MappedSuperclass	A JPA annotation marking a class (like BaseModel) as not being its own database table, but whose fields get inherited as real columns by every subclass that extends it.
@Temporal(TemporalType.TIMESTAMP)	A JPA annotation clarifying that a Java Date field should be stored as a full date-and-time value in the database, resolving an ambiguity Java's Date type has on its own.
mappedBy	An attribute on @OneToMany that tells Hibernate a given list is the reverse side of a relationship already defined elsewhere (via @ManyToOne), preventing Hibernate from creating a duplicate, unwanted extra table for the same relationship.
@ElementCollection	A JPA annotation for mapping a list of plain values (such as a list of enum constants) into a small supporting table, used when the list items are not full entities with their own table.
@Enumerated(EnumType.STRING)	A JPA annotation telling Hibernate to store an enum's name as text in the database, rather than its numeric position, protecting against silent corruption if the enum's constants are later reordered.
GenerationType.IDENTITY	An ID generation strategy where the database itself auto-increments the primary key on every insert, rather than the application assigning IDs manually.
Derived Query Method	A Spring Data JPA repository method whose name (like findByScreen_Theatre_Region_Name) is automatically parsed into a real SQL query by matching each segment of the name to a real field on the entity, without any manual query code.
CommandLineRunner	A Spring Boot interface whose run() method executes automatically once the application starts, commonly used to accept simple command-line input for testing a feature end to end.

JPA, Hibernate, ORM, Spring, Spring Boot, @Entity, @Id, Maven, Spring Initializr, and the Repository/Service/Controller layering were already defined in Post-Read 8 and earlier post-reads in this series and are not redefined here.

Frequently Asked Interview Questions

1. Why does every model class in this codebase need its own @Getter/@Setter, rather than relying on BaseModel's Lombok annotations?
Lombok's @Getter/@Setter generates accessor methods only for the fields declared directly on the class carrying the annotation. BaseModel's @Getter generates getters only for BaseModel's own fields (id, createdAt, lastModifiedAt). A subclass like Movie, which declares its own field name, needs its own @Getter to generate getName(); without it, code elsewhere calling movie.getName() would fail to compile, since no such method would ever be generated.

2. Explain the purpose of mappedBy in a @OneToMany annotation, using Screen and Seat as the example.
Without mappedBy, declaring @ManyToOne private Screen screen; on Seat and @OneToMany private List<Seat> seats; on Screen gives Hibernate no information that these two declarations describe the same relationship. Left unresolved, Hibernate creates two separate structures: the expected foreign key column on seat, plus an entirely unnecessary extra join table for the @OneToMany side. Adding mappedBy = "screen" on Screen.seats tells Hibernate to treat that list as simply the reverse view of the relationship already owned by Seat.screen, resulting in exactly one foreign key column (screen_id) and no extra table.

3. Why is SeatType modeled as its own @Entity rather than a Java enum, and what concrete benefit does this design choice provide when a seat type gets renamed?
Different theatre chains can define their own seat-tier names (GOLD/SILVER/PLATINUM at one theatre, RECLINER/EXECUTIVE at another), which a single shared Java enum cannot represent, since an enum has one fixed set of values for the entire application. Because Seat and ShowSeatType both reference SeatType through a foreign key rather than storing a copy of its name, renaming a SeatType row (say, "GOLD" to "Premium Gold") requires updating exactly one row, the shared SeatType row itself, and that change is instantly reflected everywhere it is referenced, with zero duplicated data to fix.

4. Why is the relationship between Booking and ShowSeat modeled as @ManyToMany, even though only one booking should ever be "active" for a given seat and show at once?
Schema cardinality describes what can structurally be linked over time, not what is allowed to be true at any single moment. A ShowSeat can be linked to multiple Booking records across its history: an initial booking, followed by a cancellation, followed by a completely separate booking by a different user later. @ManyToMany correctly models this full history. The constraint that only one of those bookings should be considered active at a time is a business rule, enforced through BookingStatus and ShowSeatStatus checks in the Service layer, not something the schema's cardinality itself is responsible for enforcing.

5. What actually breaks if a Booking-to-ShowSeat cancellation-and-rebooking scenario is modeled with EnumType.ORDINAL instead of EnumType.STRING?
EnumType.ORDINAL stores an enum's position number (0, 1, 2, and so on) rather than its name. If a new status is later inserted in the middle of the enum's declaration, or the existing constants are reordered, every previously stored row's ordinal number now points to a different, incorrect status than the one it was actually saved with. This corruption happens silently, with no exception thrown at read or write time, meaning a cancelled booking could silently be read back as PENDING or any other status, with no indication anywhere that something is wrong.

6. Why does Show need its own features list, separate from Screen.features, even though both use the exact same Feature enum?
Screen.features represents what a screen is physically capable of, for example, having 3D projection hardware installed. Show.features represents what is actually enabled for one specific screening. A screen capable of 3D might still run a particular show in plain 2D. Since these two facts can genuinely disagree, collapsing them into a single shared list would make it impossible to represent a screen's general capability separately from what one specific show is actually doing with that capability.

7. Why is @ElementCollection the correct annotation for Screen.features and Show.features, rather than @ManyToMany?
@ManyToMany is designed for relationships between two real entities, each backed by its own database table. Feature is a plain Java enum with no table of its own, it is a list of simple values, not a list of related entity records. @ElementCollection, combined with @Enumerated(EnumType.STRING), is the correct tool for mapping a list of plain values, and it creates a small supporting table behind the scenes (such as screen_feature) rather than attempting a join between two entity tables that don't both exist.

8. Explain what a Spring Data derived query method like findByScreen_Theatre_Region_Name actually does, and why the underscores matter.
Spring Data parses this method name by walking real field names across the entity's relationship chain: starting from Show, it follows the screen field to Screen, then the theatre field to Theatre, then the region field to Region, and finally reads the terminal name property on Region as the condition to filter by. Each underscore marks a hop to the next related entity's field. Every one of those field names must exactly match a real field declared on the corresponding entity class; a mismatch produces a "no property found" error at application startup rather than a compile-time error.

9. Why did the AI-generated repository interfaces pass the first three points of the standard AI Corner checklist but still fail to fully satisfy the system's actual needs?
The AI-generated repositories correctly matched the required contract (JpaRepository<T, Long>), followed the project's naming and package conventions, and handled the general edge case of generating all 11 requested interfaces consistently. What they could not do is anticipate a requirement specific to this system, listing shows filtered by region, since a bare JpaRepository only provides generic save/find-by-id/find-all operations with no custom filtering logic. Only checking the generated code against the system's actual, specific requirement (point 4 of the checklist) revealed this gap.

10. What is the practical difference between GenerationType.IDENTITY and manually assigning IDs in application code, and why does this project use IDENTITY?
GenerationType.IDENTITY delegates ID generation entirely to the database, which auto-increments the primary key value by one on every insert. The application never has to compute or assign an ID itself. This project uses IDENTITY because it is the simplest strategy that guarantees uniqueness without any coordination logic in the application layer, appropriate for a single-database MVP where the database itself is the sole source of truth for ID assignment.

11. What real bugs were found and fixed while building today's models, and what do they illustrate about working with an existing or inherited codebase?
Four real issues were caught: a stray, incorrectly-typed self-referencing field on Region that actually belonged on Theatre; a completely missing Theatre class body despite other classes already referencing it; a missing Payment-to-Booking back-reference that Booking.payments implicitly expected to exist; and several relationship pairs initially missing mappedBy, which would have silently created unwanted extra join tables. These illustrate that reviewing and correcting an existing codebase, catching what's wrong rather than assuming it's correct, is a normal and valuable part of real engineering work, not a sign that something unusual went wrong.

12. Why does today's implementation of R9 skip the Controller/DTO layer and connect CommandLineRunner directly to the Service layer?
This is an explicitly named MVP simplification for this specific session, not a permanent architectural stance. Building a full REST Controller and DTO layer alongside the model layer, database configuration, mapping decisions, and one working requirement would have been too much for a single session. The Controller/DTO layer returns in the next Code lecture once real REST endpoints are built; today's CLI-to-Service wiring exists only to prove the underlying Service logic and database mapping work correctly, end to end, without also requiring a full API surface.

Self-Check Questions
In your own words, explain why @MappedSuperclass is used on BaseModel instead of @Entity.
Trace through: if mappedBy = "screen" were accidentally removed from Screen.seats, describe exactly what would appear differently in MySQL after the application starts.
Write a snippet: add a @OneToMany(mappedBy = "seatType") list to SeatType that would let the system ask "give me every seat of this type." Explain what real requirement would need to exist to justify actually adding it.
Compare @ManyToOne/@OneToMany(mappedBy = ...) to @ManyToMany. Identify which BookMyShow relationship from today's session uses each, and explain why each is the correct choice for that specific case.
Explain, in your own words, why Booking:ShowSeat needed real reasoning about "over time" behavior, while most other relationships in this session did not.
Trace through: walk through what a query using EnumType.ORDINAL would return for a PaymentStatus field, if REFUNDED were later inserted between SUCCESS and FAILURE in the enum's declaration.
Write a snippet: add a second derived query method to ShowRepository that finds every Show for a given Movie name, regardless of region.
Compare Screen.features and Show.features. Describe a concrete real-world scenario where a query relying on the wrong one of these two fields would return an incorrect answer.
Explain why @ElementCollection was chosen over @ManyToMany for Show.features, even though multiple shows can share the same feature values.
Trace through: if a sixth PaymentProvider value were added to the system today (say, STRIPE), list every file from this session that would need to change, and every one that would not.
In your own words, explain the difference between what the schema allows (Booking:ShowSeat as many-to-many) and what the business logic should enforce (only one active booking per seat per show at a time).
Write a short paragraph describing, using your own words, why passing checklist points 1 through 3 was not sufficient to trust the AI-generated ShowRepository, and what point 4 specifically revealed.
Further Reading
Post-Read 8, Machine Coding 8: Design BookMyShow - the original source of every entity, relationship, and requirement (R9, R10/R11, R12, R17) built into real code in this document; revisit it for the full reasoning behind SeatType, ShowSeat, and ShowSeatType before their JPA mappings.
Post-Read 7, Machine Coding 6.2: Code Parking Lot 2 - the prior session's model on layering Repository, Service, and Controller correctly; relevant background for why today's CLI-to-Service shortcut is explicitly named as temporary, not a permanent pattern.
Spring Data JPA Official Reference Documentation, Query Methods - the official reference for how derived query methods like findByScreen_Theatre_Region_Name are parsed, directly relevant to Section 8.
Jakarta Persistence (JPA) Specification, Entity Relationships - the official reference for @OneToMany, @ManyToOne, @ManyToMany, and mappedBy, directly relevant to every mapping decision made in Section 5.
Hibernate ORM User Guide, Mapping Collections of Basic Types - the reference for @ElementCollection, relevant to how Screen.features and Show.features are stored in Section 6.
Baeldung, "Guide to @Enumerated in JPA" - a practical walkthrough of the EnumType.STRING versus EnumType.ORDINAL distinction covered in Section 5, useful for seeing additional real-world failure examples beyond the one demonstrated here.
Homework
1. Add a second custom query to ShowRepository: given a Movie
   name, find every Show for it (any Region). Wire it into a new
   ShowService method and test it via the CLI runner.

2. Extend Movie to match the Design lecture's richer version —
   cast, genre, languages, features, trailerDescription. Update
   the schema and re-verify the generated table.

3. For every OneToMany/ManyToOne pair we built today, open MySQL
   and confirm there is exactly ONE foreign key column — not an
   extra join table. If you find one, you're missing a mappedBy.

4. Open MySQL and confirm all 12 entity tables actually exist.
   If one is missing, that class is missing @Entity — find it
   and fix it.

5. Push everything to GitHub — branch name:
   bookmyshow-code-part1-complete

Last changed by 
 
Tushar Harsan·Follow
0
55
Add a comment
Published on  HackMD
