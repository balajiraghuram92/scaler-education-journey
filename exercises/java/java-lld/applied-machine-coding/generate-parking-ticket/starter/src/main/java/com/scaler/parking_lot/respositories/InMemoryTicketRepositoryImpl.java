package com.scaler.parking_lot.respositories;

import com.scaler.parking_lot.models.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryTicketRepositoryImpl implements TicketRepository{
    private Map<Long, Ticket> ticketMap;
    private static int id = 0;

    public InMemoryTicketRepositoryImpl() {
        this.ticketMap = new HashMap<>();
    }

    public Ticket save(Ticket ticket) {
        // TODO: Save ticket to memory with auto-increment id if id is 0
        return null;
    }

    @Override
    public Optional<Ticket> getTicketById(long ticketId) {
        // TODO: Look up ticket by id
        return Optional.empty();
    }

}
