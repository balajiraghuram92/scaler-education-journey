# Hotel Management System: Generate Invoice

Source folder: `1773391488_ca3da7b27cb67e72/Generate_Invoice-solution`

## Problem Statement

You are building a Hotel Management System. As a part of this system, you need to implement functionality using which customers can generate invoice for their bookings.

## Detailed Requirements

1. A customer can book multiple rooms before requesting for the invoice. Hence, the system must track all rooms booked by a customer.
   - Create a `CustomerSession` entity to track bookings by a customer.
   - Once a customer books their 1st room, create a `CustomerSession` with status `ACTIVE`.
   - All subsequent bookings by the customer are associated with the same `CustomerSession`.
   - Once the customer requests for the invoice, mark the `CustomerSession` as `ENDED`.

2. The request for generating the invoice contains only the customer id.

3. The functionality must aggregate all rooms booked by the customer and calculate the total amount to be paid.

4. Calculate GST (18% of total rooms price) and service charge (10% of total rooms price) on the total amount.

5. Return the invoice details in the response.

## Architecture Overview

**Controller Layer:**
- `BookingController` - handles HTTP request to generate invoice

**DTO Layer:**
- `GenerateInvoiceRequestDto` - input: userId
- `GenerateInvoiceResponseDto` - output: Invoice + ResponseStatus
- `ResponseStatus` - enum for SUCCESS/FAILURE

**Domain Models:**
- `BaseModel` - base class with id field
- `Invoice` - extends BaseModel; aggregates booked rooms, totalAmount, gst, serviceCharge
- `Booking` - extends BaseModel; links CustomerSession with bookedRooms Map
- `CustomerSession` - extends BaseModel; tracks user and session status (ACTIVE/ENDED)
- `Room` - extends BaseModel; room details (roomNumber, price, roomType, description)
- `Customer` - customer model (name, phone, userType)
- `User` - user base model
- `CustomerSessionStatus` - enum (ACTIVE, ENDED)
- `RoomType` - enum (DELUXE, SUPER_DELUXE, SUITE)

**Repository Layer (Interfaces):**
- `BookingRepository` - save(Booking), findBookingByCustomerSession(long)
- `CustomerSessionRepository` - save(CustomerSession), findActiveCustomerSessionByUserId(long)

**Repository Layer (Implementations):**
- `InMemoryBookingRepository` - in-memory HashMap-based storage
- `InMemoryCustomerSessionRepository` - in-memory HashMap-based storage

**Service Layer:**
- `BookingService` (interface) - generateInvoice(long userId)
- `BookingServiceImpl` (implementation) - orchestrates repositories to generate invoice

**Exception Layer:**
- `CustomerSessionNotFoundException` - thrown when no active session found
- `UserNotFoundException` - thrown when user not found

## Graded Contract (from tests)

From `GenerateInvoiceTests.java`:

1. **Repository instantiation** (via reflection):
   - Must have `BookingRepository` implementation with no-arg constructor
   - Must have `CustomerSessionRepository` implementation with no-arg constructor

2. **Service instantiation** (via reflection):
   - Must have `BookingService` implementation
   - Constructor must accept two arguments: BookingRepository and CustomerSessionRepository (in that order)

3. **Test expectations:**
   - `generateInvoice(userId)` successfully creates an `Invoice` with:
     - `bookedRooms` Map containing all rooms booked across multiple `Booking` records for that CustomerSession
     - `totalAmount` = sum of (room.price * quantity) + GST + serviceCharge
     - `gst` = 0.18 * (sum of room prices)
     - `serviceCharge` = 0.1 * (sum of room prices)
   - After generating invoice, the `CustomerSession` status must be updated to `ENDED`
   - If no active CustomerSession exists for userId, throw `CustomerSessionNotFoundException` (caught by controller as FAILURE)
   - Must handle multiple bookings per CustomerSession (aggregated into single invoice)

## Learner Template

```java
package com.example.generateinvoices.repositories;

import com.example.generateinvoices.models.Booking;
import java.util.List;

public interface BookingRepository {
    Booking save(Booking booking);
    List<Booking> findBookingByCustomerSession(long customerSessionId);
}
```

```java
package com.example.generateinvoices.repositories;

import com.example.generateinvoices.models.CustomerSession;
import java.util.Optional;

public interface CustomerSessionRepository {
    CustomerSession save(CustomerSession customerSession);
    Optional<CustomerSession> findActiveCustomerSessionByUserId(long userId);
}
```

```java
package com.example.generateinvoices.repositories;

import com.example.generateinvoices.models.Booking;
import java.util.HashMap;
import java.util.List;
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

    @Override
    public List<Booking> findBookingByCustomerSession(long customerSessionId) {
        // Return all bookings matching the customerSessionId
    }
}
```

```java
package com.example.generateinvoices.repositories;

import com.example.generateinvoices.models.CustomerSession;
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
package com.example.generateinvoices.services;

import com.example.generateinvoices.exceptions.CustomerSessionNotFoundException;
import com.example.generateinvoices.models.Invoice;

public interface BookingService {
    Invoice generateInvoice(long userId) throws CustomerSessionNotFoundException;
}
```

```java
package com.example.generateinvoices.services;

import com.example.generateinvoices.exceptions.CustomerSessionNotFoundException;
import com.example.generateinvoices.models.*;
import com.example.generateinvoices.repositories.BookingRepository;
import com.example.generateinvoices.repositories.CustomerSessionRepository;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class BookingServiceImpl implements BookingService {
    private BookingRepository bookingRepository;
    private CustomerSessionRepository customerSessionRepository;

    public BookingServiceImpl(BookingRepository bookingRepository, CustomerSessionRepository customerSessionRepository) {
        // Store repositories
    }

    @Override
    public Invoice generateInvoice(long userId) throws CustomerSessionNotFoundException {
        // 1. Find active CustomerSession for userId; throw exception if not found
        // 2. Mark CustomerSession as ENDED and save
        // 3. Fetch all bookings for this CustomerSession
        // 4. Aggregate all booked rooms into a single map (combining quantities)
        // 5. Calculate total amount, GST (18%), and service charge (10%)
        // 6. Create and return Invoice with all details
    }
}
```

## Deliberately Left Out (for the learner to design)

- **Auto-increment ID logic** in both in-memory repositories (learner must implement ID generation)
- **Aggregation logic** combining multiple Booking records into a single invoice
- **Calculation logic** for GST and service charge percentages
- **Exception handling** for missing CustomerSession (learner must throw CustomerSessionNotFoundException)
- **Status update logic** to mark CustomerSession as ENDED after invoice generation
