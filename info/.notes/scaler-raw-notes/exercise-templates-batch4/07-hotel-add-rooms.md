# Hotel Management System: Add Rooms

Source folder: `1773391491_d72199b6f2ab1cd9/Add_rooms-solution`

## Problem Statement

You are building a Hotel Management System. As a part of this system, you need to implement functionality using which hotel staff (ADMINs) can add the hotel rooms in the system.

## Detailed Requirements

1. The add room request contains the following details:
   - User id of the admin who is adding the room
   - Room name
   - Room description
   - Room price
   - Room Type (can be "deluxe" or "super_deluxe" or "suite")

2. Non-admin users should not be able to add a room. If a non-admin tries, the system returns an error.

3. Persist the room details in the database.

4. Once the room is added, the system returns the room instance in response.

## Architecture Overview

**Controller Layer:**
- `RoomController` - handles HTTP request to add room

**DTO Layer:**
- `AddRoomRequestDto` - input: userId, name, price, roomType, description
- `AddRoomResponseDto` - output: Room + ResponseStatus
- `ResponseStatus` - enum for SUCCESS/FAILURE

**Domain Models:**
- `BaseModel` - base class with id field
- `Room` - extends BaseModel; room details (roomNumber, price, roomType, description)
- `User` - user details (id, name, phone, password, userType)
- `UserType` - enum (ADMIN, CUSTOMER)
- `RoomType` - enum (DELUXE, SUPER_DELUXE, SUITE)
- `Customer` - customer model

**Repository Layer (Interfaces):**
- `RoomRepository` - add(Room), getRooms(), getRoomsByRoomType(RoomType), save(Room)
- `UserRepository` - findById(long userId), save(User)

**Repository Layer (Implementations):**
- `InMemoryRoomRepository` - in-memory HashMap-based storage
- `InMemoryUserRepository` - in-memory HashMap-based storage

**Service Layer:**
- `RoomService` (interface) - addRoom(userId, roomName, price, roomType, description)
- `RoomServiceImpl` (implementation) - validates user is admin, then saves room

**Exception Layer:**
- `UnAuthorizedAccess` - thrown when non-admin tries to add room
- `UserNotFoundException` - thrown when user doesn't exist

## Graded Contract (from tests)

From `RoomControllerTests.java`:

1. **Repository instantiation** (via reflection):
   - Must have `RoomRepository` implementation with no-arg constructor
   - Must have `UserRepository` implementation with no-arg constructor

2. **Service instantiation** (via reflection):
   - Must have `RoomService` implementation
   - Constructor must accept two arguments: RoomRepository and UserRepository (in that order)

3. **Test expectations:**
   - `addRoom(userId, roomName, price, roomType, description)` successfully:
     - Returns a persisted `Room` object with all fields set
     - Validates that user exists (throw `UserNotFoundException` if not)
     - Validates that user type is ADMIN (throw `UnAuthorizedAccess` if not)
   - Room is stored in repository and can be retrieved
   - Non-admin users (CUSTOMER type) cannot add rooms
   - Non-existent users cannot add rooms

## Learner Template

```java
package com.example.addroomshotelmanagement.repositories;

import com.example.addroomshotelmanagement.models.Room;
import com.example.addroomshotelmanagement.models.RoomType;
import java.util.List;

public interface RoomRepository {
    Room add(Room room);
    List<Room> getRooms();
    List<Room> getRoomsByRoomType(RoomType roomType);
    Room save(Room room);
}
```

```java
package com.example.addroomshotelmanagement.repositories;

import com.example.addroomshotelmanagement.models.User;
import java.util.Optional;

public interface UserRepository {
    Optional<User> findById(long userId);
    User save(User user);
}
```

```java
package com.example.addroomshotelmanagement.repositories;

import com.example.addroomshotelmanagement.models.Room;
import com.example.addroomshotelmanagement.models.RoomType;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class InMemoryRoomRepository implements RoomRepository {
    private Map<Long, Room> roomMap;
    private static long idCounter = 0;

    public InMemoryRoomRepository() {
        // Initialize in-memory storage
    }

    @Override
    public Room add(Room room) {
        // Store room in map and return
    }

    @Override
    public List<Room> getRooms() {
        // Return all rooms as a list
    }

    @Override
    public List<Room> getRoomsByRoomType(RoomType roomType) {
        // Filter and return rooms by type
    }

    @Override
    public Room save(Room room) {
        // Auto-generate ID if not set, store in map, return room
    }
}
```

```java
package com.example.addroomshotelmanagement.repositories;

import com.example.addroomshotelmanagement.models.User;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryUserRepository implements UserRepository {
    private Map<Long, User> userMap;
    private static long idCounter = 0;

    public InMemoryUserRepository() {
        // Initialize in-memory storage
    }

    @Override
    public Optional<User> findById(long userId) {
        // Return Optional with user if found, empty if not
    }

    @Override
    public User save(User user) {
        // Auto-generate ID if not set, store in map, return user
    }
}
```

```java
package com.example.addroomshotelmanagement.services;

import com.example.addroomshotelmanagement.exceptions.UnAuthorizedAccess;
import com.example.addroomshotelmanagement.exceptions.UserNotFoundException;
import com.example.addroomshotelmanagement.models.Room;

public interface RoomService {
    Room addRoom(long userId, String roomName, double price, String roomType, String description) throws UserNotFoundException, UnAuthorizedAccess;
}
```

```java
package com.example.addroomshotelmanagement.services;

import com.example.addroomshotelmanagement.exceptions.UnAuthorizedAccess;
import com.example.addroomshotelmanagement.exceptions.UserNotFoundException;
import com.example.addroomshotelmanagement.models.Room;
import com.example.addroomshotelmanagement.models.RoomType;
import com.example.addroomshotelmanagement.models.User;
import com.example.addroomshotelmanagement.models.UserType;
import com.example.addroomshotelmanagement.repositories.RoomRepository;
import com.example.addroomshotelmanagement.repositories.UserRepository;
import java.util.Optional;

public class RoomServiceImpl implements RoomService {
    private RoomRepository roomRepository;
    private UserRepository userRepository;

    public RoomServiceImpl(RoomRepository roomRepository, UserRepository userRepository) {
        // Store repositories
    }

    @Override
    public Room addRoom(long userId, String roomName, double price, String roomType, String description) throws UserNotFoundException, UnAuthorizedAccess {
        // 1. Find user by userId; throw UserNotFoundException if not found
        // 2. Check if user type is ADMIN; throw UnAuthorizedAccess if not
        // 3. Convert roomType string to RoomType enum
        // 4. Create new Room with provided details
        // 5. Save room using repository
        // 6. Return saved room
    }
}
```

## Deliberately Left Out (for the learner to design)

- **User validation logic** (verify user exists and is ADMIN)
- **Room type conversion** from string to enum
- **Room object creation** and field assignment
- **Auto-increment ID logic** in both repositories
- **Exception throwing** for authorization and user not found cases
- **Repository storage** implementation details (HashMap operations)
