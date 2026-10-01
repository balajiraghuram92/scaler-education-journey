package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.Show;

import java.util.List;
import java.util.Optional;

public interface ShowRepository {
    Show save(Show show);

    Optional<Show> findById(int id);

    List<Show> findAll();
}
