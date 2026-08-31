package com.example.getrooms.services;

import com.example.getrooms.models.Room;
import com.example.getrooms.models.RoomType;
import com.example.getrooms.repositories.RoomRepository;

import java.util.List;

// TODO: implement RoomService — when roomType is null return every room from the
// repository, otherwise parse it into a RoomType and delegate to
// roomRepository.getRoomsByRoomType(...).
public class RoomServiceImpl implements RoomService {
    private RoomRepository roomRepository;

    public RoomServiceImpl(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    @Override
    public List<Room> getRooms(String roomType) {
        return null;
    }
}
