# Facade Pattern for Travel Booking Platform

Source folder: `1773391253_933f2539f089105a/Facade_Booking-solution`

## Problem Statement

You are working on an online booking platform for travel accommodations. The platform needs to handle bookings, payments, and notifications through different external services. The goal is to provide a simplified interface for customers and internal modules to perform booking-related tasks without directly dealing with the intricacies of each external service.

## Detailed Requirements

1. **Review the original class**: Take a closer look at the `BookingManager` class and its methods. Understand the dependencies it uses and the interactions with external services.

2. **Create the facade class**: Create a new class called `BookingFacade` that implements the Facade pattern. This class will encapsulate the complex interactions with the external services and provide a simplified interface for clients.

3. **Remember to call the constructor of your facade using the same arguments from the BookingManager class**: The constructor of your `BookingFacade` class should take the same arguments that the `BookingManager` class constructor does. This allows you to pass the necessary dependencies to the facade.

4. **Test your implementation**: Test cases have been provided for you to test your implementation. Run the test cases to ensure that your facade class works correctly and provides the expected functionality.

## Graded Contract (from tests)

The tests verify the following:

- **BookingManager** must NOT have any direct fields referencing: `AvailabilityService`, `PaymentService`, `NotificationService`, `LoyaltyService`, or `AccommodationDetailsService`
- **BookingManager constructor** accepts 5 parameters in order:
  - `AvailabilityService`
  - `PaymentService`
  - `NotificationService`
  - `LoyaltyService`
  - `AccommodationDetailsService`
- **bookAccommodation(String userId, String accommodationId, LocalDate checkInDate, LocalDate checkOutDate) -> BookingResult** method exists
- When `bookAccommodation()` is called, all of these must occur:
  - `availabilityService.checkAvailability(accommodationId, checkInDate, checkOutDate)` is called
  - `paymentService.makePayment(userId, accommodationId)` is called
  - `notificationService.sendBookingConfirmation(bookingConfirmation)` is called with correct details
  - `loyaltyService.updateLoyaltyPoints(userId, points)` is called
  - `accommodationDetailsService.updateAccommodationDetails(accommodationId, checkInDate, checkOutDate)` is called

## Learner Template

```java
package com.assignment.question;

import com.assignment.question.models.*;
import com.assignment.question.services.*;
import java.time.LocalDate;

public class BookingManager {
    private BookingProcessor bookingProcessor;

    public BookingManager(AvailabilityService availabilityService, 
                          PaymentService paymentService,
                          NotificationService notificationService, 
                          LoyaltyService loyaltyService,
                          AccommodationDetailsService accommodationDetailsService) {
        // TODO: initialize bookingProcessor with the dependencies
    }

    public BookingResult bookAccommodation(String userId, String accommodationId, 
                                           LocalDate checkInDate, LocalDate checkOutDate) {
        // TODO: delegate to bookingProcessor
    }
}
```

## Deliberately Left Out (for the learner to design)

- The initialization of `BookingProcessor` inside the constructor
- The delegation logic in `bookAccommodation()` method to call `bookingProcessor.process()`
- The understanding that `BookingProcessor` encapsulates all the booking workflow steps
- The data flow between the different services (availability check → payment → notification → loyalty → details update)
- The understanding that the facade pattern shields clients from the complexity of coordinating multiple external services
- The construction of the `BookingConfirmation` object with appropriate details
