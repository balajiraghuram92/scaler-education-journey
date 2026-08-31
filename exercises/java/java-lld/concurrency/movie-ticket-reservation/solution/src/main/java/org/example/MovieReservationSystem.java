package org.example;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class MovieReservationSystem {
    private int availableSeats;
    private final Lock reservationLock;

    public MovieReservationSystem(int totalSeats) {
        this.availableSeats = totalSeats;
        this.reservationLock = new ReentrantLock();
    }

    public boolean reserveSeats(int numSeats) {
        reservationLock.lock();
        try {
            if (availableSeats >= numSeats) {
                availableSeats -= numSeats;
                return true;
            }
            return false; // Not enough seats available
        } finally {
            reservationLock.unlock();
        }
    }

    public int getAvailableSeats() {
        return availableSeats;
    }
}
