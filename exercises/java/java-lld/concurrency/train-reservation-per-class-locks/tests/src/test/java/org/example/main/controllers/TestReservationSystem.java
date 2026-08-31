package org.example.main.controllers;

import org.example.ReservationSystem;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class TestReservationSystem{

    @Test
    void testReserveSeats() {
        Map<String, Integer> availableSeats = new HashMap<>();
        availableSeats.put("1AC", 50);
        availableSeats.put("2AC", 100);
        availableSeats.put("3AC", 150);
        availableSeats.put("Sleeper", 200);
        ReservationSystem reservationSystem = new ReservationSystem(availableSeats);

        assertTrue(reservationSystem.reserveSeats("1AC", 10));
        assertEquals(40, reservationSystem.getAvailableSeats("1AC"));

        assertFalse(reservationSystem.reserveSeats("2AC", 200)); // Not enough seats available
        assertEquals(100, reservationSystem.getAvailableSeats("2AC"));

        assertTrue(reservationSystem.reserveSeats("Sleeper", 100));
        assertEquals(100, reservationSystem.getAvailableSeats("Sleeper"));

        assertFalse(reservationSystem.reserveSeats("3AC", 300)); // No seats available
        assertEquals(150, reservationSystem.getAvailableSeats("3AC"));
    }

    @Test
    void testReserveSeatsConcurrent() throws InterruptedException {
        Map<String, Integer> availableSeats = new HashMap<>();
        availableSeats.put("1AC", 500);
        availableSeats.put("2AC", 100);
        availableSeats.put("3AC", 150);
        availableSeats.put("Sleeper", 200);
        ReservationSystem reservationSystem = new ReservationSystem(availableSeats);

        Thread thread1 = new Thread(() -> {
            for (int i = 0; i < 25; i++) {
                reservationSystem.reserveSeats("1AC", 1);
                reservationSystem.reserveSeats("2AC", 1);
                reservationSystem.reserveSeats("Sleeper",4);
            }
        });

        Thread thread2 = new Thread(() -> {
            for (int i = 0; i < 25; i++) {
                reservationSystem.reserveSeats("1AC", 2);
                reservationSystem.reserveSeats("2AC", 1);
                reservationSystem.reserveSeats("Sleeper", 4);
            }
        });

        thread1.start();
        thread2.start();

        thread1.join();
        thread2.join();





        assertEquals(425, reservationSystem.getAvailableSeats("1AC"));
        assertEquals(50, reservationSystem.getAvailableSeats("2AC"));
        assertEquals(150, reservationSystem.getAvailableSeats("3AC"));
        assertEquals(0, reservationSystem.getAvailableSeats("Sleeper"));
    }
}
