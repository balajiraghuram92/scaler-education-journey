# Integrate Cloud Service Provider for Our Project

Source folder: 1773391505_0e5b753500a0415d/Integrate_Cloud_-solution

## Problem Statement

You are building a Web Project. As a part of this system, you need to integrate AWS and Google as cloud service providers into your system.

## Detailed Requirements

1. Make connection request functionality will get user id as input.
2. If an invalid user id is given to this functionality, we should get an error saying "User not found".
3. When a valid user id is given, you need to get the user details stored in the database and make a call to cloud Providers (AWS or Google) to call the Cloud API's to initiate the connection. Once the processing is completes, it will return us some details about the connection, out of all these details we need to extract the connection id and connection status and return it in the response.
4. We need to implement the cloud providers integration in such a way that it should be very easy for us to migrate from 1 cloud to another.

## Detailed Instructions

- Refer the `createConnection` method inside `CloudController` class.
- Refer the libraries package to understand the AWS and Google libraries.
- Refer the `CreateConnectionRequestDto` and `CreateConnectionResponseDto` for understanding the expected input and output to the functionality.
- Refer the `CloudAdapter` interface and see how it can be used in this scenario.
- Refer the models package to understand the models.
- Implement the `CloudService` and `UserRepository` interfaces to achieve the above requirements.
- Implement an in memory database for storing the user details.
- Do not modify existing methods and their parameters for interfaces, feel free to add more methods if required.

## Graded Contract (from tests)

- **CloudAdapter interface** with method `Connection createConnection(long userId)`
- **AWSAdapter implements CloudAdapter** — must have AWSApi field, must implement createConnection mapping AWS response to Connection
- **GoogleAdapter implements CloudAdapter** — must have GoogleApi field, must implement createConnection mapping Google response to Connection
- **CloudService interface** with method `Connection createConnection(Long userId) throws UserNotFoundException`
- **CloudServiceImpl implements CloudService** — must accept UserRepository and CloudAdapter in constructor, must throw UserNotFoundException if user not found
- **UserRepository interface** with methods:
  - `User save(User user)`
  - `Optional<User> findUserById(long userId)`
- **InMemoryUserRepositoryImpl implements UserRepository** — in-memory HashMap-based storage
- **CloudController** accepts CloudService in constructor, method `createConnection(CreateConnectionRequestDto)` returns CreateConnectionResponseDto with SUCCESS/FAILURE status
- **User model** with name, password, extends BaseModel with id
- **Connection model** with connectionId, connectionStatus, userId
- **CreateConnectionRequestDto** with userId getter/setter
- **CreateConnectionResponseDto** with connectionId, connectionStatus, responseStatus (SUCCESS/FAILURE)
- **UserNotFoundException** with message "User not found"

## Learner Template

### Interfaces

```java
// CloudAdapter.java
package com.example.cloudproviders.adapters;

import com.example.cloudproviders.models.Connection;

public interface CloudAdapter {
    Connection createConnection(long userId);
}

// CloudService.java
package com.example.cloudproviders.services;

import com.example.cloudproviders.exceptions.UserNotFoundException;
import com.example.cloudproviders.models.Connection;

public interface CloudService {
    Connection createConnection(Long userId) throws UserNotFoundException;
}

// UserRepository.java
package com.example.cloudproviders.repositories;

import com.example.cloudproviders.models.User;
import java.util.Optional;

public interface UserRepository {
    User save(User user);
    Optional<User> findUserById(long userId);
}
```

### Adapter Implementations

```java
// AWSAdapter.java
package com.example.cloudproviders.adapters;

import com.example.cloudproviders.libraries.aws.AWSApi;
import com.example.cloudproviders.libraries.aws.AWSConnectionResponse;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.models.ConnectionStatus;

public class AWSAdapter implements CloudAdapter {
    private AWSApi awsApi;

    public AWSAdapter() {
        this.awsApi = new AWSApi();
    }

    @Override
    public Connection createConnection(long userId) {
        // TODO: Call awsApi.createConnection(userId)
        // TODO: Map AWSConnectionResponse to Connection object
        // TODO: Extract connectionId and connectionStatus
    }
}

// GoogleAdapter.java
package com.example.cloudproviders.adapters;

import com.example.cloudproviders.libraries.google.GoogleApi;
import com.example.cloudproviders.libraries.google.GoogleConnectionResponse;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.models.ConnectionStatus;

public class GoogleAdapter implements CloudAdapter {
    private GoogleApi googleApi;

    public GoogleAdapter() {
        this.googleApi = new GoogleApi();
    }

    @Override
    public Connection createConnection(long userId) {
        // TODO: Call googleApi.createConnection(userId)
        // TODO: Map GoogleConnectionResponse to Connection object
        // TODO: Extract connectionId and connectionStatus
    }
}
```

### Repository Implementation

```java
// InMemoryUserRepositoryImpl.java
package com.example.cloudproviders.repositories;

import com.example.cloudproviders.models.User;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryUserRepositoryImpl implements UserRepository {
    private Map<Long, User> userMap;

    public InMemoryUserRepositoryImpl() {
        this.userMap = new HashMap<>();
    }

    @Override
    public User save(User user) {
        // TODO: Implement auto-increment ID if user.id == 0
        // TODO: Store in userMap and return user
    }

    @Override
    public Optional<User> findUserById(long userId) {
        // TODO: Return Optional containing user if found, empty Optional otherwise
    }
}
```

