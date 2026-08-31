package com.example.bookrooms.repositories;

import com.example.bookrooms.models.Room;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// TODO: implement RoomRepository as an in-memory store keyed by room id — save(...)
// assigns an id when absent (id == 0) and stores it; findById(...) returns the matching
// stored room wrapped in an Optional, or empty if no such id exists.
public class InMemoryRoomRepository implements RoomRepository {
    private Map<Long, Room> roomsMap;
    private static long idCounter = 0;

    public InMemoryRoomRepository() {
        roomsMap = new HashMap<>();
    }

    @Override
    public Room save(Room room) {
        return null;
    }

    @Override
    public Optional<Room> findById(long roomId) {
        return null;
    }
}
