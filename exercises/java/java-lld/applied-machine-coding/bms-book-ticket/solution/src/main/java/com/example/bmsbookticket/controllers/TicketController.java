package com.example.bmsbookticket.controllers;

import com.example.bmsbookticket.dtos.BookTicketRequestDTO;
import com.example.bmsbookticket.dtos.BookTicketResponseDTO;
import com.example.bmsbookticket.dtos.ResponseStatus;
import com.example.bmsbookticket.models.Ticket;
import com.example.bmsbookticket.services.TicketService;

public class TicketController {
    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    public BookTicketResponseDTO bookTicket(BookTicketRequestDTO requestDTO) {
        BookTicketResponseDTO responseDTO = new BookTicketResponseDTO();
        try {
            Ticket ticket = ticketService.bookTicket(requestDTO.getShowSeatIds(), requestDTO.getUserId());
            responseDTO.setTicket(ticket);
            responseDTO.setStatus(ResponseStatus.SUCCESS);
        } catch (Exception e) {
            responseDTO.setStatus(ResponseStatus.FAILURE);
        }
        return responseDTO;
    }
}
