Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/HkmYmOhLGx

Title: Untitled - HackMD
URL: https://hackmd.io
Source element: <body>
---
Untitled
Tushar Harsan·Follow
Last edited by
Tushar Harsan
on
Aug 14, 2026
POST-READ	Applied Design & Machine Coding	Machine Coding - 1: How to Approach Design Problems
Introduction

Module 2 built vocabulary: SOLID principles, nine design patterns, and formal UML notation. Module 3 is different. It is not about learning anything new in isolation, it is about learning to walk into a room, get handed a vague or half-detailed problem, and produce a working answer under pressure, combining everything already in the toolbox. This document teaches that shift on its own, start to finish, using one running example throughout: designing a Vehicle, carried from "what does the interviewer actually want" all the way to a complete class diagram.

No prior Post-Read exists yet for this "Applied Design & Machine Coding" series, so this document establishes the structural and tone conventions that later Post-Reads in this module will follow.
There are no animations to describe in this session; every visual below is either an ASCII diagram or a reference image built directly into the explanation.
Wherever this material depends on concepts taught earlier (SOLID, the Liskov Substitution Principle, UML notation, composition versus aggregation), those concepts are named explicitly and cross-referenced to Module 2 rather than assumed as "already covered in class." If you have not seen that material, treat the brief definitions given inline here as sufficient to follow this document; the Further Reading section points to where to go deeper.
Section 1: Not Every LLD Interview Is the Same Test
What It Means
Picture two companies. Company A wants to check if you deeply know your fundamentals: what static does, what Singleton is, why DIP matters. Company B wants to check if you can apply that knowledge to build something real, under a deadline.
These two companies would never run their interviews the same way, because they are testing fundamentally different things.
Knowing which of these tests you are walking into, before you even open a laptop to prepare, changes your entire strategy. There are three types of LLD interviews.
Three types of LLD interviews:
1. Theoretical
2. Design
3. Machine Coding

The Three Formats, in Detail

Theoretical

If a company just wants rapid proof that you know your concepts, not that you can design anything, the round only needs to be short: 30-45 minutes.
Format: several quick concept questions back to back ("what's the static keyword," "write me a quick Singleton," maybe a follow-up if you didn't handle thread-safety).
No end-to-end system, no real problem-solving. At most, toy code for one small thing.
Not language-specific, concept-specific. The interviewer cares about why, not which syntax.
Common at older, settled companies whose main product isn't tech itself: big banks, or a company like Oracle. PayPal is occasionally mentioned here too, though PayPal has been shifting toward Design-round style interviews recently. These categories are not fixed forever; companies move between them.

Design

A company that wants to see you actually use your knowledge on something realistic (like "design a system like Tinder") will hand you a real-world problem statement instead of asking "what is a Singleton" directly, and expect you to bring the relevant concepts out yourself while solving it.
Duration: ~45 minutes, one single case study (design a system like Paytm, Tinder, or AWS).
You are deliberately never given detailed requirements upfront. Figuring out what's actually being asked is itself part of the test.
Depth: class diagrams, schema design, maybe a few classes written on paper. Not a full working system.
Common at big tech: Amazon, Microsoft, Walmart, PayPal.
This does not mean Amazon or Microsoft never ask a theoretical question. They might still slip one in, especially early on. It's about which format dominates the round, not a hard rule.

Machine Coding

A startup with a small team and no time to train someone slowly mainly wants to see what you can ship, not just what you know.
Duration: ~2.5 hours. Detailed requirements are handed to you upfront.
You write real, running, end-to-end code, on your own machine, your own IDE, your own stack.
This is the most common first technical round today at startups and product companies: Flipkart, Myntra, and basically every startup.
FAANG-scale companies rarely run this format, because at that scale a single engineer almost never ships a whole system alone from scratch. Design instinct matters more day-to-day than solo implementation speed. Startups genuinely need someone who can build the whole thing themselves, fast, with zero onboarding time.
Machine Coding — tool flexibility:
- Any language, any framework, any IDE, any database — all fine
- What's actually being judged: your PRACTICES, not your tool choices
- You bring your own dev environment, fully set up, ready to go

If tool choice genuinely doesn't matter, the one thing that IS non-negotiable is arriving ready: language installed, IDE set up, framework you're comfortable with. Losing 15 minutes to setup is 15 minutes stolen from actual coding time, out of a fixed 2.5-hour budget.
Hidden Pitfalls
Preparing for the wrong format: memorizing textbook definitions when a Machine Coding round is coming (or vice versa) wastes prep time on the wrong skill set entirely.
Showing up without a ready dev environment: any minute spent installing a language or configuring an IDE is a minute taken directly out of a fixed 2.5-hour coding budget that is scored on output.
Assuming a company's interview format is permanent: formats shift over time (PayPal moving toward Design-style is a real example), so it is worth confirming the current format rather than relying on outdated information.
Section 2: Design Round vs. Machine Coding Round
What It Means
Both the Design round and the Machine Coding round ask for a class diagram, and often a schema diagram too. What differs is depth, direction, and time allocation.
                           Design Round                   Machine Coding Round
Problem statement     Single line, deliberately           Detailed requirements
                      ambiguous                           handed upfront

What's tested         How you bring CLARITY to            How much clarity you can
                      an ambiguous problem                extract even from detail

Requirements          You GATHER them                     You CLARIFY them

Diagrams              Class diagram, schema               Class diagram, schema

Code                  A few classes, on paper          FULL end-to-end working code

Duration              ~45 min                             ~2.5 hrs

The subtle part: in Machine Coding, the requirements are already detailed, so is "clarifying requirements" still a meaningful skill being tested there? Yes, just differently. Even "detailed" requirements have gaps and edge cases. Noticing those gaps and asking about them is still exactly what's evaluated, on top of raw execution speed. Detailed does not mean complete. A good candidate still finds the holes.
Practical Mechanics: The Machine Coding Timeline
Machine Coding round — typical timeline:
0:00 – 0:30   Clarify requirements → class diagram → schema diagram
0:30 – 2:00   Write code (interviewer often steps away)
2:00 – 2:30   Interviewer reviews code, asks follow-ups

Thirty minutes are budgeted for design, ninety for coding. If forty-five minutes are burned still arguing over the class diagram, the rest of the interview loses time from the part weighted most heavily in this round: actually writing working code.
Quiz Recap

You're in a Machine Coding round. The interviewer already gave you 12 detailed requirements. Should you still ask clarifying questions?

A) No, requirements are already detailed, just start coding
B) Yes, detailed doesn't mean complete; edge cases and gaps are still worth surfacing, and it's still part of what's evaluated (correct)
C) Only if you finish early
D) Only if the interviewer explicitly invites questions
Correct answer: B. This is the exact trap the round is designed to catch people in. A long requirements list can still hide edge cases, and surfacing them is itself part of what's scored.
Why A is wrong: it assumes volume of detail equals completeness, which is precisely the false assumption the round is testing for.
Why C is wrong: clarification needs to happen in the first 30-minute design window, not deferred to "if there's time left," because by then the design and code are already locked in.
Why D is wrong: waiting to be explicitly invited to ask questions is a passive habit; leading the requirements conversation is on the candidate, not something to wait for permission on (this exact passivity trap resurfaces again in Section 5).
Hidden Pitfalls
Treating "detailed" as "complete": assuming a long requirements list has already covered every edge case skips the clarification step and misses gaps that later break the code or cost interview points.
Overspending on the design phase: since Machine Coding weighs working code heavily, spending disproportionate time debating diagrams in the first 30 minutes directly shrinks the 90-minute coding window.
Section 3: The Scaler 6-Step Framework
What It Means
Given the two-column comparison above, a single process that prepares for either round needs to cover both gathering and clarifying, both diagrams, and code, just going deeper in the code step for Machine Coding.
The 6-step framework:
1. Get an overview        (align with the interviewer's intent)
2. Gather requirements     (5-8 core features, with rationale)
3. Clarify requirements    (edge cases, future scope)
4. Class diagram
5. Schema diagram
6. End-to-end working code

This is deliberately the superset of both interview types. Prepared this way, a 45-minute Design round is just "steps 1-5, deeper." A Machine Coding round is "all six steps, under more time pressure."
The rest of this document walks through steps 0-2 in full, using one running example: design a vehicle.
Hidden Pitfalls
Skipping straight to coding under pressure: jumping directly to writing classes loses the structured thinking that is actually being evaluated, even if the resulting code technically compiles.
Treating the schema diagram as always mandatory: step 5 only applies when there is a real system that needs persistence; forcing it into a pure entity-design problem wastes time on a step that doesn't apply.
Section 4: Step 0, Getting an Overview: Designing a Vehicle
What It Means
Interviewer prompt: "Design a vehicle for me." A common instinct is to immediately start listing vehicle types and attributes: car, bike, truck, petrol, electric.
The risk in skipping straight to that: you might end up solving a completely different problem than the interviewer actually meant. That's wasted effort, and it signals you didn't stop to think before diving in.
Step 0 — Get an Overview (before gathering requirements):
Align your mental model with the INTERVIEWER'S intent first.

Two scenarios:
  a) You already know the domain → state your understanding out
     loud, flag what's uncertain, confirm direction
  b) You don't know the domain → ask for a brief overview

