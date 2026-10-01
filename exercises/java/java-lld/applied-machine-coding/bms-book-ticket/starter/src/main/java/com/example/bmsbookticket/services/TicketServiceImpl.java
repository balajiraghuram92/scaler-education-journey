package com.example.bmsbookticket.services;

import com.example.bmsbookticket.exceptions.InvalidShowSeatException;
import com.example.bmsbookticket.exceptions.SeatsUnavailableException;
import com.example.bmsbookticket.exceptions.UserNotFoundException;
import com.example.bmsbookticket.models.Ticket;
import com.example.bmsbookticket.repositories.ShowSeatRepository;
import com.example.bmsbookticket.repositories.TicketRepository;
import com.example.bmsbookticket.repositories.UserRepository;

import java.util.List;

// TODO: implement bookTicket —
//  1. the user must exist (UserNotFoundException);
//  2. every requested show-seat id must exist and all of them must belong to the same show
//     (InvalidShowSeatException otherwise);
//  3. all-or-nothing: if ANY requested seat is not AVAILABLE, change nothing and throw
//     SeatsUnavailableException listing exactly the unavailable show-seat ids;
//  4. otherwise mark every requested seat BLOCKED and save a Ticket (status UNPAID, the booked
//     seats, the show, the user, timeOfBooking = now), then return it.
//  Many requests can arrive at once for the same seats. Make the check in step 3 and the write
//  in step 4 a single critical section so two requests can never both see a seat as AVAILABLE,
//  without making bookings for unrelated shows wait on each other.
public class TicketServiceImpl implements TicketService {
    private final ShowSeatRepository showSeatRepository;
    private final TicketRepository ticketRepository;
    private final UserRepository userRepository;

    public TicketServiceImpl(ShowSeatRepository showSeatRepository, TicketRepository ticketRepository,
                             UserRepository userRepository) {
        this.showSeatRepository = showSeatRepository;
        this.ticketRepository = ticketRepository;
        this.userRepository = userRepository;
    }

    @Override
    public Ticket bookTicket(List<Integer> showSeatIds, int userId)
            throws UserNotFoundException, InvalidShowSeatException, SeatsUnavailableException {
        return null;
    }
}
