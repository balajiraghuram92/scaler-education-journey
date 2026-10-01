package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.Ticket;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicInteger;

public class InMemoryTicketRepository implements TicketRepository {
    // Sorted by id so findAll() returns rows in insertion order, like a table scan on an identity key.
    private final Map<Integer, Ticket> rows = new ConcurrentSkipListMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(0);

    @Override
    public Ticket save(Ticket ticket) {
        if (ticket.getId() == 0) {
            ticket.setId(idCounter.incrementAndGet());
        }
        rows.put(ticket.getId(), ticket);
        return ticket;
    }

    @Override
    public Optional<Ticket> findById(int id) {
        return Optional.ofNullable(rows.get(id));
    }

    @Override
    public List<Ticket> findAll() {
        return new ArrayList<>(rows.values());
    }
}