Even though "vehicle" is a completely familiar object, the ask itself is genuinely ambiguous. Does the interviewer want ONE vehicle entity modeled with all its variants, or a whole software system built around vehicles, such as a rental company, a fleet management platform, or a dealership? That ambiguity is exactly why you ask before you build.
Practical Mechanics: Three Clarifying Questions
Three clarifying questions, worth asking early on almost every
LLD problem:

1. What exactly am I designing?
   - ENTITY — model the "thing" and its variants (e.g. all types
     of vehicles that exist) — no controllers, no persistence, no API
   - SYSTEM — a real software system managing/renting/tracking
     that thing

2. Do I need to persist data? (in-memory okay, or a real DB?)

3. How does a user interact with the system?
   - REST API
   - Command line
   - Hardcoded main() calling methods directly

The simplest of the three interaction modes, "hardcoded":

class Client {
    public static void main(String[] args) {
        // do whatever you want here — call methods directly,
        // no API layer, no controller, no persistence
    }
}

Suppose the interviewer clarifies: "I'm asking you to design all the different kinds of vehicles that exist on the road." Given that answer, do questions 2 (persist data?) and 3 (how does a user interact?) still matter? No. Both become irrelevant the moment it's confirmed to be pure entity design, not a system. They are automatically discarded.
"Entity design" ⇒ questions 2 and 3 become moot — there's no
persistence layer or interaction model to design at all.

Quiz Recap

An interviewer says: "Design all the different kinds of vehicles that exist." Which of the three clarifying questions is now genuinely irrelevant?

A) Only Q1, what am I designing
B) Q2 and Q3, persistence and interaction mode (correct)
C) None, all three still apply
D) Only Q3, interaction mode
Correct answer: B. Once it's confirmed as pure entity design, there is no system to persist data for or interact with, so both Q2 and Q3 drop away.
Why A is wrong: Q1 is exactly the question that just got answered and resolved, it isn't the one left irrelevant.
Why C is wrong: entity design genuinely has no persistence layer or interaction model to speak of, so treating all three as still applicable ignores the answer just given.
Why D is wrong: it only removes Q3 and leaves Q2 standing, but persistence is equally irrelevant here since there is no system state to persist.
Hidden Pitfalls
Diving into attributes before confirming scope: jumping straight to "a car has 4 wheels, an engine…" before resolving entity-vs-system risks spending the entire round modeling the wrong shape of problem.
Asking all three clarifying questions rigidly regardless of context: once entity vs. system is settled, mechanically asking the remaining questions anyway wastes time and can signal you weren't listening to your own previous answer.
Section 5: Step 1, Gathering Requirements
What It Means
A genuinely bad opening question at this stage is: "What features should I support?" This puts the entire burden of defining the problem back on the interviewer and makes you look passive rather than engaged.
DON'T ask: "What features should I support?"
DO suggest: "I'm thinking we should support X, because Y — does
             that make sense to include?"

You LEAD the requirements discussion. The interviewer reacts to
YOUR suggestions — that's what's actually being evaluated.

Practical Mechanics: Building the Vehicle Requirements List

For vehicles, a working requirements list, built with reasoning attached to each item:

