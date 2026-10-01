package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.Seat;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicInteger;

public class InMemorySeatsRepository implements SeatsRepository {
    // Sorted by id so findAll() returns rows in insertion order, like a table scan on an identity key.
    private final Map<Integer, Seat> rows = new ConcurrentSkipListMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(0);

    @Override
    public Seat save(Seat seat) {
        if (seat.getId() == 0) {
            seat.setId(idCounter.incrementAndGet());
        }
        rows.put(seat.getId(), seat);
        return seat;
    }

    @Override
    public Optional<Seat> findById(int id) {
        return Optional.ofNullable(rows.get(id));
    }

    @Override
    public List<Seat> findAll() {
        return new ArrayList<>(rows.values());
    }
}
