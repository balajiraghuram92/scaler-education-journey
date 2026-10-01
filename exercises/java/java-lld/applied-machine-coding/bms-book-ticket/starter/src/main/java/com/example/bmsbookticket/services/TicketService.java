package com.example.bmsbookticket.services;

import com.example.bmsbookticket.exceptions.InvalidShowSeatException;
import com.example.bmsbookticket.exceptions.SeatsUnavailableException;
import com.example.bmsbookticket.exceptions.UserNotFoundException;
import com.example.bmsbookticket.models.Ticket;

import java.util.List;

public interface TicketService {
    Ticket bookTicket(List<Integer> showSeatIds, int userId)
            throws UserNotFoundException, InvalidShowSeatException, SeatsUnavailableException;
}