Requirements gathered (5-8 core features — enough for 5-8 minutes,
no more):
- Support: PetrolVehicle, ElectricVehicle, HybridVehicle
- Petrol vehicles have an engine (needs refuelling); electric
  vehicles have a battery (needs charging); hybrids have both
- Every vehicle: brand, model name, price
- Transmission: manual OR automatic
- Behaviours: drive(), start()/stop(), refuel() and charge()
  (only where applicable)

A habit worth building for every feature suggested: ask whether it could evolve in the future, what the edge case is, and what might change, so the design anticipates it instead of needing a rewrite later.
Take "transmission" specifically. Manual and automatic behave completely differently under the hood. If this were naively stored as a boolean isAutomatic, what happens the day a third transmission type (say, CVT, or semi-automatic) needs to be added? A boolean only holds two values, a third option can't be represented at all without breaking the meaning of the existing field.
Rule of thumb, worth saying out loud in the interview:
"Booleans aren't extensible — I'll use an enum instead, so we
can add new values later without breaking the model."

TransmissionType enum: MANUAL, AUTOMATIC   (room to grow — CVT,
                                             semi-automatic, later)

Saying this sentence unprompted, at the right moment, genuinely signals to an interviewer that you're designing for change, not just for the current requirement. This is the same instinct behind the Liskov Substitution Principle and the Open-Closed Principle from Module 2, now showing up as an interview habit rather than a textbook rule.
Hidden Pitfalls
Asking "what features should I support?": this shifts responsibility for defining the problem onto the interviewer and reads as passive rather than as ownership of the design.
Using a boolean for anything with growth potential: a boolean hard-caps a field at exactly two states forever; the moment a third state appears, the entire model needs rework instead of a simple enum addition.
Gathering far more than 5-8 features: requirements gathering is deliberately capped at 5-8 core features (roughly 5-8 minutes); going well beyond that eats time that should go to later, higher-value steps.
Section 6: Step 2, The Class Diagram, Built Live
What It Means
There are two ways to arrive at a class diagram from a requirements list:
Visualize the physical object itself, and go from the outside in.
Find every noun in the requirements list; nouns are usually entities, and this method alone gets you about 99% of the classes in more abstract systems.
For a physical object like a vehicle specifically, visualization is faster under pressure: you can literally picture it and peel back layers, bonnet open, engine bay, battery pack.
Two ways to derive a class diagram:
1. VISUALIZE the object, go outside-in     ← used below
2. Find every NOUN in the requirements list  ← ~99% of classes,
                                                faster for abstract,
                                                non-physical systems

