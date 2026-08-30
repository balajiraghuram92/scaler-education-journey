# Decorator Pattern for File Storage Service

Source folder: `1781507011_dddbb9b392294669 / Decorator_Patter-solution`

## Problem Statement

You are building a file storage service like Google Drive or Dropbox. The service allows users to upload files, store them securely, and retrieve them when needed. You need to add more functionality to the service, such as encryption, compression, and virus scanning. The developers have implemented all this functionality in a single class, which is becoming difficult to maintain and extend.

## Given "Before" Code - Monolithic StorageManager

The current implementation shows how all functionality is tightly coupled in a single class:

```java
public class StorageManager {

    public void storeFile(byte[] fileData, String fileName) {
        // Scan the data for viruses
        boolean hasVirus = StorageUtils.scanForVirus(fileData);
        if (hasVirus) {
            throw new VirusDetectedException("Virus detected in file: " + fileName);
        }

        // Compress the data
        byte[] compressedData = StorageUtils.compress(fileData);

        // Store the data
        StorageUtils.store(fileName, compressedData);

    }

    public byte[] getFile(String fileName) {

        byte[] compressedData = StorageUtils.read(fileName);
        if (compressedData == null) {
            throw new IllegalArgumentException("File not found: " + fileName);
        }

        // Decompress the data
        byte[] data = StorageUtils.decompress(compressedData);

        // Scan the data for viruses
        boolean hasVirus = StorageUtils.scanForVirus(data);
        if (hasVirus) {
            throw new VirusDetectedException("Virus detected in file: " + fileName);
        }

        return data;
    }
}
```

This class is tightly coupled with the implementation details of these features, making it difficult to extend or modify the functionality. For example, if you want to store some files without compressing them, or disable virus scanning for some files, the current implementation does not provide an easy way to add or remove features without modifying the existing code.

## Detailed Requirements

Your task is to implement the Decorator pattern to enhance the file storage service. The Decorator pattern allows you to add additional functionality to objects dynamically at runtime without modifying their structure. By applying decorators to the core file storage logic, you can easily enhance its features with encryption, compression, virus scanning, and other capabilities.

### Task 1 - Implement the FileStorage Interface

You have been provided with a base class named `StorageManager`, which currently handles compression and virus scanning in a tightly coupled manner. Your first task is to extract a common interface for file storage operations. You need to complete the `FileStorage` interface by adding two methods:

- Add a method `storeFile` that takes a `String fileName` and a `byte[] content` as arguments with no return value.
- Add a method `getFile` that takes a `String fileName` as an argument and returns a `byte[]`.

### Task 2 - Implement the RawFileStorage Class

Next, you need to implement the `RawFileStorage` class, which is a concrete implementation of the `FileStorage` and simply stores and retrieves the raw file content. The tasks are as follows:

- Implement the `FileStorage` interface to simply store and get the raw file content.
- Use the methods `StorageUtils.store(String, byte[])` and `StorageUtils.read(String)` to perform the actual storage and retrieval operations.

### Task 3 - Implement the BaseFileDecorator Class

Now, you need to implement the `BaseFileDecorator` abstract class, which is the base class for all decorators. Each decorator should have the same methods as the product it decorates, i.e., `storeFile` and `getFile`. It also needs to call the next decorator in the chain and finally call the raw file storage. The tasks are as follows:

- Inherit from the `FileStorage` interface.
- Store a reference to the next layer of type `FileStorage`.

### Task 4 - Implement the CompressionDecorator and VirusScanningDecorator Classes

Finally, you need to implement the `CompressionDecorator` and `VirusScanningDecorator` classes, which are concrete decorators that add compression and virus scanning functionality to the file storage service. The tasks are as follows:

- Implement the `CompressionDecorator` class to compress and decompress the file content. Use the `StorageUtils.compress` and `StorageUtils.decompress` methods for this purpose. Remember to call the next layer in the chain while reading and writing the file content.
- Implement the `VirusScanningDecorator` class to scan the file content for viruses before storing and reading the file content. Use the `StorageUtils.scanForVirus` method for this purpose.

## Graded Contract (from tests)

- `FileStorage` interface must have:
  - `void storeFile(String fileName, byte[] content)` method
  - `byte[] getFile(String fileName)` method
- `RawFileStorage` must implement `FileStorage` interface
- `BaseFileDecorator` must:
  - Implement `FileStorage` interface
  - Have a field of type `FileStorage` (to store the next layer)
  - Have a constructor accepting `FileStorage` parameter
- `CompressionDecorator` must:
  - Extend `BaseFileDecorator`
  - Have a constructor accepting `FileStorage` parameter
- `VirusScanningDecorator` must:
  - Extend `BaseFileDecorator`
  - Have a constructor accepting `FileStorage` parameter
- Tests use reflection to verify interface implementation, class hierarchy, and constructor signatures

## Learner Template

```java
package contest;

public interface FileStorage {
    
    void storeFile(String fileName, byte[] content);
    
    byte[] getFile(String fileName);
}
```

```java
package contest;

import contest.utils.StorageUtils;

public class RawFileStorage implements FileStorage {
    
    @Override
    public void storeFile(String fileName, byte[] content) {
        // TODO: Implement
    }

    @Override
    public byte[] getFile(String fileName) {
        // TODO: Implement
    }
}
```

```java
package contest;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public abstract class BaseFileDecorator implements FileStorage {
    
    protected FileStorage nextLayer;
}
```

```java
package contest;

import contest.utils.StorageUtils;

public class CompressionDecorator extends BaseFileDecorator {
    
    public CompressionDecorator(FileStorage nextLayer) {
        // TODO: Implement
    }

    @Override
    public void storeFile(String fileName, byte[] content) {
        // TODO: Implement
    }

    @Override
    public byte[] getFile(String fileName) {
        // TODO: Implement
    }
}
```

```java
package contest;

import contest.utils.StorageUtils;

public class VirusScanningDecorator extends BaseFileDecorator {
    
    public VirusScanningDecorator(FileStorage nextLayer) {
        // TODO: Implement
    }

    @Override
    public void storeFile(String fileName, byte[] content) {
        // TODO: Implement
    }

    @Override
    public byte[] getFile(String fileName) {
        // TODO: Implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- The constructor implementation in `BaseFileDecorator` (must call super with the nextLayer parameter)
- The `storeFile()` and `getFile()` implementations that call the next layer in the chain
- The specific compression logic in `CompressionDecorator` (must call `StorageUtils.compress()` and `StorageUtils.decompress()`)
- The specific virus scanning logic in `VirusScanningDecorator` (must call `StorageUtils.scanForVirus()` and throw `VirusDetectedException` if virus found)
- The pattern of composing decorators together (e.g., `new VirusScanningDecorator(new CompressionDecorator(new RawFileStorage()))`)
