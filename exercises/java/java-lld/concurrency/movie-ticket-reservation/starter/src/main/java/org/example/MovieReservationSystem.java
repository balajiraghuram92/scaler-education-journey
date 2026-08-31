package org.example;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

// TODO: implement reserveSeats(...) — guard the check-then-decrement with
// reservationLock (lock in a try block, unlock in a finally block) so concurrent
// callers can't both pass the availability check before either decrements
// availableSeats. Return true and deduct numSeats if enough seats remain, false
// (leaving availableSeats unchanged) otherwise.
public class MovieReservationSystem {
    private int availableSeats;
    private final Lock reservationLock;

    public MovieReservationSystem(int totalSeats) {
        this.availableSeats = totalSeats;
        this.reservationLock = new ReentrantLock();
    }

    public boolean reserveSeats(int numSeats) {
        return false;
    }

    public int getAvailableSeats() {
        return availableSeats;
    }
}