### Service Implementation

```java
// CloudServiceImpl.java
package com.example.cloudproviders.services;

import com.example.cloudproviders.adapters.CloudAdapter;
import com.example.cloudproviders.exceptions.UserNotFoundException;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.models.User;
import com.example.cloudproviders.repositories.UserRepository;

public class CloudServiceImpl implements CloudService {
    private UserRepository userRepository;
    private CloudAdapter cloudAdapter;

    public CloudServiceImpl(UserRepository userRepository, CloudAdapter cloudAdapter) {
        this.userRepository = userRepository;
        this.cloudAdapter = cloudAdapter;
    }

    @Override
    public Connection createConnection(Long userId) throws UserNotFoundException {
        // TODO: Find user by userId using userRepository
        // TODO: Throw UserNotFoundException if user not found
        // TODO: Call cloudAdapter.createConnection(userId)
        // TODO: Return the Connection object
    }
}
```

### Controller

```java
// CloudController.java
package com.example.cloudproviders.controllers;

import com.example.cloudproviders.dtos.CreateConnectionRequestDto;
import com.example.cloudproviders.dtos.CreateConnectionResponseDto;
import com.example.cloudproviders.dtos.ResponseStatus;
import com.example.cloudproviders.exceptions.UserNotFoundException;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.services.CloudService;

public class CloudController {
    private CloudService cloudService;

    public CloudController(CloudService cloudService) {
        this.cloudService = cloudService;
    }

    public CreateConnectionResponseDto createConnection(CreateConnectionRequestDto createConnectionRequestDto) {
        CreateConnectionResponseDto responseDto = new CreateConnectionResponseDto();
        try {
            // TODO: Call cloudService.createConnection() with userId from request
            // TODO: Extract connectionId and connectionStatus from Connection
            // TODO: Set SUCCESS status
        } catch (UserNotFoundException e) {
            // TODO: Set FAILURE status and leave connectionId/connectionStatus as null
        }
        return responseDto;
    }
}
```

### Models

```java
// User.java
package com.example.cloudproviders.models;

public class User extends BaseModel {
    private String name;
    private String password;

    public String getName() {
        // TODO: Implement getter
    }

    public void setName(String name) {
        // TODO: Implement setter
    }

    public String getPassword() {
        // TODO: Implement getter
    }

    public void setPassword(String password) {
        // TODO: Implement setter
    }
}

// Connection.java
package com.example.cloudproviders.models;

public class Connection extends BaseModel {
    private String connectionId;
    private ConnectionStatus connectionStatus;
    private long userId;

    public String getConnectionId() {
        // TODO: Implement getter
    }

    public void setConnectionId(String connectionId) {
        // TODO: Implement setter
    }

    public ConnectionStatus getConnectionStatus() {
        // TODO: Implement getter
    }

    public void setConnectionStatus(ConnectionStatus connectionStatus) {
        // TODO: Implement setter
    }

    public long getUserId() {
        // TODO: Implement getter
    }

    public void setUserId(long userId) {
        // TODO: Implement setter
    }
}

// BaseModel.java
package com.example.cloudproviders.models;

public class BaseModel {
    private long id;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }
}

// ConnectionStatus.java
package com.example.cloudproviders.models;

public enum ConnectionStatus {
    ACTIVE,
    INACTIVE
}
```

### DTOs

```java
// CreateConnectionRequestDto.java
package com.example.cloudproviders.dtos;

public class CreateConnectionRequestDto {
    private long userId;

    public long getUserId() {
        // TODO: Implement getter
    }

    public void setUserId(long userId) {
        // TODO: Implement setter
    }
}

// CreateConnectionResponseDto.java
package com.example.cloudproviders.dtos;

import com.example.cloudproviders.models.ConnectionStatus;

public class CreateConnectionResponseDto {
    private String connectionId;
    private ResponseStatus responseStatus;
    private ConnectionStatus connectionStatus;

    public String getConnectionId() {
        // TODO: Implement getter
    }

    public void setConnectionId(String connectionId) {
        // TODO: Implement setter
    }

    public ResponseStatus getResponseStatus() {
        // TODO: Implement getter
    }

    public void setResponseStatus(ResponseStatus responseStatus) {
        // TODO: Implement setter
    }

    public ConnectionStatus getConnectionStatus() {
        // TODO: Implement getter
    }

    public void setConnectionStatus(ConnectionStatus connectionStatus) {
        // TODO: Implement setter
    }
}

// ResponseStatus.java
package com.example.cloudproviders.dtos;

public enum ResponseStatus {
    SUCCESS,
    FAILURE
}
```

### Exceptions

```java
// UserNotFoundException.java
package com.example.cloudproviders.exceptions;

public class UserNotFoundException extends Exception {
    public UserNotFoundException(String message) {
        super(message);
    }
}
```

## Deliberately Left Out (for the learner to design)

- Specific API calls in AWSAdapter and GoogleAdapter (AWS/Google library code is provided)
- Response mapping logic from cloud provider responses to Connection objects
- Auto-increment ID logic details in InMemoryUserRepositoryImpl
- Error handling beyond UserNotFoundException
- Logging and monitoring
- Connection pooling or caching strategies
- Additional methods on services/repositories beyond what interface defines
- Spring/DI configuration (if using Spring)
