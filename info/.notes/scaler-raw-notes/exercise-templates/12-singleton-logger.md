# Singleton Pattern for Logger

Source folder: `1773391274_84e5d5920da94111/Singleton_Log-solution`

## Problem Statement

You are tasked with developing a logging module for a complex software application. The logging module needs to maintain a single log file throughout the application's execution to avoid file access conflicts and ensure consistency. To prevent multiple instances of the logging module and ensure thread-safe access to the log file, you need to implement the Singleton design pattern along with the logging functionality.

Your task is to implement the `Logger` interface that follows the Singleton design pattern to manage logging operations and maintain a single log file.

## Graded Contract (from tests)

- **Interface `Logger`**
  - Method: `void log(LogLevel level, String message)` — logs a message with a level
  - Method: `void setLogFile(String filePath)` — sets the log file path
  - Method: `String getLogFile()` — returns the current log file path
  - Method: `void flush()` — flushes buffered log entries to file
  - Method: `void close()` — closes the logger and releases resources

- **Implementation of `Logger`** (must be the only non-abstract implementation)
  - Constructor: must be private (no public constructors)
  - Static method: `getInstance()` — returns singleton Logger instance (thread-safe)
  - Static method: `resetInstance()` — resets the singleton instance to null

- **Singleton contract details**
  - Multiple calls to getInstance() must return the same instance
  - getInstance() must be thread-safe (tested with 10 concurrent threads)
  - resetInstance() must allow getInstance() to return a new instance
  - Constructor must be private (reflection check for non-public constructors)

- **Logging contract details**
  - log() must throw IllegalStateException if setLogFile() was not called
  - log() must write to file with format including timestamp, level, and message
  - setLogFile() initializes file writer for the given path
  - getLogFile() returns the path set via setLogFile()
  - flush() must call flush on underlying writer
  - close() must close underlying writer and make log() throw IllegalStateException

## Learner Template

```java
package com.assignment.question;

import org.springframework.boot.logging.LogLevel;

public interface Logger {
    void log(LogLevel level, String message);

    void setLogFile(String filePath);

    String getLogFile();

    void flush();

    void close();
}
```

```java
package com.assignment.question;

import org.springframework.boot.logging.LogLevel;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class LoggerImpl implements Logger {
    private static volatile Logger instance = null;
    private String logFilePath;
    private PrintWriter logWriter;

    private LoggerImpl() {
        // TODO: implement - private constructor for singleton
    }

    public static synchronized Logger getInstance() {
        // TODO: implement - double-checked locking pattern for thread-safe singleton
    }

    public static void resetInstance() {
        // TODO: implement - reset instance to null
    }

    @Override
    public void log(LogLevel level, String message) {
        // TODO: implement - throw IllegalStateException if logWriter is null
        // Format: [timestamp] [level] message
    }

    @Override
    public String getLogFile() {
        // TODO: implement
    }

    @Override
    public void setLogFile(String filePath) {
        // TODO: implement - close old writer if exists, then open new FileWriter
    }

    @Override
    public void flush() {
        // TODO: implement - call flush on logWriter if not null
    }

    @Override
    public void close() {
        // TODO: implement - close logWriter if not null, set to null
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field declarations (logFilePath, logWriter)
- Private constructor implementation
- getInstance() double-checked locking implementation (volatile keyword placement, synchronization)
- File I/O with FileWriter and PrintWriter initialization
- Timestamp formatting using LocalDateTime and DateTimeFormatter
- Log message formatting with level and timestamp
- Resource cleanup logic in close() and setLogFile()
- Error handling for IOException during file operations
- Thread-safety considerations (synchronization vs. volatile)