Keep both techniques available. Visualization wins for tangible objects like a vehicle. Noun-spotting wins for something more abstract, like a booking platform, and is used properly in a later lecture in this module.
Quick Recall: UML Notation Under Time Pressure
An earlier class (Module 2's UML lecture) covered proper UML in full: three-compartment class boxes, <<interface>>, italics for abstract classes, underlines for static members, solid-vs-dashed lines with hollow triangle arrowheads, and hollow vs. filled diamonds for aggregation and composition. That material is assumed known here and is not re-taught from scratch; only the parts being reused directly below are called out.
In an actual interview, with the clock running, there isn't time to draw all of that formally, in full detail, for every single class. But the core notation itself is fast once known, and using it properly is exactly what makes a diagram readable to an interviewer without extra explanation.
This is not a "different, faster style" invented for interviews. It is the same UML already taught, just applied with slightly less exhaustive detail inside each box (skip trivial getters/setters), while keeping every relationship symbol (arrows, diamonds, stereotypes) fully correct. That is the entire point of learning a standard notation: you don't reinvent shorthand under pressure, you just draw less inside the boxes, faster.

Board reference (notation recap): 

Practical Mechanics: Building the Diagram, Piece by Piece

Piece 1: The Outermost Box

Starting from the outside: should Vehicle be a concrete class, or something else, given that a petrol car, an electric car, and a hybrid all behave completely differently under the hood? Vehicle should be abstract. You would never instantiate a plain generic "Vehicle," only a specific powertrain type, but they all share common attributes like name, brand, and price.

Board reference: 

abstract class Vehicle {
    String name;
    String brand;
    double price;
    VehicleType type;                    // enum: PETROL, ELECTRIC, HYBRID
    TransmissionType transmissionType;   // enum: MANUAL, AUTOMATIC
    VehicleState state;                   // enum: RUNNING, STOPPED

    abstract void drive();
    void start() { /* shared or overridden per type */ }
    void stop() { /* shared or overridden per type */ }
}

Walkthrough: the abstract class holds every field shared across all vehicle types. drive() is declared abstract because petrol, electric, and hybrid vehicles each drive completely differently, forcing each subclass to supply its own implementation. start() and stop() may be shared as-is or overridden where a subtype needs different behavior.
VehicleType, TransmissionType, and VehicleState are fixed sets of values with no real methods of their own, so by proper UML notation they are drawn as <<enumeration>> stereotype boxes, not full three-compartment classes.
<<enumeration>>              <<enumeration>>            <<enumeration>>
VehicleType                  TransmissionType            VehicleState
PETROL, ELECTRIC, HYBRID     MANUAL, AUTOMATIC           RUNNING, STOPPED

Piece 2: Subclasses and Interfaces, With Correct Arrowheads

Refuelling and charging are behaviours only some vehicles have. This is the exact same shape of problem as the "Penguin can't fly" issue from the SOLID lecture in Module 2. The correct move is two separate interfaces, Refuelable and Chargeable, rather than putting both methods directly on the abstract Vehicle class. Putting both on Vehicle would force ElectricVehicle to implement a refuel() it will never use, and PetrolVehicle to implement a charge() it will never use, violating the Liskov Substitution Principle exactly like Penguin and fly().

Board reference: 

interface Refuelable {
    void refuel(Fuel fuel);
}

interface Chargeable {
    void charge();
}

class PetrolVehicle extends Vehicle implements Refuelable {
    private Engine engine;
    public void refuel(Fuel fuel) { engine.addFuel(fuel); }
    public void drive() { /* uses engine power */ }
}

class ElectricVehicle extends Vehicle implements Chargeable {
    private Battery battery;
    public void charge() { battery.chargeFully(); }
    public void drive() { /* uses battery power */ }
}

PetrolVehicle has an Engine as a field. This is neither inheritance nor an interface, so it is one of the two diamond relationships. The test carried over from the UML lecture: if a PetrolVehicle gets scrapped right now, does "that specific engine" still mean anything as an independent object in this system? No, exactly like the Car/Engine example from that lecture. This is composition (filled diamond), and it is a direct reuse of that earlier judgement, not a new decision.

Piece 3: Peeling One Layer Deeper

Engine itself is more than just "a power source." It has a fuel type, a displacement, and its own fuel tank with a capacity. Does a FuelTank mean anything independent of the specific Engine it's bolted to? No, composition again. A fuel tank ripped out of its engine bay doesn't function as "a fuel tank" on its own in this domain.
┌───────────────┐   ◆────   ┌───────────┐   ◆────   ┌───────────┐
│ PetrolVehicle │           │  Engine   │           │ FuelTank  │
└───────────────┘           ├───────────┤           ├───────────┤
                            │-displace- │           │-capacity: │
                            │  ment:    │           │  double   │
                            │  double   │           └───────────┘
                            │-fuelType: │
                            │  FuelType │
                            └───────────┘
       <<enumeration>>
       FuelType
       PETROL, DIESEL

┌────────────────┐   ◆────    ┌────────────┐
│ ElectricVehicle│            │  Battery   │
└────────────────┘            ├────────────┤
                              │-capacity:  │
                              │  double    │
                              │-charging-  │
                              │  Type:     │
                              │  Charging- │
                              │  Type      │
                              │-features:  │
                              │  List<...> │
                              └────────────┘
       <<enumeration>>                    <<enumeration>>
       ChargingType                        BatteryFeature
       FAST, SLOW                          REGEN_BRAKING,
                                            THERMAL_MGMT,
                                            FAST_CHARGING

Board reference: 

class Engine {
    double displacement;
    FuelType fuelType;     // enum: PETROL, DIESEL
    FuelTank fuelTank;
}

class FuelTank {
    double capacity;
}

class Battery {
    double capacity;
    ChargingType chargingType;         // enum: FAST, SLOW
    List<BatteryFeature> features;      // enum: REGENERATIVE_BRAKING,
                                          // THERMAL_MANAGEMENT, FAST_CHARGING
}

Every diamond so far has been filled. A case where a hollow diamond (aggregation) would make more sense in this same domain: Vehicle HAS A Driver. The driver existed as a person before getting into the vehicle, and continues existing independently after getting out. Same logic as the Car/Driver example from the UML lecture. Not everything a class "has" is composition; the test is always the same one from before: does the part survive, meaningfully, without the whole?

Board reference: 

Piece 4: The Subtle One, Hybrid and Composition Does Not Equal Capability

Bring in HybridVehicle. It has BOTH an Engine AND a Battery, two composition diamonds coming off it. Does that mean every HybridVehicle should ALSO get a dashed "implements" arrow to both Refuelable and Chargeable? Not necessarily. A regular hybrid's battery only charges internally, through regenerative braking and the engine itself. There is no public charging port. Only a plug-in hybrid can actually be plugged in and charged externally.
This is the real-world engineering distinction between a normal HEV (hybrid electric vehicle) and a PHEV (plug-in hybrid), not just marketing language.
                    ┌───────────┐
                    │  Vehicle  │
                    └───────────┘
                          △
                          │
                 ┌─────────────────┐   ◆──── Engine
                 │  HybridVehicle  │   ◆──── Battery
                 └─────────────────┘
                          △
                          │              (no dashed arrow to
                          │               Chargeable here — the
                          │               composition diamond to
                          │               Battery does NOT imply
                          │               the Chargeable interface)
              ┌─────────────────────┐
              │ PluginHybridVehicle │
              └─────────────────────┘
                        ┈┈┈△
              ┌──────────────┐
              │ <<interface>>│
              │  Chargeable  │
              └──────────────┘

class HybridVehicle extends Vehicle implements Refuelable {
    private Engine engine;
    private Battery battery;      // charges internally, no public charge()
    public void refuel(Fuel fuel) { engine.addFuel(fuel); }
    public void drive() { /* uses engine + battery together */ }
}

class PluginHybridVehicle extends HybridVehicle implements Chargeable {
    public void charge() { /* battery charges via external port */ }
}

Why not just draw that dashed "implements Chargeable" arrow straight from HybridVehicle, the same way it was drawn for ElectricVehicle? Because not every hybrid vehicle actually has a chargeable port. Forcing that arrow (and the charge() method) onto every HybridVehicle would break the Liskov Substitution Principle for the non-plug-in ones, exactly the same shape of mistake as forcing refill() onto every pen regardless of whether it's sealed or refillable.
The instinct to carry into every design problem: a composition diamond only tells you what a class is made of. It never automatically earns that class a dashed "implements" arrow to a capability, no matter how tempting it is to add that arrow one level higher "just because most of them have it."
Outside-in visualization technique — the checklist:
1. Start with the most general, outermost concept → likely
   ABSTRACT (italicized box: Vehicle)
2. Peel inward — each distinct "part" with its own attributes →
   its own box, connected with a COMPOSITION diamond (filled) if
   it can't meaningfully outlive the whole (Engine, FuelTank,
   Battery) — or AGGREGATION (hollow) if it can (e.g. Driver)
3. Behaviours that don't apply to every subtype → INTERFACE
   (<<interface>> box), connected with a dashed "implements"
   arrow — never forced onto the parent
4. Any attribute with only a few fixed states, no behaviour →
   ENUM (<<enumeration>> box: VehicleType, TransmissionType,
   FuelType, ChargingType)
5. A value check alone → enum. A value WITH associated behaviour →
   interface.
6. A composition/aggregation diamond never automatically earns an
   implements arrow — a HybridVehicle HAS a Battery, but doesn't
   automatically get Chargeable unless it genuinely supports
   external charging.

Under a 30-45 minute clock, there is no expectation to write every getter and setter in full UML compartments on a whiteboard. What IS expected: the right boxes for the right kind of entity, class, <<interface>>, abstract in italics, <<enumeration>>, and the right connectors, solid/dashed arrows with hollow triangles, filled/hollow diamonds, even if the attribute/method lists inside stay short.
Quiz Recap

