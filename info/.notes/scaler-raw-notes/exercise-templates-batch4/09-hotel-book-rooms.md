# Hotel Management System: Book Rooms

Source folder: `1773391503_0b47898a19fd7972/Book_rooms-solution`

## Problem Statement

You are building a Hotel Management System. As a part of this system, you need to implement functionality using which customers can book hotel rooms.

## Detailed Requirements

1. A customer can book multiple rooms before requesting for an invoice. The system must track all rooms booked by a customer.
   - A `CustomerSession` entity tracks rooms booked by a customer.
   - Once a customer books their 1st room, create a `CustomerSession` with status `ACTIVE`.
   - All subsequent room bookings by the customer are associated with the same `CustomerSession`.

2. The booking request contains:
   - User id of the customer
   - Map<Long, Integer> where key = room id, value = number of such rooms booked

3. Store booking details in the database.

4. If a customer (user) doesn't exist in the database, throw an error.

5. If a booking contains a room not present in the database, throw an error.

6. Return the booking details in the response.

## Architecture Overview

**Controller Layer:**
- `BookingController` - handles HTTP request to make booking

**DTO Layer:**
- `MakeBookingRequestDto` - input: userId, Map<Long,Integer> bookedRooms
- `MakeBookingResponseDto` - output: Booking + ResponseStatus
- `ResponseStatus` - enum for SUCCESS/FAILURE

**Domain Models:**
- `BaseModel` - base class with id field
- `Booking` - extends BaseModel; links CustomerSession with bookedRooms Map<Room,Integer>
- `CustomerSession` - extends BaseModel; tracks user and session status (ACTIVE/ENDED)
- `Room` - extends BaseModel; room details (roomNumber, price, roomType, description)
- `User` - user details (id, name, phone, userType)
- `Customer` - customer model
- `Invoice` - invoice model (for reference, not directly used in booking)
- `CustomerSessionStatus` - enum (ACTIVE, ENDED)
- `RoomType` - enum (DELUXE, SUPER_DELUXE, SUITE)
- `UserType` - enum (ADMIN, CUSTOMER)

**Repository Layer (Interfaces):**
- `BookingRepository` - save(Booking)
- `CustomerSessionRepository` - save(CustomerSession), findActiveCustomerSessionByUserId(long)
- `RoomRepository` - findById(long), getRooms(), save(Room)
- `UserRepository` - findById(long), save(User)

**Repository Layer (Implementations):**
- `InMemoryBookingRepository` - in-memory HashMap-based storage
- `InMemoryCustomerSessionRepository` - in-memory HashMap-based storage
- `InMemoryRoomRepository` - in-memory HashMap-based storage
- `InMemoryUserRepository` - in-memory HashMap-based storage

**Service Layer:**
- `BookingService` (interface) - makeBooking(userId, Map<Long,Integer> roomsToBeBooked)
- `BookingServiceImpl` (implementation) - orchestrates booking creation with session management

**Exception Layer:**
- `UserNotFoundException` - thrown when user doesn't exist
- `InvalidRoomException` - thrown when room doesn't exist

## Graded Contract (from tests)

From `BookingControllerTest.java`:

1. **Repository instantiation** (via reflection):
   - Must have `BookingRepository`, `CustomerSessionRepository`, `RoomRepository`, `UserRepository` implementations with no-arg constructors

2. **Service instantiation** (via reflection):
   - Must have `BookingService` implementation
   - Constructor must accept four arguments in order: RoomRepository, UserRepository, CustomerSessionRepository, BookingRepository

