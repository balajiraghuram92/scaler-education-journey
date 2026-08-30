# Java Singleton - Configuration Manager

Source folder: `1773391183_58ec9337927b5b99/Java_Singleton_E-solution`

## Problem Statement

Implement the Singleton design pattern for a file-based configuration manager. The configuration manager must be thread-safe and ensure only one instance exists throughout the application lifecycle. 

Extend the abstract `FileBasedConfigurationManager` class to create a concrete implementation that implements:
- Singleton pattern with getInstance() and resetInstance()
- Configuration retrieval and storage with type conversion
- File-based property loading

## Graded Contract (from tests)

From `FileBasedConfigurationManagerTest.java`, the following must be present and function correctly:

- **Class extending `FileBasedConfigurationManager`** (abstract base)
  - Must be a concrete (non-abstract) subclass of `FileBasedConfigurationManager`
  - Must NOT have a public constructor (private or package-private)
  - Must have a static `getInstance()` method that returns `FileBasedConfigurationManager`
  - Must have a static `resetInstance()` method (void return type)
  - getInstance() must return the same instance on multiple calls (singleton)
  - getInstance() must be thread-safe (returns same instance from multiple threads)
  - resetInstance() must clear the singleton instance (next getInstance() call returns new instance)

- **Abstract Methods to Implement** (from `FileBasedConfigurationManager`)
  - `String getConfiguration(String key)`
  - `<T> T getConfiguration(String key, Class<T> type)`
  - `void setConfiguration(String key, String value)`
  - `<T> void setConfiguration(String key, T value)`
  - `void removeConfiguration(String key)`
  - `void clear()`

## Learner Template

```java
package com.assignment.question;

public class FileBasedConfigurationManagerImpl extends FileBasedConfigurationManager {
    
    private static volatile FileBasedConfigurationManagerImpl instance = null;
    
    private FileBasedConfigurationManagerImpl() {
        super();
    }
    
    public static FileBasedConfigurationManager getInstance() {
        // TODO: implement double-checked locking singleton pattern
    }
    
    public static void resetInstance() {
        // TODO: implement
    }
    
    @Override
    public String getConfiguration(String key) {
        // TODO: implement
    }
    
    @Override
    public <T> T getConfiguration(String key, Class<T> type) {
        // TODO: implement (use convert() helper from parent class)
    }
    
    @Override
    public void setConfiguration(String key, String value) {
        // TODO: implement
    }
    
    @Override
    public <T> void setConfiguration(String key, T value) {
        // TODO: implement
    }
    
    @Override
    public void removeConfiguration(String key) {
        // TODO: implement
    }
    
    @Override
    public void clear() {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Double-checked locking synchronization logic
- Implementation details of type conversion (convert() method is in parent class)
- Property storage and retrieval mechanism (use getProperties() from parent)
- Null-handling and Optional usage for type conversion
- toString() conversion for setConfiguration(key, T value)
- Any additional helper methods or caching strategies