You're modeling this same Vehicle hierarchy. A HybridVehicle has a Battery (drawn with a filled composition diamond), but its battery only ever charges via regenerative braking, never through an external plug. On your UML diagram, should there be a dashed "implements" arrow with a hollow triangle from HybridVehicle to <<interface>> Chargeable?

A) Yes, it has a Battery, so it should support charging
B) No, a composition diamond to Battery doesn't automatically earn an implements arrow to Chargeable; only a genuinely plug-in variant gets that arrow (correct)
C) Yes, but draw the arrow with a lighter/dotted line to show it's "partial"
D) It doesn't matter, either works fine
Correct answer: B. Same shape as Penguin/fly() and the disposable-pen problem, now expressed in UML terms: a diamond relationship never implies an implements arrow.
Why A is wrong: having a battery only describes what the class is made of; it says nothing about whether that battery exposes an external charging capability.
Why C is wrong: UML has no notion of a "partial capability" arrow. A dashed line with a hollow triangle either applies in full (the class genuinely implements the interface) or it doesn't apply at all; inventing an in-between style misrepresents the model.
Why D is wrong: drawing the wrong arrow actively misleads a reader into believing every HybridVehicle supports charge(), which is factually false and reintroduces the exact Liskov Substitution violation the design was built to avoid.

Final board diagram, complete vehicle hierarchy: 

Hidden Pitfalls
Jumping to noun-spotting for a physical object: for tangible items like a vehicle, visualization outside-in is faster; noun-spotting is better saved for abstract systems. Using the wrong technique for the wrong problem type wastes time under a fixed clock.
Drawing full three-compartment detail for every class under time pressure: skipping exhaustive getter/setter listing is expected and encouraged; over-drawing burns minutes better spent on getting relationships and correctness right.
Letting composition imply capability: assuming a class composed of a "chargeable-looking" part automatically earns the matching interface is the single most repeated subtlety in this material, and the direct cause of Liskov Substitution violations when skipped.
Modeling enums as full classes: giving VehicleType or TransmissionType a three-compartment box with methods, when they are just fixed value sets, wastes diagram space and mid-interview time; the <<enumeration>> stereotype exists for exactly this case.
Section 7: AI Corner, Using AI to Train Yourself, Not to Shortcut Yourself
What It Means
In Module 2, AI Corner was about catching code bugs, shallow copies, missed edge cases. Here the bottleneck isn't code, it's requirements-gathering and design clarity, the things that actually get evaluated in the first 30 minutes of an interview. AI's job shifts from "find my bug" to "be my sparring partner while I practice thinking out loud."
If the actual interview is a live, verbal, back-and-forth conversation, can that be meaningfully practiced just by typing prompts at an AI and reading answers? Not really. Reading isn't the same skill as speaking. The practice needs to actually be spoken out loud to be useful.
Four ways to use AI while preparing for LLD rounds:
1. As a starting point — to break a blank page
2. As a thinking partner — to pressure-test YOUR requirements
3. As a mock interviewer — to practice extracting requirements
4. As a mirror — to check if your design matches what you meant

Practical Mechanics: The Four Uses

Step 1 of 4: AI as a Starting Point

Sometimes the hardest part isn't design skill at all, it's staring at a blank page for the first sixty seconds when an unfamiliar system gets thrown at you. A low-cost way to break that freeze: ask AI for a rough, generic starting point, then react to it and improve it. Reacting is easier than generating from nothing.
Example prompt: "Give me a rough, high-level starting point for designing a parking lot system, just enough to react to, not a full design."
The answer that comes back will usually be shallow and generic, a few obvious entities, nothing carefully thought through. That shallowness is not a flaw, it's exactly what makes the answer useful: it gives you something to critique, question, and rebuild on top of, using Steps 0-2, instead of sitting in front of nothing.
Rule: AI's first answer is a rough sketch to REACT to,
never a design to copy. You still run Steps 0-2 on top of it.

Step 2 of 4: AI as a Thinking Partner, Refining Requirements

Draft a rough requirements list on your own first. Then hand it to AI, not to get answers, but to pressure-test what you already came up with.
Example prompt:
"Here are the functional requirements I've drafted for a parking
lot system: [paste 5-6 requirements]. Act like a senior engineer
reviewing this list in a design discussion. Only flag things that
are genuinely missing or ambiguous — don't invent unrelated
features, and don't rewrite my list."

Read AI's critique and react to each point deliberately: some gaps are fair and worth folding in, others are scope creep worth ignoring. Not every suggestion should be accepted. What decides whether a suggestion gets folded in or thrown out is the same discipline from Step 1: does it fit inside the 5-8 core feature scope for this round? Does it actually matter for the stated problem, or is it out-of-scope noise that would burn time better spent elsewhere?
Rule: AI's suggestions are one more idea on the table to evaluate
— not instructions to follow. YOU still decide what's in scope.

Step 3 of 4: AI as a Mock Interviewer

Now the reverse. Instead of you leading, AI leads, and you have to extract requirements the way it was practiced with the vehicle.
Example prompt:
"You are conducting a design-round LLD interview. Give me a
single-line, deliberately ambiguous prompt like a real interviewer
would — something like 'design a vending machine.' Then respond
to my clarifying questions the way a real interviewer would:
answer only what I actually asked, one thing at a time, and don't
volunteer requirements I haven't asked for yet."

Run Steps 0-1 live against the AI, narrating each clarifying question and why it's being asked, exactly as done with the vehicle. Does the AI actually hold back and make you earn each requirement, or does it just dump everything immediately, defeating the whole point? This genuinely varies by tool; sometimes AI over-explains everything unless explicitly told to stay terse and interviewer-like. It's worth re-prompting if it breaks character.
The practice should then be attempted solo, out loud, not by typing your thoughts. The real interview is verbal, so your practice should be too.
Rule: Explicitly instruct AI to act terse and answer-only-what's-
asked. Practice OUT LOUD — this is a speaking skill, not a
typing skill.

Step 4 of 4: AI as a Mirror, Checking Your Design Against Your Own Intent

