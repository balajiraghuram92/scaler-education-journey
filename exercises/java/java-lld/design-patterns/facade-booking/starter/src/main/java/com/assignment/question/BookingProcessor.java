package com.assignment.question;

import com.assignment.question.models.BookingConfirmation;
import com.assignment.question.models.BookingResult;
import com.assignment.question.models.PaymentStatus;
import com.assignment.question.services.*;

import java.time.LocalDate;

public class BookingProcessor {

    private AvailabilityService availabilityService;
    private PaymentService paymentService;
    private NotificationService notificationService;
    private LoyaltyService loyaltyService;
    private AccommodationDetailsService accommodationDetailsService;

    public BookingProcessor(AvailabilityService availabilityService, PaymentService paymentService, NotificationService notificationService, LoyaltyService loyaltyService, AccommodationDetailsService accommodationDetailsService) {
        this.availabilityService = availabilityService;
        this.paymentService = paymentService;
        this.notificationService = notificationService;
        this.loyaltyService = loyaltyService;
        this.accommodationDetailsService = accommodationDetailsService;
    }

    public BookingResult process(String userId, String accommodationId, LocalDate checkInDate, LocalDate checkOutDate) {
        // TODO: check availability first — return BookingResult.notAvailable(...)
        // if the accommodation is not free for these dates.
        //
        // TODO: attempt payment — return BookingResult.paymentFailed(...) if the
        // payment status is not PaymentStatus.SUCCESS.
        //
        // TODO: on success, build a BookingConfirmation, send it via
        // notificationService, update loyalty points using
        // paymentService.calculatePaymentAmount(...), update accommodation
        // details, and return BookingResult.success(confirmation).
        return null;
    }

}
