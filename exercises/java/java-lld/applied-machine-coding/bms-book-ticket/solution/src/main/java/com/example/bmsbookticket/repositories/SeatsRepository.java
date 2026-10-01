package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.Seat;

import java.util.List;
import java.util.Optional;

public interface SeatsRepository {
    Seat save(Seat seat);

    Optional<Seat> findById(int id);

    List<Seat> findAll();
}
