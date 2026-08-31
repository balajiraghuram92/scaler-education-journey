package org.example;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

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
        Lock seatTypeLock = seatTypeLocks.get(seatType);
        seatTypeLock.lock();
        try {
//            int available = availableSeats.getOrDefault(seatType, 0);
            int available = availableSeats.get(seatType);
            if (available >= numSeats) {
                availableSeats.put(seatType, available - numSeats);
                return true;
            } else {
                return false; // Not enough seats available
            }
        } finally {
            seatTypeLock.unlock();
        }
    }
    public int getAvailableSeats(String seatType) {
//        return availableSeats.getOrDefault(seatType, 0);
        return availableSeats.get(seatType);
    }
}
