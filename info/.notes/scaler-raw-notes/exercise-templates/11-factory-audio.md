# Simple Factory Pattern for Audio Player

Source folder: `1773391267_1a838247edae7209/Factory_Audio-solution`

## Problem Statement

You are developing an audio player application that supports different audio formats, such as MP3, WAV, and FLAC. Each audio format requires a specific decoder and player implementation. To keep your audio player extensible and maintainable, you decide to implement the Simple Factory pattern to create audio player objects based on the audio format.

Your task is to implement the Simple Factory pattern to create audio players for different audio formats in the audio player application. The Simple Factory pattern allows you to encapsulate the creation logic of audio player objects, making it easy to add support for new audio formats in the future.

## Graded Contract (from tests)

- **Abstract class `AudioPlayer`**
  - Abstract methods:
    - `MediaFormat supportsType()` — returns the MediaFormat this player supports
    - `void play()` — plays audio
    - `void pause()` — pauses audio
    - `void stop()` — stops audio
  - Constructor: `AudioPlayer(int volume, double playBackRate)`
  - Fields: `volume` (int), `playBackRate` (double)
  - Getters: `getVolume()`, `getPlayBackRate()`

- **Enum `MediaFormat`**
  - Values: `MP3`, `FLAC`, `WAV`

- **Exactly 3 concrete subclasses of AudioPlayer**
  - Must extend AudioPlayer
  - Each must have constructor with parameters (int volume, double playBackRate)
  - Each must override the abstract methods

- **Class `AudioPlayerFactory`**
  - Static method: `getAudioPlayer(MediaFormat mediaFormat, int volume, double playBackRate)` — returns AudioPlayer
  - Method must accept parameters in some order: MediaFormat, int, double
  - Returns correct player type based on MediaFormat enum value

- **Test contract details**
  - Tests use reflection to find exactly 3 subclasses of AudioPlayer
  - Tests check for abstract methods in AudioPlayer
  - Tests verify volume (int/Integer) and playBackRate (double/Double) fields
  - Tests check factory method exists and accepts MediaFormat + int + double parameters
  - Tests verify factory returns correct player type for a given format

## Learner Template

```java
package com.assignment.question;

public enum MediaFormat {
    MP3,
    FLAC,
    WAV
}
```

```java
package com.assignment.question;

public abstract class AudioPlayer {
    private int volume;
    private double playBackRate;

    public AudioPlayer(int volume, double playBackRate) {
        // TODO: implement
    }

    public abstract MediaFormat supportsType();

    public abstract void play();

    public abstract void pause();

    public abstract void stop();

    public int getVolume() {
        // TODO: implement
    }

    public double getPlayBackRate() {
        // TODO: implement
    }

    public void setVolume(int volume) {
        // TODO: implement
    }
}
```

```java
package com.assignment.question;

public class MP3Player extends AudioPlayer {
    public MP3Player(int volume, double playBackRate) {
        // TODO: implement
    }

    @Override
    public void play() {
        // TODO: implement
    }

    @Override
    public void pause() {
        // TODO: implement
    }

    @Override
    public void stop() {
        // TODO: implement
    }

    public MediaFormat supportsType() {
        // TODO: implement
    }
}
```

```java
package com.assignment.question;

public class WAVPlayer extends AudioPlayer {
    public WAVPlayer(int volume, double playBackRate) {
        // TODO: implement
    }

    @Override
    public void play() {
        // TODO: implement
    }

    @Override
    public void pause() {
        // TODO: implement
    }

    @Override
    public void stop() {
        // TODO: implement
    }

    public MediaFormat supportsType() {
        // TODO: implement
    }
}
```

```java
package com.assignment.question;

public class FLACPlayer extends AudioPlayer {
    public FLACPlayer(int volume, double playBackRate) {
        // TODO: implement
    }

    @Override
    public void play() {
        // TODO: implement
    }

    @Override
    public void pause() {
        // TODO: implement
    }

    @Override
    public void stop() {
        // TODO: implement
    }

    public MediaFormat supportsType() {
        // TODO: implement
    }
}
```

```java
package com.assignment.question;

public class AudioPlayerFactory {
    public static AudioPlayer getAudioPlayer(MediaFormat mediaFormat, int volume, double playBackRate) {
        // TODO: implement - use switch or if-else to return correct player type
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field initialization in AudioPlayer constructor
- Volume and playBackRate getter implementations
- SetVolume method implementation (with validation logic)
- Concrete implementations of play(), pause(), stop() in each player
- The exact type detection/switch logic in the factory method
- Whether to use switch expression or traditional switch/if-else
- Helper classes or configuration maps for factory (if any)
