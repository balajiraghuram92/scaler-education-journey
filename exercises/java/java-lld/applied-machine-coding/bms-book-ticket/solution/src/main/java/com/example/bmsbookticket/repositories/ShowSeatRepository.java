package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.ShowSeat;

import java.util.List;
import java.util.Optional;

public interface ShowSeatRepository {
    ShowSeat save(ShowSeat showSeat);

    Optional<ShowSeat> findById(int id);

    List<ShowSeat> findAll();

    List<ShowSeat> findAllByIdIn(List<Integer> ids);
}
