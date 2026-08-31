package com.example.bookrooms.services;

import com.example.bookrooms.exceptions.InvalidRoomException;
import com.example.bookrooms.exceptions.UserNotFoundException;
import com.example.bookrooms.models.*;
import com.example.bookrooms.repositories.BookingRepository;
import com.example.bookrooms.repositories.CustomerSessionRepository;
import com.example.bookrooms.repositories.RoomRepository;
import com.example.bookrooms.repositories.UserRepository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// TODO: implement makeBooking —
//  1. look for an ACTIVE CustomerSession for this userId; if none exists, look up the
//     user (throwing UserNotFoundException("User not found") if absent), create a new
//     ACTIVE CustomerSession for them, and save it.
//  2. build a Booking against that session; for each (roomId, quantity) pair in
//     roomsToBeBooked, look the room up (throwing InvalidRoomException("Room doesn't
//     exist") if any room id is unknown) and record it in a Map<Room, Integer>.
//  3. save the Booking and return it.
public class BookingServiceImpl implements BookingService {
    private CustomerSessionRepository customerSessionRepository;
    private UserRepository userRepository;
    private RoomRepository roomRepository;
    private BookingRepository bookingRepository;

    public  BookingServiceImpl(CustomerSessionRepository customerSessionRepository, UserRepository userRepository,
                               RoomRepository roomRepository, BookingRepository bookingRepository) {
        this.customerSessionRepository = customerSessionRepository;
        this.userRepository = userRepository;
        this.roomRepository = roomRepository;
        this.bookingRepository = bookingRepository;
    }

    @Override
    public Booking makeBooking(long userId, Map<Long, Integer> roomsToBeBooked) throws UserNotFoundException, InvalidRoomException {
        return null;
    }
}
