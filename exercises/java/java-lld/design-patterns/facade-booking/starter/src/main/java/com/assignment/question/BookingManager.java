package com.assignment.question;

import com.assignment.question.models.BookingResult;
import com.assignment.question.services.*;

import java.time.LocalDate;

public class BookingManager {
    // TODO: this class must NOT hold direct fields of AvailabilityService,
    // PaymentService, NotificationService, LoyaltyService, or
    // AccommodationDetailsService — delegate to BookingProcessor instead.

    public BookingManager(AvailabilityService availabilityService, PaymentService paymentService,
                          NotificationService notificationService, LoyaltyService loyaltyService,
                          AccommodationDetailsService accommodationDetailsService) {
        // TODO: construct the internal BookingProcessor from these dependencies
    }

    public BookingResult bookAccommodation(String userId, String accommodationId, LocalDate checkInDate, LocalDate checkOutDate) {
        // TODO: delegate to the internal BookingProcessor
        return null;
    }

}
