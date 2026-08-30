# Hotel Management System: Get Rooms

Source folder: `1773391498_173bf11a9ea80149/Get_rooms-solution`

## Problem Statement

You are building a Hotel Management System. As a part of this system, you need to implement functionality using which customers can browse the hotel rooms.

## Detailed Requirements

1. The get rooms request will accept an optional room type filter. The room type can be either "deluxe" or "super_deluxe" or "suite".

2. If an invalid room type is given, the system returns an error.

3. When a valid room type is given, fetch rooms from the database and filter by type, returning filtered results.

4. If room type is not given (null), return all rooms in the response.

## Architecture Overview

**Controller Layer:**
- `RoomController` - handles HTTP request to get/browse rooms

**DTO Layer:**
- `GetRoomsRequestDto` - input: roomType (optional String)
- `GetRoomsResponseDto` - output: List<Room> + ResponseStatus
- `ResponseStatus` - enum for SUCCESS/FAILURE

**Domain Models:**
- `BaseModel` - base class with id field
- `Room` - extends BaseModel; room details (roomNumber, price, roomType, description)
- `User` - user model
- `RoomType` - enum (DELUXE, SUPER_DELUXE, SUITE)

**Repository Layer (Interfaces):**
- `RoomRepository` - getRooms(), getRoomsByRoomType(RoomType)

**Repository Layer (Implementations):**
- `InMemoryRoomRepositoryImpl` - in-memory HashMap-based storage

**Service Layer:**
- `RoomService` (interface) - getRooms(String roomType)
- `RoomServiceImpl` (implementation) - returns filtered or all rooms

## Graded Contract (from tests)

From `RoomsControllerTest.java`:

1. **Repository instantiation** (via reflection):
   - Must have `RoomRepository` implementation with no-arg constructor

2. **Service instantiation** (via reflection):
   - Must have `RoomService` implementation
   - Constructor must accept one argument: RoomRepository

3. **Test expectations:**
   - `getRooms(null)` returns ALL rooms in repository
   - `getRooms("DELUXE")` returns only DELUXE rooms
   - `getRooms("SUPER_DELUXE")` returns only SUPER_DELUXE rooms
   - `getRooms("SUITE")` returns only SUITE rooms
   - Returns ResponseStatus.SUCCESS for all valid/null types
   - Invalid types or filtering errors return ResponseStatus.FAILURE

## Learner Template

```java
package com.example.getrooms.repositories;

import com.example.getrooms.models.Room;
import com.example.getrooms.models.RoomType;
import java.util.List;

public interface RoomRepository {
    List<Room> getRooms();
    List<Room> getRoomsByRoomType(RoomType roomType);
}
```

```java
package com.example.getrooms.repositories;

import com.example.getrooms.models.Room;
import com.example.getrooms.models.RoomType;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class InMemoryRoomRepositoryImpl implements RoomRepository {
    private Map<Long, Room> roomMap;
    private static long idCounter = 0;

    public InMemoryRoomRepositoryImpl() {
        // Initialize in-memory storage
    }

    @Override
    public List<Room> getRooms() {
        // Return all rooms as a list
    }

    @Override
    public List<Room> getRoomsByRoomType(RoomType roomType) {
        // Filter and return rooms matching the specified type
    }

    // Additional method for test setup
    public Room save(Room room) {
        // Auto-generate ID if not set, store in map, return room
    }
}
```

```java
package com.example.getrooms.services;

import com.example.getrooms.models.Room;
import java.util.List;

public interface RoomService {
    List<Room> getRooms(String roomType);
}
```

```java
package com.example.getrooms.services;

import com.example.getrooms.models.Room;
import com.example.getrooms.models.RoomType;
import com.example.getrooms.repositories.RoomRepository;
import java.util.List;

public class RoomServiceImpl implements RoomService {
    private RoomRepository roomRepository;

    public RoomServiceImpl(RoomRepository roomRepository) {
        // Store repository
    }

    @Override
    public List<Room> getRooms(String roomType) {
        // If roomType is null, return all rooms
        // Otherwise, convert string to RoomType enum and return filtered rooms
        // Handle invalid room type gracefully
    }
}
```

## Deliberately Left Out (for the learner to design)

- **Null-check logic** to distinguish between "no filter" and invalid input
- **String-to-enum conversion** for room type validation
- **Filtering logic** for returning only rooms of specified type
- **Exception handling** for invalid room types (if needed)
- **Auto-increment ID logic** in repository
- **Repository storage implementation** (HashMap operations)
- **List filtering** using streams or loops
