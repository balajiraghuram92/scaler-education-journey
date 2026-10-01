package com.example.bmsbookticket.services;

import com.example.bmsbookticket.exceptions.InvalidShowSeatException;
import com.example.bmsbookticket.exceptions.SeatsUnavailableException;
import com.example.bmsbookticket.exceptions.UserNotFoundException;
import com.example.bmsbookticket.models.SeatStatus;
import com.example.bmsbookticket.models.Show;
import com.example.bmsbookticket.models.ShowSeat;
import com.example.bmsbookticket.models.Ticket;
import com.example.bmsbookticket.models.TicketStatus;
import com.example.bmsbookticket.models.User;
import com.example.bmsbookticket.repositories.ShowSeatRepository;
import com.example.bmsbookticket.repositories.TicketRepository;
import com.example.bmsbookticket.repositories.UserRepository;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

public class TicketServiceImpl implements TicketService {
    private final ShowSeatRepository showSeatRepository;
    private final TicketRepository ticketRepository;
    private final UserRepository userRepository;

    // One lock per show: two requests for the same show serialize their check-and-block step,
    // while bookings for different shows never wait on each other. In the Spring/JPA version of
    // this exercise the same guarantee comes from a short SERIALIZABLE transaction (or
    // SELECT ... FOR UPDATE on the show_seat rows); a JVM lock only works because this
    // in-memory store lives inside a single process.
    private final ConcurrentHashMap<Integer, ReentrantLock> showLocks = new ConcurrentHashMap<>();

    public TicketServiceImpl(ShowSeatRepository showSeatRepository, TicketRepository ticketRepository,
                             UserRepository userRepository) {
        this.showSeatRepository = showSeatRepository;
        this.ticketRepository = ticketRepository;
        this.userRepository = userRepository;
    }

    @Override
    public Ticket bookTicket(List<Integer> showSeatIds, int userId)
            throws UserNotFoundException, InvalidShowSeatException, SeatsUnavailableException {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Invalid user: " + userId));

        if (showSeatIds == null || showSeatIds.isEmpty()) {
            throw new InvalidShowSeatException("At least one show seat must be requested");
        }

        List<ShowSeat> showSeats = showSeatRepository.findAllByIdIn(showSeatIds);
        if (showSeats.size() != showSeatIds.size()) {
            throw new InvalidShowSeatException("One or more show seat ids are invalid: " + showSeatIds);
        }

        Show show = showSeats.get(0).getShow();
        for (ShowSeat showSeat : showSeats) {
            if (showSeat.getShow().getId() != show.getId()) {
                throw new InvalidShowSeatException("All seats on one ticket must belong to the same show");
            }
        }

        ReentrantLock lock = showLocks.computeIfAbsent(show.getId(), id -> new ReentrantLock());
        lock.lock();
        try {
            // Check every seat before changing any of them: a request is all-or-nothing.
            List<Integer> unavailable = new ArrayList<>();
            for (ShowSeat showSeat : showSeats) {
                if (showSeat.getStatus() != SeatStatus.AVAILABLE) {
                    unavailable.add(showSeat.getId());
                }
            }
            if (!unavailable.isEmpty()) {
                throw new SeatsUnavailableException(unavailable);
            }

            for (ShowSeat showSeat : showSeats) {
                showSeat.setStatus(SeatStatus.BLOCKED);
                showSeatRepository.save(showSeat);
            }

            Ticket ticket = new Ticket();
            ticket.setSeats(showSeats.stream().map(ShowSeat::getSeat).collect(Collectors.toList()));
            ticket.setShow(show);
            ticket.setTimeOfBooking(new Date());
            ticket.setUser(user);
            ticket.setStatus(TicketStatus.UNPAID);
            return ticketRepository.save(ticket);
        } finally {
            lock.unlock();
        }
    }
}
