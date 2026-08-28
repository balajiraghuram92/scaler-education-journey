| PRE-READ | Foundations of Object-Oriented Design & Scalable Systems | Lecture-1: Intro to LLD for Scalable & AI-Ready Systems |
|----------|-------------------------------|------------------------------------------------------|

> **Welcome:** Today we officially begin the **Low Level Design (LLD)** journey. We will not write a single line of code in this session. Instead, we build the mental model first: what LLD is, how it helps in writing good code, how the whole module is structured, and why Object-Oriented Programming exists at all. Everything you learn for the next several weeks sits on top of today. Come with curiosity, not a keyboard.

---

## Overview

Here is what we will cover in this session, a quick tour so nothing feels brand new when the instructor says it out loud:

| Session Breakdown | What it is about |
|-------------------|------------------|
| What is LLD? (HLD vs LLD) | Zooming out to High Level Design (what components exist and how they connect), then zooming in to Low Level Design (how we actually write the code inside each component). |
| Why is LLD important? | The two payoffs: your day-to-day job and clearing LLD interview rounds. |
| Module Overview | The three-module LLD roadmap and what comes after it |
| Programming Paradigms | The two ways to structure code that matter for us: Procedural and Object-Oriented, and why the contrast matters. |
| The Concept of Entity | The single most important idea in OOP: an entity owns both its data and its behaviour, and controls what happens to it. |

The whole session moves from the outside in. We start at the level of servers and databases (HLD), then drill down to the code that runs inside them (LLD), and finally to the smallest unit of good design: a well-modelled entity.

---

## Why You Should Join This Class

This is the class where you stop thinking of code as "lines that make the feature work" and start thinking of it as something that has to be **maintained, extended, and reused** by an entire team over years. The difference between rewriting a whole module and changing one small piece is exactly what LLD teaches, and that difference shows up in real codebases and in interviews.

LLD rounds are now a deciding factor in hiring, even at the SDE-1 levels. Companies use them to separate engineers who can merely write code from engineers who can design code. So this session is not abstract theory. It directly affects the offers you receive and how fast you grow once you are hired. Even if you have written object-oriented code before, today gives you the **right mental model for why OOP exists**, and that model makes every later session easier.

---

## Prerequisites from the Previous Class

This is the very first lecture of the LLD module, so there is no prior LLD class to recall.

What we do assume you bring with you:

- **Very basic Java syntax:** You should recognize what a function looks like, what variables and data types are, and roughly how a program runs from a `main` method. If some of this is rusty or new, do not worry, but use the setup walkthrough below so you are ready when coding begins next class.
- **The idea of a "struct" or grouped data:** Helpful if you have seen attributes grouped together (a name, an age, a gender) as a single unit. We use this to contrast procedural data with OOP entities.
- **Comfort with everyday systems:** You have booked a cab, made an online payment, and used apps that serve thousands of users. That intuition is all you need for today's examples.

---

## Environment Setup

We will not code today, but the next session is hands-on, so get your environment ready now. Some of you already have Java set up; if so, just verify it works. Everyone else, follow this walkthrough in prose.

- **Install the JDK (Java Development Kit):** This is the toolkit that lets your machine compile and run Java programs. Download a current Long-Term Support version (Java 17 or Java 21 are good choices) from a trusted distributor such as Adoptium (Eclipse Temurin) or Oracle. Install it like any normal application.
- **Verify the JDK is working:** Open a terminal or command prompt and check the Java version. If the command reports a version number rather than an error, the JDK is installed correctly. If it says the command is not found, you may need to add Java to your system PATH; the installer for Temurin usually does this for you.
- **Install an IDE (your code editor):** An IDE makes writing and running Java far easier than a plain text editor. IntelliJ IDEA Community Edition is the most popular choice for Java and is strongly recommended. Alternatively, VS Code with the official Java Extension Pack works well if you prefer a lighter editor. Install one of these.
- **Create and run a tiny test project:** Inside your IDE, create a new Java project, let the IDE create a starter class with a `main` method, and run it so you see output in the console. The goal is simply to confirm that the full loop (write, compile, run) works on your machine before the next class.
- **GitHub ready:** Have a GitHub account and connect it to your machine. We commit code from the coding sessions onward, so getting this out of the way now saves time later.

If anything in this setup fails, bring the exact error message to class or post it in the chat. Setup issues are common and quick to fix once we see the message.

---

## Key Concept Preview

Come prepared to think about this one shift in perspective. It is the single most useful idea for understanding why OOP exists and why we structure code around entities:

| PROCEDURAL (the puppeteer and the puppets) | OBJECT-ORIENTED (the entity is in control) |
|---------------------------------------------|----------------------------------------------|
| Procedures are the active concept; entities are passive data. Any function anywhere can reach into an entity and change any attribute. The entity has no say. As the system grows, this becomes chaos that is impossible to debug. | Entities are the active concept; they own both their data and their behaviour. Nothing reaches in without permission. You write `driver.acceptRide()`, so the driver is doing the action. When a bug appears, all the logic lives in one place. |

> *"In OOP, the action belongs to the subject. OOP simply structures code the same way our minds already make sense of the world."*

---

## Coming Up Next: Representing Entities in Code

In the next class we move from concept to code: how a Java class represents an entity, how to create objects from it, and how to create many independent objects, turning today's Uber entities into your first real classes.
