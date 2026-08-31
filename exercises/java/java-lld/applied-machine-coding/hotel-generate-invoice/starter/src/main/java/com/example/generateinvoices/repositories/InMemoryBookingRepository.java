package com.example.generateinvoices.repositories;

import com.example.generateinvoices.models.Booking;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

// TODO: implement BookingRepository as an in-memory store keyed by booking id — save(...)
// assigns an id when absent (id == 0) and stores it; findBookingByCustomerSession(...)
// returns every stored booking whose customerSession id matches the given id.
public class InMemoryBookingRepository implements BookingRepository {
    private Map<Long, Booking> bookingMap;
    private static long idCounter = 0;

    public InMemoryBookingRepository() {
        bookingMap = new HashMap<>();
    }

    @Override
    public Booking save(Booking booking) {
        return null;
    }

    @Override
    public List<Booking> findBookingByCustomerSession(long customerSessionId) {
        return null;
    }
}