Having just built the Vehicle class diagram, if you had to describe that same design out loud, in plain English, to someone who couldn't see the board, would what comes out of your mouth exactly match what's actually written up there? Probably not perfectly. Verbal explanations tend to skip details you assumed were "obvious," which is exactly where interview follow-ups catch people.
Example prompt:
"I'm going to describe a class design in plain English, the way
I'd explain it out loud in an interview. Based only on my
description, output a list of classes with their attributes and
methods, and the relationships between them (inheritance,
interface, composition). Don't add anything I didn't say or
imply. Here's my description: [describe the Vehicle hierarchy
verbally, as if explaining it fresh — including the Hybrid vs
Plug-in-Hybrid distinction]"

Compare AI's structured output against the actual whiteboard diagram side by side. Where the two don't match, is that a gap in the explanation, or a gap in the actual design? Usually it's a gap in the explanation. The Hybrid-vs-Plug-in-Hybrid split, in particular, is very easy to say out loud sloppily and have AI (or a real interviewer) miss entirely, even when the board diagram had it right.
Rule: The gap between "what I think I said" and "what I actually
specified" is exactly what interviewer follow-up questions are
designed to surface. Catching it yourself, in practice, is
cheaper than catching it live in the actual interview.

Quick Add-On: Justify the Decision

Consider the enum-over-boolean call for transmission type, and the two separate interfaces for refuelling versus charging. If AI were asked to justify one of these choices, how would you know if its reasoning is actually sound for this specific vehicle problem, versus generic textbook justification? Check whether the reasoning names the actual constraint hit: a third transmission type (CVT) breaking a boolean, or a HybridVehicle being forced into a charge() method it doesn't actually support. Generic reasoning that could apply to literally any enum-or-interface question is a red flag that it's boilerplate, not real analysis.
Rule: A good justification names YOUR specific constraint.
A generic justification that fits any problem = not real analysis
— from AI, or from yourself, in an actual interview.

NOT a legitimate use of AI: asking it to design the whole system
for you and memorizing the output. That defeats the entire
purpose — the interview tests YOUR live reasoning, not your
ability to recite a memorized answer.

Hidden Pitfalls
Practicing only by typing: since the real interview is verbal, typing-only practice with AI misses the actual skill being tested, which is speaking through your reasoning under pressure.
Accepting every AI suggestion as gospel: treating AI's critique of your requirements as authoritative rather than one more input to filter through your own scope discipline invites scope creep.
Letting AI over-explain during mock-interview practice: if not explicitly told to stay terse, AI tends to dump all requirements at once, defeating the practice of earning requirements one at a time.
Memorizing an AI-generated design instead of practicing reasoning: this defeats the purpose entirely, since interviews test live reasoning, not recall.
Wrap-Up: Tying It Together

Three ideas carry this entire document, and are worth fixing in memory before moving on:

Three types of LLD interviews:
- Theoretical  → tests KNOWLEDGE, rapid-fire, no real design
- Design        → tests CLARITY on an ambiguous prompt, ~45 min
- Machine Coding → tests EXECUTION on detailed requirements, ~2.5 hrs

The 6-step framework — use it for EVERY problem in this module:
1. Overview        — align intent, entity vs system
2. Gather           — lead with suggestions, 5-8 features
3. Clarify          — edge cases, future scope, for each feature
4. Class diagram    — outside-in or nouns; abstract/interface/enum
5. Schema diagram    — only if it's a real system, not pure entity
6. Working code      — MVC-structured, one requirement at a time

AI, used well, is a sparring partner — for starting points, for
pressure-testing your requirements, for practicing the interview
conversation out loud, and for catching the gap between what you
meant and what you actually said. It is never a replacement for
your own live reasoning — that reasoning is the entire thing being
tested.

Everything practiced here for the vehicle, overview, requirements, class diagram, is the exact same process to run for every problem in this module, just on bigger systems. The framework does not get more complicated as problems get bigger; it just gets applied more times, more carefully, under more time pressure. The next document in this series applies the same six steps to a much larger problem: TicTacToe, generalized to an N by N board, with bots, difficulty levels, and an undo feature, since "just build TicTacToe" is never actually the full ask in a real interview.

Common Pitfalls Summary
1. Preparing for the wrong interview format.
   -> Prepping pure theory when a Machine Coding round is coming
      (or vice versa) wastes prep time on the wrong skill set.

2. Showing up without a ready dev environment.
   -> Any setup time in a Machine Coding round is stolen directly
      from a fixed 2.5-hour coding budget.

3. Assuming a company's interview format never changes.
   -> Formats shift over time (e.g. PayPal moving toward
      Design-round style); confirm current format, don't assume.

4. Treating "detailed requirements" as "complete requirements."
   -> Even a 12-point requirements list can hide edge cases;
      surfacing them is still part of what's evaluated.

5. Overspending time on the design phase in Machine Coding.
   -> The 30-minute design budget bleeding into the 90-minute
      coding budget directly hurts the most heavily weighted part.

6. Skipping Step 0 or Step 1 under time pressure and jumping to code.
   -> Loses the structured thinking that is actually being graded,
      even if the resulting code compiles.

7. Treating the schema diagram (Step 5) as always mandatory.
   -> It only applies to real systems needing persistence, not to
      pure entity-design problems.

8. Diving into attributes before confirming entity vs. system scope.
   -> Risks modeling the wrong shape of problem for the entire round.

9. Asking all three clarifying questions rigidly, regardless of context.
   -> Wastes time and can look like you ignored your own previous
      answer once entity vs. system is already resolved.

10. Asking "what features should I support?" as an opening question.
    -> Shifts the burden of defining the problem onto the
       interviewer instead of demonstrating ownership.

11. Using a boolean for any field with growth potential.
    -> A boolean hard-caps a field at two states forever; adding a
       third state later breaks the model instead of extending it.

12. Gathering far more than 5-8 core features.
    -> Eats time that should go toward clarification, diagramming,
       and code.

13. Using noun-spotting for a physical, tangible object.
    -> Visualization is faster for physical objects; noun-spotting
       is better saved for abstract systems.

14. Drawing exhaustive three-compartment UML detail under time pressure.
    -> Burns minutes that should go toward relationships and
       correctness, not toward every getter and setter.

15. Letting a composition diamond imply a capability interface.
    -> The most repeated mistake in this material: "HAS A Battery"
       does not automatically mean "IS Chargeable."

16. Modeling fixed-value fields as full classes instead of enums.
    -> Wastes diagram space and interview time on entities that
       have no real behaviour of their own.

