package com.example.getrooms;

import com.example.getrooms.controllers.RoomController;
import com.example.getrooms.dtos.GetRoomsRequestDto;
import com.example.getrooms.dtos.GetRoomsResponseDto;
import com.example.getrooms.dtos.ResponseStatus;
import com.example.getrooms.models.Room;
import com.example.getrooms.models.RoomType;
import com.example.getrooms.repositories.RoomRepository;
import com.example.getrooms.services.RoomService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.Constructor;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;

class RoomsControllerTest {
    private RoomRepository roomRepository;
    private RoomService roomService;
    private RoomController roomController;

    @BeforeEach
    public void setupTest() throws Exception {
        initializeComponents();
    }

    private void initializeComponents() throws Exception {
        initializeRepositories();
        initializeRoomService();
        initializeRoomController();
    }

    private <T> T createInstance(Class<T> interfaceClass, Reflections reflections) throws Exception {
        Set<Class<? extends T>> implementations = reflections.getSubTypesOf(interfaceClass);
        if (implementations.isEmpty()) {
            throw new Exception("No implementation for " + interfaceClass.getSimpleName() + " found");
        }

        Class<? extends T> implementationClass = implementations.iterator().next();
        Constructor<? extends T> constructor = implementationClass.getDeclaredConstructor();
        constructor.setAccessible(true);
        return constructor.newInstance();
    }

    private <T> T createInstanceWithArgs(Class<T> interfaceClass, Reflections reflections, List<Object> dependencies) throws Exception {
        Set<Class<? extends T>> implementations = reflections.getSubTypesOf(interfaceClass);
        if (implementations.isEmpty()) {
            throw new Exception("No implementation for " + interfaceClass.getSimpleName() + " found");
        }
        Class<? extends T> implementationClass = implementations.iterator().next();
        Constructor<?>[] constructors = implementationClass.getConstructors();
        Constructor<?> constructor = Arrays.stream(constructors)
                .filter(constructor1 -> constructor1.getParameterCount() == dependencies.size())
                .findFirst().orElseThrow(() -> new Exception("No constructor with " + dependencies.size() + " arguments found"));
        constructor.setAccessible(true);
        Object[] args = new Object[constructor.getParameterCount()];
        for (int i = 0; i < constructor.getParameterCount(); i++) {
            for (Object dependency : dependencies) {
                if (constructor.getParameterTypes()[i].isInstance(dependency)) {
                    args[i] = dependency;
                    break;
                }
            }
        }
        return (T) constructor.newInstance(args);
    }

    private void initializeRepositories() throws Exception {
        Reflections repositoryReflections = new Reflections(RoomRepository.class.getPackageName(), new SubTypesScanner(false));
        this.roomRepository = createInstance(RoomRepository.class, repositoryReflections);
    }

    private void initializeRoomService() throws Exception {
        Reflections serviceReflections = new Reflections(RoomService.class.getPackageName(), new SubTypesScanner(false));
        this.roomService = createInstanceWithArgs(RoomService.class, serviceReflections, Collections.singletonList(roomRepository));
    }

    private void initializeRoomController() {
        this.roomController = new RoomController(this.roomService);
    }

    @Test
    public void testGetRoomsWithoutFilter() {
        addFewRooms();
        GetRoomsRequestDto requestDto = new GetRoomsRequestDto();
        requestDto.setRoomType(null);
        GetRoomsResponseDto responseDto = roomController.getRooms(requestDto);
        assertEquals(responseDto.getResponseStatus(), ResponseStatus.SUCCESS, "GetRoomsResponseDto status should be SUCCESS");
        assertEquals(responseDto.getRooms().size(), 6, "Number of rooms should be 6");
    }

    @Test
    public void testGetRoomsWithDeluxeFilter() {
        addFewRooms();
        GetRoomsRequestDto requestDto = new GetRoomsRequestDto();
        requestDto.setRoomType("DELUXE");
        GetRoomsResponseDto responseDto = roomController.getRooms(requestDto);
        assertEquals(responseDto.getResponseStatus(), ResponseStatus.SUCCESS, "GetRoomsResponseDto status should be SUCCESS");
        assertEquals(responseDto.getRooms().size(), 2, "Number of DELUXE rooms should be 2");
    }

    @Test
    public void testGetRoomsWithSuperDeluxeFilter() {
        addFewRooms();
        GetRoomsRequestDto requestDto = new GetRoomsRequestDto();
        requestDto.setRoomType("SUPER_DELUXE");
        GetRoomsResponseDto responseDto = roomController.getRooms(requestDto);
        assertEquals(responseDto.getResponseStatus(), ResponseStatus.SUCCESS, "GetRoomsResponseDto status should be SUCCESS");
        assertEquals(responseDto.getRooms().size(), 2, "Number of SUPER DELUXE rooms should be 2");
    }

    @Test
    public void testGetRoomsWithSuiteFilter() {
        addFewRooms();
        GetRoomsRequestDto requestDto = new GetRoomsRequestDto();
        requestDto.setRoomType("SUITE");
        GetRoomsResponseDto responseDto = roomController.getRooms(requestDto);
        assertEquals(responseDto.getResponseStatus(), ResponseStatus.SUCCESS, "GetRoomsResponseDto status should be SUCCESS");
        assertEquals(responseDto.getRooms().size(), 2, "Number of SUITE rooms should be 2");
    }

    private void addFewRooms() {
        Room room = new Room();
        room.setRoomNumber("A1");
        room.setDescription("Room number A1");
        room.setRoomType(RoomType.DELUXE);
        room.setPrice(5000.0);
        roomRepository.save(room);

        room = new Room();
        room.setRoomNumber("A2");
        room.setDescription("Room number A2");
        room.setRoomType(RoomType.SUPER_DELUXE);
        room.setPrice(7000.0);
        roomRepository.save(room);

        room = new Room();
        room.setRoomNumber("A3");
        room.setDescription("Room number A3");
        room.setRoomType(RoomType.SUITE);
        room.setPrice(10000.0);
        roomRepository.save(room);

        room = new Room();
        room.setRoomNumber("B1");
        room.setDescription("Room number B1");
        room.setRoomType(RoomType.DELUXE);
        room.setPrice(4000.0);
        roomRepository.save(room);

        room = new Room();
        room.setRoomNumber("B2");
        room.setDescription("Room number B2");
        room.setRoomType(RoomType.SUPER_DELUXE);
        room.setPrice(6000.0);
        roomRepository.save(room);

        room = new Room();
        room.setRoomNumber("B3");
        room.setDescription("Room number B3");
        room.setRoomType(RoomType.SUITE);
        room.setPrice(9000.0);
        roomRepository.save(room);
    }
}
