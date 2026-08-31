package com.example.bookrooms.repositories;

import com.example.bookrooms.models.Booking;

import java.util.HashMap;
import java.util.Map;

// TODO: implement BookingRepository as an in-memory store keyed by booking id — save(...)
// should assign an id when the booking doesn't already have one (id == 0) and store it.
public class InMemoryBookingRepository implements BookingRepository {
    private Map<Long, Booking> bookingsMap;
    private static long idCounter = 0;

    public InMemoryBookingRepository() {
        bookingsMap = new HashMap<>();
    }
    @Override
    public Booking save(Booking booking) {
        return null;
    }
}
