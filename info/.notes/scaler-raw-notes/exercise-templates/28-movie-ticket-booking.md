# Movie Ticket Booking

Source folder: `1773391645_1723effd232a8164/Movie_Ticket_Boo-solution`

## Problem Statement

Consider an online reservation system for booking tickets for a movie hall. The system needs to handle concurrent requests from multiple users trying to reserve seats. To ensure thread safety and prevent race conditions, a `ReentrantLock` can be employed.

### Requirements:
- The reservation system manages the availability of seats for a movie hall.
- Multiple users can attempt to reserve seats concurrently.
- A user should be able to reserve multiple seats in one booking.
- The system should prevent overbooking and ensure the integrity of seat reservations.

## Graded Contract (from tests)

- Class `MovieReservationSystem` must exist in package `org.example` with:
  - Constructor: `MovieReservationSystem(int totalSeats)` that initializes availableSeats and creates a ReentrantLock
  - Method: `boolean reserveSeats(int numSeats)` that:
    - Acquires lock before checking availability
    - Returns true if reservation successful (enough seats), false otherwise
    - Decrements availableSeats on success
    - Releases lock in finally block
  - Method: `int getAvailableSeats()` returning current available seats

- Must be thread-safe for concurrent access
- Must handle multiple sequential reservations correctly
- Must prevent overbooking (return false if not enough seats)

## Learner Template

```java
package org.example;

import java.util.concurrent.locks.*;

public class MovieReservationSystem {
    public MovieReservationSystem(int totalSeats) {
        // TODO: implement - initialize availableSeats and create ReentrantLock
        throw new UnsupportedOperationException("TODO");
    }

    public boolean reserveSeats(int numSeats) {
        // TODO: implement - acquire lock, check availability, modify state, release lock
        throw new UnsupportedOperationException("TODO");
    }

    public int getAvailableSeats() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Instance variables declaration (availableSeats, reservationLock)
- Lock acquisition and release pattern with try-finally
- Availability checking logic
- Seat decrement calculation
- Main method (empty in solution)

## Notes

- Must use ReentrantLock from java.util.concurrent.locks package
- Lock must be acquired before any state check/modification
- Lock must be released in finally block to ensure it's always released
- Tests verify both sequential and concurrent reservation scenarios
- Thread safety is critical; concurrent test verifies atomicity of operations
