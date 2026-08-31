package org.example;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

// TODO: implement reserveSeats(...) and getAvailableSeats(...) — each seat type has its
// own ReentrantLock (already built in the constructor), so reservations against
// different seat types can proceed fully in parallel while reservations against the
// SAME seat type are serialized. reserveSeats(...) should lock that seat type's lock,
// check-then-decrement availableSeats under the lock (true + deduct if enough remain,
// false otherwise), and unlock in a finally block.
public class ReservationSystem {
    private final Map<String,Integer> availableSeats;
    private final Map<String, Lock> seatTypeLocks;

    public ReservationSystem(Map<String, Integer> availableSeats) {
        this.availableSeats = new HashMap<>(availableSeats);
        this.seatTypeLocks = new HashMap<>();
        for (String seatType : availableSeats.keySet()) {
            seatTypeLocks.put(seatType, new ReentrantLock());
        }
    }

    public boolean reserveSeats(String seatType, int numSeats) {
        return false;
    }

    public int getAvailableSeats(String seatType) {
        return 0;
    }
}
