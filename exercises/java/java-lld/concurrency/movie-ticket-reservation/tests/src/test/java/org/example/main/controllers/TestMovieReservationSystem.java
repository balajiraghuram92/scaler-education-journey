package org.example.main.controllers;

import org.example.MovieReservationSystem;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TestMovieReservationSystem {

    @Test
    void testReserveSeats() {
        MovieReservationSystem reservationSystem = new MovieReservationSystem(200);

        assertTrue(reservationSystem.reserveSeats(10));
        assertEquals(190, reservationSystem.getAvailableSeats());

        assertTrue(reservationSystem.reserveSeats(50));
        assertEquals(140, reservationSystem.getAvailableSeats());

        assertFalse(reservationSystem.reserveSeats(300)); // Not enough seats available
        assertEquals(140, reservationSystem.getAvailableSeats());
    }

    @Test
    void testReserveSeatsConcurrent() throws InterruptedException {
        MovieReservationSystem reservationSystem = new MovieReservationSystem(20000);

        Thread thread1 = new Thread(() -> {
            reservationSystem.reserveSeats(5000);
        });

        Thread thread2 = new Thread(() -> {
            reservationSystem.reserveSeats(10000);
        });

        thread1.start();
        thread2.start();

        thread1.join();
        thread2.join();

        assertEquals(5000, reservationSystem.getAvailableSeats());
    }
}
