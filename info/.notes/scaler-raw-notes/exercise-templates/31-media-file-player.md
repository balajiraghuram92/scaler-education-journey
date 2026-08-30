# Media File Player

Source folder: 1773391660_c04fae06ac58360d/Media_File_Playe-solution

## Problem Statement

You are tasked with implementing a media player application that supports playing different types of media files, including audio and video. Each media file type requires specific implementations to play them properly. Your goal is to create a method named `playMedia` within the `MediaFilePlayer` class that can accept various types of media files (either audio or video) and play them using runtime polymorphism. The `playMedia` method should accept a parameter representing a media file, print the details of the media file, and call the `play` method appropriate to each media type.

## Graded Contract (from tests)

- **MediaFile abstract class**: Must have abstract method `play()` and method `getDetails()` returning String
- **AudioFile class**: Must extend MediaFile with constructor `(String title, String artist, String fileName)` and override both `play()` and `getDetails()`
- **VideoFile class**: Must extend MediaFile with constructor `(String title, String fileName, String duration)` and override both `play()` and `getDetails()`
- **MediaFilePlayer class**: Must have static method `playMedia(MediaFile mediaFile)` that prints file details and calls play()

## Learner Template

```java
package org.example;

public abstract class MediaFile {
    // TODO: Declare protected fields and constructor

    public abstract void play();

    public String getDetails() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class AudioFile extends MediaFile {
    // TODO: Declare private fields

    public AudioFile(String title, String artist, String fileName) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void play() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public String getDetails() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class VideoFile extends MediaFile {
    // TODO: Declare private fields

    public VideoFile(String title, String fileName, String duration) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void play() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public String getDetails() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class MediaFilePlayer {
    public static void playMedia(MediaFile mediaFile) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field names and types in AudioFile and VideoFile
- Implementation logic in `getDetails()` for building the detail strings
- Implementation logic in `play()` methods for printing output
- Implementation logic in `playMedia()` for calling methods in proper order
- Constructor bodies and super() calls
- Main method if any