17. Practicing AI-based interview prep only by typing.
    -> The real interview is verbal; typing-only practice misses
       the actual skill being tested.

18. Accepting every AI critique or suggestion without filtering it.
    -> Leads to scope creep or over-engineering beyond the 5-8
       feature discipline.

19. Letting AI over-explain during mock-interview practice.
    -> Defeats the purpose of practicing to earn requirements one
       at a time, the way a real interviewer withholds information.

20. Memorizing an AI-generated design instead of practicing reasoning.
    -> Interviews test live reasoning, not the ability to recite a
       memorized answer.

Higher-Level Hidden Pitfalls (cross-cutting, not listed above):

Confusing "knowing" the framework with being fast at it: understanding the 6-step framework intellectually is not the same as being able to execute all six steps fluidly under a ticking clock. Speed and fluency, not comprehension alone, is what actually gets tested.
Treating the six steps as strictly sequential and non-overlapping: in a real interview, it is common to loop back, for example, a class diagram revealing a missing requirement. Rigidly refusing to revisit an earlier step once it's "done" can lock in a flawed design that a quick backtrack would have fixed.
Key Terminology
Term	Meaning in Simple Words
Theoretical Interview	A short (30-45 min) LLD round testing raw concept knowledge through rapid-fire questions, with no real design problem to solve.
Design Round	A ~45-minute LLD round built around a single, deliberately vague problem statement, where gathering and clarifying requirements is itself part of the test.
Machine Coding Round	A ~2.5-hour LLD round with detailed requirements given upfront, where you write real, running, end-to-end code on your own machine.
Entity Design	Modeling a "thing" and its variants directly (for example, all types of vehicles), with no controllers, persistence, or API layer involved.
System Design (interview context)	Modeling a full software system that manages, rents, or tracks a thing, which does involve persistence and a way for users to interact with it.
The 6-Step Framework	The repeatable process taught in this module: overview, gather, clarify, class diagram, schema diagram, working code, used as a superset for both Design and Machine Coding rounds.
Outside-In Visualization	A technique for building a class diagram by picturing a physical object and peeling back its layers, from the outermost concept inward.
Noun-Spotting Technique	A technique for building a class diagram by treating every noun in a requirements list as a likely class, best suited to abstract, non-physical systems.
HEV (Hybrid Electric Vehicle)	A hybrid vehicle whose battery only charges internally, through regenerative braking and the engine, with no external charging port.
PHEV (Plug-in Hybrid Electric Vehicle)	A hybrid vehicle that can also be charged externally through a physical charging port, in addition to internal charging.

Composition, aggregation, <<interface>>, abstract classes, and the Liskov Substitution Principle are treated as prior knowledge from Module 2's SOLID and UML lectures and are intentionally not redefined here; see Further Reading below.

Frequently Asked Interview Questions

1. What are the three types of LLD interviews, and how does each differ in what it tests?
Theoretical interviews (30-45 minutes) test raw conceptual knowledge through rapid-fire questions with no real design problem, common at settled, non-tech-core companies like big banks or Oracle. Design interviews (~45 minutes) hand you a single, deliberately ambiguous case study (like "design Tinder") and test how well you bring clarity to that ambiguity, common at big tech like Amazon or Microsoft. Machine Coding interviews (~2.5 hours) give you detailed requirements upfront and test whether you can produce real, working, end-to-end code, common at startups and product companies like Flipkart or Myntra.

2. In a Machine Coding round, the interviewer already gave you a detailed requirements list. Should you still ask clarifying questions, and why?
Yes. Detailed does not mean complete. Even a thorough requirements list can hide edge cases and ambiguities. Noticing and surfacing those gaps is still part of what's being evaluated, alongside your raw execution speed. Skipping this step because the list "already looks complete" is exactly the trap this round is designed to catch.

3. How do you decide whether an LLD prompt is asking for an entity design or a system design?
Check whether the request is about modeling a "thing" and its variants (entity, for example "design all types of vehicles"), which needs no persistence or API layer, versus modeling a software system that manages, rents, or tracks that thing (system, for example "design a car rental platform"), which does need persistence and a defined way for users to interact with it. If it's unclear, ask directly, since this decision changes whether the next two clarifying questions (persistence, interaction mode) are even relevant.

4. Why is "what features should I support?" considered a weak opening question, and what should replace it?
It hands the entire burden of defining the problem back to the interviewer, which reads as passive rather than as ownership of the design. The stronger approach is to lead with a specific suggestion and its reasoning, for example "I'm thinking we should support X, because Y, does that make sense to include?" The interviewer's reaction to your suggestions, not their answer to an open-ended question, is what's actually being evaluated.

5. Why should transmission type be modeled as an enum rather than a boolean?
A boolean can only ever represent two states. Manual and automatic transmissions behave completely differently, and modeling that as isAutomatic works only as long as exactly two types exist. The moment a third type (like CVT or semi-automatic) needs to be added, a boolean field cannot represent it without breaking the existing meaning of the field. An enum (TransmissionType: MANUAL, AUTOMATIC) leaves room to add new values later without touching existing code, which is the same extensibility instinct behind the Open-Closed Principle.

6. What test determines whether a relationship between two classes should be drawn as composition or aggregation?
Ask whether the "part" would still mean anything as an independent object if the "whole" were destroyed right now. If the part cannot meaningfully outlive the whole (an Engine bolted into a scrapped vehicle, a FuelTank ripped out of its engine bay), it's composition, drawn with a filled diamond. If the part existed independently before and continues to exist independently after (a Driver who gets out of the vehicle), it's aggregation, drawn with a hollow diamond.

7. Why doesn't a HybridVehicle automatically implement both Refuelable and Chargeable just because it has both an Engine and a Battery?
Because a composition diamond only describes what a class is made of, it says nothing about what capabilities that class exposes externally. A regular hybrid's battery only charges internally through regenerative braking and the engine, with no public charging port, so it should not implement Chargeable. Only a plug-in hybrid variant, which genuinely supports external charging, should implement that interface. Forcing charge() onto every HybridVehicle would break the Liskov Substitution Principle for the non-plug-in ones.

