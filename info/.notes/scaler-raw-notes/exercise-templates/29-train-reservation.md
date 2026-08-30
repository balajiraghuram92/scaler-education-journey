# Train Reservation System

Source folder: `1773391651_f50b32583b56510a/Train_Reservatio-solution`

## Problem Statement

Consider an online reservation system for booking tickets for an Indian train system. The system needs to handle concurrent requests from multiple users trying to reserve seats. To ensure thread safety and prevent race conditions, a ReentrantLock can be employed.

### Requirements:
- The reservation system manages the availability of seats for different seat types on Indian trains, including `1AC`, `2AC`, `3AC`, and `Sleeper`.
- Multiple users can attempt to reserve seats concurrently.
- A user should be able to reserve multiple seats of the same seat type.
- The system should prevent overbooking and ensure the integrity of seat reservations.

## Graded Contract (from tests)

- Class `ReservationSystem` must exist in package `org.example` with:
  - Constructor: `ReservationSystem(Map<String, Integer> availableSeats)` that:
    - Initializes availableSeats map with a copy of the input
    - Creates a separate ReentrantLock for each seat type in seatTypeLocks map
  
  - Method: `boolean reserveSeats(String seatType, int numSeats)` that:
    - Retrieves the lock for the given seat type
    - Acquires the lock before checking/modifying
    - Returns true if reservation successful, false if not enough seats
    - Decrements available seats on success
    - Releases lock in finally block
  
  - Method: `int getAvailableSeats(String seatType)` returning available seats for that type

- Must be thread-safe for concurrent access to different seat types
- Must handle multiple reservations on different seat types independently

## Learner Template

```java
package org.example;

import java.util.*;
import java.util.concurrent.locks.*;

public class ReservationSystem {
    public ReservationSystem(Map<String, Integer> availableSeats) {
        // TODO: implement - initialize availableSeats and create ReentrantLock for each seat type
        throw new UnsupportedOperationException("TODO");
    }

    public boolean reserveSeats(String seatType, int numSeats) {
        // TODO: implement - get lock for seat type, acquire, check availability, modify, release
        throw new UnsupportedOperationException("TODO");
    }

    public int getAvailableSeats(String seatType) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Instance variables declaration (availableSeats Map, seatTypeLocks Map)
- Map initialization and locking strategy (per seat type lock)
- Lock retrieval logic using seatType as key
- Lock acquisition and release pattern with try-finally
- Availability checking and seat decrement logic for specific seat type

## Notes

- Must use HashMap for both availableSeats and seatTypeLocks
- Each seat type must have its own ReentrantLock for independent locking
- Concurrent test verifies multiple threads can safely reserve different seat types
- Lock must be acquired from seatTypeLocks map before any state modification
- Tests verify both sequential and concurrent multi-seat-type scenarios with accurate final counts
