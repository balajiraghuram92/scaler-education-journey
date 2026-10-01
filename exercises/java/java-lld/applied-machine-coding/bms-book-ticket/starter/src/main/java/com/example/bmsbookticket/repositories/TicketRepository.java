package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.Ticket;

import java.util.List;
import java.util.Optional;

public interface TicketRepository {
    Ticket save(Ticket ticket);

    Optional<Ticket> findById(int id);

    List<Ticket> findAll();
}