8. What is the real engineering difference between an HEV and a PHEV, and how does that show up in the class diagram?
An HEV (hybrid electric vehicle) charges its battery only internally, via regenerative braking and the combustion engine, with no external charging port. A PHEV (plug-in hybrid electric vehicle) can additionally be plugged into an external power source to charge. In the class diagram, this is modeled by having HybridVehicle implement only Refuelable, while a separate PluginHybridVehicle subclass extends HybridVehicle and additionally implements Chargeable, rather than putting Chargeable on the parent class.

9. When should you use the "visualize the object" technique versus the "find every noun" technique for building a class diagram?
Visualization, picturing the physical object and peeling back its layers from the outside in, is faster for tangible, physical objects like a vehicle, where you can literally imagine opening the bonnet and finding the engine bay. Noun-spotting, treating every noun in the requirements list as a likely class, is faster and more reliable for abstract, non-physical systems, such as a booking platform, where there's no physical shape to visualize.

10. Why is Vehicle modeled as an abstract class instead of a concrete one?
Because a plain, generic "Vehicle" would never actually be instantiated on its own; only a specific powertrain type (petrol, electric, hybrid) exists in reality, and each drives completely differently. Making Vehicle abstract, with an abstract drive() method, forces every concrete subclass to supply its own driving behavior while still sharing common fields like name, brand, and price at the parent level.

11. What are the four ways to use AI while preparing for LLD interviews, and what is each one for?
As a starting point, to break the freeze of a blank page by reacting to a rough, generic sketch. As a thinking partner, to pressure-test a requirements list you already drafted yourself, without letting it dictate your scope. As a mock interviewer, to practice extracting requirements out loud the way you would live, with AI instructed to withhold information and answer only what's asked. As a mirror, to describe your own design verbally and check whether AI's structured interpretation of your explanation actually matches what you meant to say.

12. Why is it considered illegitimate to ask AI to design a whole system and then memorize the output?
Because the interview is testing your live reasoning process, not your ability to recall a pre-made answer. A memorized design falls apart the moment a follow-up question probes a decision you didn't actually make yourself, since you have no genuine reasoning behind it to defend. The entire value of the 6-step framework is in practicing the thinking, not in producing a polished final diagram to memorize.

Self-Check Questions
In your own words, explain why "detailed requirements" in a Machine Coding round does not mean "complete requirements."
Trace through what would go wrong if refuel() and charge() were placed directly on the abstract Vehicle class instead of on separate Refuelable and Chargeable interfaces. Which subclasses would be affected, and how?
Write a snippet: add a new transmission type called SEMI_AUTOMATIC to the TransmissionType enum, and describe what, if anything, else would need to change elsewhere in the code.
Compare the "visualize the object" approach and the "find every noun" approach for a movie ticket booking system. Which would you reach for first, and why?
Explain, in your own words, why a filled diamond (composition) connects PetrolVehicle to Engine, while a hollow diamond (aggregation) would connect Vehicle to Driver.
Trace through: if the prompt had been "design a car rental system" instead of "design a vehicle," how would the answers to the three clarifying questions (entity vs. system, persistence, interaction mode) change?
Write a snippet: sketch, in code, a PluginHybridVehicle class hierarchy that correctly avoids forcing a charge() method onto regular HybridVehicle instances.
Explain why requirements gathering is capped at 5-8 features rather than listing everything you can think of.
Compare a Theoretical LLD interview and a Design LLD interview in terms of what each is actually trying to measure about a candidate.
Trace through the AI-as-mirror exercise: if you described your Vehicle design out loud and AI's structured output was missing the HEV vs. PHEV distinction, what would that gap most likely indicate, and what would you do next?
In your own words, explain why using AI to generate a complete design and memorizing it defeats the purpose of interview preparation.
Write down the full sequence of the 6-step framework from memory, without looking back at this document, and note which step you find hardest to execute quickly.
Further Reading
Effective Java, Joshua Bloch ("Use enums instead of int constants" and related items) - directly relevant to the boolean-versus-enum discipline built around TransmissionType in this material.
Design Patterns: Elements of Reusable Object-Oriented Software (Gang of Four) - relevant background for how role-specific interfaces like Refuelable and Chargeable reinforce the pattern vocabulary built in Module 2.
Module 2's SOLID and UML lectures (not included in this document) - this material explicitly reuses the Liskov Substitution Principle, the Car/Engine composition example, the Car/Driver aggregation example, and full UML notation from that earlier material without re-teaching it; revisit those lectures directly for the full grounding.
Oracle Java Documentation on Enum Types - the official reference for how Java enums work, relevant to every enum introduced here (VehicleType, TransmissionType, FuelType, ChargingType, BatteryFeature).
UML Class Diagram Notation Reference (any standard UML notation guide) - useful for reviewing the exact meaning of stereotypes, italics, and diamond/arrow conventions referenced but not re-taught here.
Grokking the Object Oriented Design Interview (or an equivalent LLD interview preparation resource) - offers additional worked examples of the entity-vs-system distinction across other classic prompts, such as a parking lot, vending machine, or elevator system, useful for practicing the same 6-step framework on new problems.
Homework
1. Pick any object from your daily life (a water bottle, a
   backpack, a smartphone). Run Steps 0-2 on paper, exactly
   as done here for the Vehicle — overview, requirements with
   rationale, outside-in class diagram.

2. Use an AI assistant as a practice interviewer for the SAME
   object — verbally walk through your clarifying questions.
   Note one moment where the AI's response changed how you'd
   design it.

3. Debug an AI's flawed design. Use this exact system prompt,
   pick any one system from the bracket, and find every issue
   BEFORE fixing anything:

   "You are simulating a junior engineer's rushed submission for
   a [library management / vending machine / elevator] machine
   coding interview. Generate: (1) a short requirements list, and
   (2) a class diagram (classes with attributes and methods) that
   looks reasonable at first glance, but deliberately contains
   3-4 realistic design mistakes — for example: a boolean used
   where an enum should be, one class doing too much (a "God
   class"), a subclass forced to implement a method that doesn't
   apply to it, or a missing interface where one is clearly
   needed. Do NOT tell me what the errors are, and do NOT flag
   them in any way. Present it as if it's a good design. I will
   find and fix the errors myself."

4. Read up on schema design cardinality (1:1, 1:M, M:M) — we'll
   need it heavily starting next lecture.

Last changed by 
 
Tushar Harsan·Follow
0
55
Add a comment
Published on  HackMD
