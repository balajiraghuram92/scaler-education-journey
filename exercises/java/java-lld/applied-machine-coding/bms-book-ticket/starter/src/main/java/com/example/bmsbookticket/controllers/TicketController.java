package com.example.bmsbookticket.controllers;

import com.example.bmsbookticket.dtos.BookTicketRequestDTO;
import com.example.bmsbookticket.dtos.BookTicketResponseDTO;
import com.example.bmsbookticket.services.TicketService;

// TODO: implement bookTicket — call TicketService with the request's show-seat ids and user id.
// On success return status SUCCESS with the ticket; on any exception return status FAILURE and
// no ticket.
public class TicketController {
    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    public BookTicketResponseDTO bookTicket(BookTicketRequestDTO requestDTO) {
        return null;
    }
}