3. **Test expectations:**
   - `makeBooking(userId, Map<Long,Integer>)` successfully:
     - Validates user exists (throw `UserNotFoundException` if not)
     - Validates all rooms exist (throw `InvalidRoomException` if any don't)
     - Creates or reuses active `CustomerSession` for user
     - Creates `Booking` object with CustomerSession and bookedRooms mapping
     - Saves booking to repository
     - Returns persisted `Booking` with all details intact
   - If user doesn't exist, returns FAILURE status and null booking
   - If any room in the booking doesn't exist, returns FAILURE status and null booking
   - Multiple bookings by same customer use same `CustomerSession`
   - `Booking.getBookedRooms()` returns Map<Room,Integer> with actual Room objects

## Learner Template

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.Booking;

public interface BookingRepository {
    Booking save(Booking booking);
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.CustomerSession;
import java.util.Optional;

public interface CustomerSessionRepository {
    CustomerSession save(CustomerSession customerSession);
    Optional<CustomerSession> findActiveCustomerSessionByUserId(long userId);
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.Room;
import com.example.bookrooms.models.RoomType;
import java.util.List;
import java.util.Optional;

public interface RoomRepository {
    Optional<Room> findById(long roomId);
    List<Room> getRooms();
    Room save(Room room);
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.User;
import java.util.Optional;

public interface UserRepository {
    Optional<User> findById(long userId);
    User save(User user);
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.Booking;
import java.util.HashMap;
import java.util.Map;

public class InMemoryBookingRepository implements BookingRepository {
    private Map<Long, Booking> bookingMap;
    private static long idCounter = 0;

    public InMemoryBookingRepository() {
        // Initialize in-memory storage
    }

    @Override
    public Booking save(Booking booking) {
        // Auto-generate ID if not set, store in map, return booking
    }
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.CustomerSession;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryCustomerSessionRepository implements CustomerSessionRepository {
    private Map<Long, CustomerSession> customerSessionMap;
    private static long idCounter = 0;

    public InMemoryCustomerSessionRepository() {
        // Initialize in-memory storage
    }

    @Override
    public CustomerSession save(CustomerSession customerSession) {
        // Auto-generate ID if not set, store in map, return customerSession
    }

    @Override
    public Optional<CustomerSession> findActiveCustomerSessionByUserId(long userId) {
        // Return Optional with active CustomerSession for user, or empty if none
    }
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.Room;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class InMemoryRoomRepository implements RoomRepository {
    private Map<Long, Room> roomMap;
    private static long idCounter = 0;

    public InMemoryRoomRepository() {
        // Initialize in-memory storage
    }

    @Override
    public Optional<Room> findById(long roomId) {
        // Return Optional with room if found, empty if not
    }

    @Override
    public List<Room> getRooms() {
        // Return all rooms as a list
    }

    @Override
    public Room save(Room room) {
        // Auto-generate ID if not set, store in map, return room
    }
}
```

```java
package com.example.bookrooms.repositories;

import com.example.bookrooms.models.User;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryUserRepository implements UserRepository {
    private Map<Long, User> userMap;
    private static long idCounter = 0;

    public InMemoryUserRepository() {
        // Initialize in-memory storage
    }

    @Override
    public Optional<User> findById(long userId) {
        // Return Optional with user if found, empty if not
    }

    @Override
    public User save(User user) {
        // Auto-generate ID if not set, store in map, return user
    }
}
```

```java
package com.example.bookrooms.services;

import com.example.bookrooms.exceptions.InvalidRoomException;
import com.example.bookrooms.exceptions.UserNotFoundException;
import com.example.bookrooms.models.Booking;
import java.util.Map;

public interface BookingService {
    Booking makeBooking(long userId, Map<Long, Integer> roomsToBeBooked) throws UserNotFoundException, InvalidRoomException;
}
```

```java
package com.example.bookrooms.services;

import com.example.bookrooms.exceptions.InvalidRoomException;
import com.example.bookrooms.exceptions.UserNotFoundException;
import com.example.bookrooms.models.*;
import com.example.bookrooms.repositories.BookingRepository;
import com.example.bookrooms.repositories.CustomerSessionRepository;
import com.example.bookrooms.repositories.RoomRepository;
import com.example.bookrooms.repositories.UserRepository;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class BookingServiceImpl implements BookingService {
    private RoomRepository roomRepository;
    private UserRepository userRepository;
    private CustomerSessionRepository customerSessionRepository;
    private BookingRepository bookingRepository;

    public BookingServiceImpl(RoomRepository roomRepository, UserRepository userRepository, 
                             CustomerSessionRepository customerSessionRepository, BookingRepository bookingRepository) {
        // Store repositories
    }

    @Override
    public Booking makeBooking(long userId, Map<Long, Integer> roomsToBeBooked) throws UserNotFoundException, InvalidRoomException {
        // 1. Validate user exists; throw UserNotFoundException if not
        // 2. Validate all rooms exist; throw InvalidRoomException if any don't
        // 3. Find or create active CustomerSession for user
        //    - If no active session, create new one with status ACTIVE
        // 4. Convert room IDs to Room objects from the booking request
        // 5. Create Booking object with CustomerSession and Map<Room,Integer>
        // 6. Save booking using repository
        // 7. Return persisted booking
    }
}
```

## Deliberately Left Out (for the learner to design)

- **User validation logic** and throwing UserNotFoundException
- **Room validation logic** and throwing InvalidRoomException
- **CustomerSession creation/reuse logic** (find active or create new)
- **Room ID to Room object mapping** from the input Map
- **Booking object assembly** with all required fields
- **Auto-increment ID logic** in all repositories
- **Repository storage implementation** (HashMap operations)
- **Session status management** (ACTIVE vs ENDED)
