Source: Downloads/machine-coding/lesson_8.txt (Scaler Companion AI-generated class revision notes)

Comprehensive Revision Notes: Designing BookMyShow
Overview
In this live class, we explored the structural design of the BookMyShow platform, focusing specifically on movie ticketing functionalities. We covered the requirements gathering process, the development of a comprehensive class diagram, and began setting up our first Spring Boot project to illustrate practical application scenarios. The discussion was centered around understanding how users interact with the system, modeled through a city-theater-screen hierarchy, and emphasized concurrency controls on booking transactions.

Defining the System: BookMyShow
Problem Statement
BookMyShow is a ticketing platform that allows users to book tickets for movies, shows, concerts, and sports events.
Today’s discussion is limited to booking movie tickets, emphasizing the user journey through city, theater, screen, and seat selection phases.
Initial Considerations
System Familiarity: Assumed user familiarity with the platform for efficient requirement alignment.
System Scope: Focused exclusively on the movie ticket booking feature for clarity.
Requirements Gathering
Key Functional Requirements
User Bookings: Users should be able to select and book seats for specific movie shows.
Multiple Cities and Theaters: The system supports a hierarchy of cities, each with multiple theaters.
Screen Structure: Each theater contains multiple screens capable of showing one movie at a time.
Show vs. Movie
Show: Defined as a composite of a specific movie, shown on a particular screen, at a designated start and end time.
Users book seats for precise shows rather than generally for a movie.
Data Persistence
Real data persistence in MySQL is required, not limited to in-memory storage.
Seat Booking Specifics
Seat Limits: Maximum of 10 seats can be booked by one user per show.
Concurrency: Ensure no two users can book the same seat for a specific show simultaneously.
Pricing Model
Price Calculation: Price is a function of the show and seat type (e.g., Gold, Silver, Platinum).
Flexible Pricing: Allows variance in pricing based on different seat types and time slots.
Class Diagram Construction
Physical Hierarchy
City → Theater → Screen → Seat Structure: Modeled as a physical composition hierarchy, reflecting the booking structure.
Feature and Screen: Screens are associated with features like 2D, 3D, etc.
Critical Design Decisions
ShowSeat Entity: Consolidated booking status as a function of both Show and Seat.
ShowSeat: Maps shows to seats, storing their booking status.
ShowSeatType: Maintains pricing as a function of the show and seat type, preventing repetitive entries.
Distinguishable Attributes
Movie Attributes: Includes cast, genre, and supported languages.
Seat Types: Configurable per theater due to varying conventions (e.g., Gold, Recliner).
Setting Up Spring Boot
Introduction to Spring Boot
Framework Explanation: Spring Boot is a Java-based framework simplifying the app development process by providing default configurations.
Maven Build Tool: Used for dependency management and project structure maintenance.
Project Setup
Spring Initializer: Used to set up a basic Spring Boot project with required dependencies like Spring Boot DevTools, Lombok, JPA, and a MySQL driver.
JPA Configuration: Implements ORM through Hibernate, providing a seamless connection between Java classes and MySQL database tables.
Conclusion
The session established a clear functional and architectural understanding of BookMyShow's movie ticketing system, building a robust class diagram to map user interactions and system behaviors. By introducing Spring Boot, the groundwork is laid for transitioning from design to implementation, providing a solid foundation for real-world applications involving complex data interactions and seamless user booking experiences. Overall, this design and framework integration facilitate scalability and efficiency in the development lifecycle.