package com.example.generateinvoices.services;

import com.example.generateinvoices.exceptions.CustomerSessionNotFoundException;
import com.example.generateinvoices.models.*;
import com.example.generateinvoices.repositories.BookingRepository;
import com.example.generateinvoices.repositories.CustomerSessionRepository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

// TODO: implement generateInvoice —
//  1. find the customer's ACTIVE session, throwing CustomerSessionNotFoundException
//     ("Customer session not found") if there isn't one; then mark it ENDED and save it.
//  2. fetch every booking recorded against that session and merge their booked-room
//     quantities into a single Map<Room, Integer> (summing quantities for a room booked
//     across multiple bookings).
//  3. compute totalAmount as the sum of price * quantity across all rooms, add GST
//     (18% of that subtotal) and a service charge (10% of that subtotal) on top.
//  4. return a populated Invoice (bookedRooms, gst, serviceCharge, totalAmount including
//     GST and service charge).
public class BookingServiceImpl implements BookingService {
    private BookingRepository bookingRepository;
    private CustomerSessionRepository customerSessionRepository;

    public BookingServiceImpl(BookingRepository bookingRepository, CustomerSessionRepository customerSessionRepository) {
        this.bookingRepository = bookingRepository;
        this.customerSessionRepository = customerSessionRepository;
    }

    @Override
    public Invoice generateInvoice(long userId) throws CustomerSessionNotFoundException {
        return null;
    }
}
