package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.ShowSeat;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class InMemoryShowSeatRepository implements ShowSeatRepository {
    // Sorted by id so findAll() returns rows in insertion order, like a table scan on an identity key.
    private final Map<Integer, ShowSeat> rows = new ConcurrentSkipListMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(0);

    @Override
    public ShowSeat save(ShowSeat showSeat) {
        if (showSeat.getId() == 0) {
            showSeat.setId(idCounter.incrementAndGet());
        }
        rows.put(showSeat.getId(), showSeat);
        return showSeat;
    }

    @Override
    public Optional<ShowSeat> findById(int id) {
        return Optional.ofNullable(rows.get(id));
    }

    @Override
    public List<ShowSeat> findAll() {
        return new ArrayList<>(rows.values());
    }

    @Override
    public List<ShowSeat> findAllByIdIn(List<Integer> ids) {
        return ids.stream()
                .distinct()
                .map(rows::get)
                .filter(showSeat -> showSeat != null)
                .collect(Collectors.toList());
    }
}
