package com.example.getrooms.repositories;

import com.example.getrooms.models.Room;
import com.example.getrooms.models.RoomType;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

// TODO: implement RoomRepository as an in-memory store keyed by room id — add(...) and
// save(...) should both assign an id when the room doesn't already have one (id == 0)
// and store it in the map; getRooms() returns every stored room; getRoomsByRoomType(...)
// filters the stored rooms down to the given RoomType.
public class InMemoryRoomRepositoryImpl implements RoomRepository {
    private Map<Long, Room> roomsMap;
    private static long idCounter = 0;

    public InMemoryRoomRepositoryImpl() {
        roomsMap = new HashMap<>();
    }

    @Override
    public Room add(Room room) {
        return null;
    }

    @Override
    public List<Room> getRooms() {
        return null;
    }

    @Override
    public List<Room> getRoomsByRoomType(RoomType roomType) {
        return null;
    }

    @Override
    public Room save(Room room) {
        return null;
    }
}
