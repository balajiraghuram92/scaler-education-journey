package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.Show;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicInteger;

public class InMemoryShowRepository implements ShowRepository {
    // Sorted by id so findAll() returns rows in insertion order, like a table scan on an identity key.
    private final Map<Integer, Show> rows = new ConcurrentSkipListMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(0);

    @Override
    public Show save(Show show) {
        if (show.getId() == 0) {
            show.setId(idCounter.incrementAndGet());
        }
        rows.put(show.getId(), show);
        return show;
    }

    @Override
    public Optional<Show> findById(int id) {
        return Optional.ofNullable(rows.get(id));
    }

    @Override
    public List<Show> findAll() {
        return new ArrayList<>(rows.values());
    }
}
