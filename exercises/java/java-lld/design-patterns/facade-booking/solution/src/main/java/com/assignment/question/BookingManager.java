package com.assignment.question;

import com.assignment.question.models.BookingResult;
import com.assignment.question.services.*;

import java.time.LocalDate;

public class BookingManager {

    private BookingProcessor bookingProcessor;

    public BookingManager(AvailabilityService availabilityService, PaymentService paymentService,
                          NotificationService notificationService, LoyaltyService loyaltyService,
                          AccommodationDetailsService accommodationDetailsService) {
        this.bookingProcessor = new BookingProcessor(availabilityService, paymentService, notificationService, loyaltyService, accommodationDetailsService);
    }

    public BookingResult bookAccommodation(String userId, String accommodationId, LocalDate checkInDate, LocalDate checkOutDate) {
        return bookingProcessor.process(userId, accommodationId, checkInDate, checkOutDate);
    }

}
