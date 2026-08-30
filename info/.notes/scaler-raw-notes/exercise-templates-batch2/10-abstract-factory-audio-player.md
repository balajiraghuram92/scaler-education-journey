# Abstract Factory Pattern for Audio Players

Source folder: `1773391285_bde50a5a94549d0e/Abstract_Factory-solution`

## Problem Statement

You are designing an audio player application. The application should support different audio formats such as MP3, WAV, and FLAC. Each format requires specific decoding, processing, and rendering steps. You want to create instances of these processing steps without explicitly specifying their classes and ensure that the steps within the same format family are compatible.

## Detailed Requirements

Your task is to extend the Abstract Factory pattern to create audio processing components in the audio player application. The Abstract Factory pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes, allowing for easy addition of new audio format processor types and ensuring compatibility within families.

### Task 1 - Adding the factory methods to the abstract factory

The abstract factory class `AudioFactory` has been created for you. You will need to add the factory methods to create audio decoders, processors, and renderers to the abstract factory class. The method `supportsFormat` has already been abstracted out for you as an example. You will need to implement the `AudioFactory` class as a common parent class for all the audio format factories.

### Task 2 - Implementing the Abstract Factory

Now that you have the abstract factory class, you will need to implement the abstract factory for different audio formats such as MP3, WAV, and FLAC. Three classes have been created for you: `Mp3AudioFactory`, `WavAudioFactory`, and `FlacAudioFactory`. You will need to implement the methods to create compatible audio decoders, processors, and renderers. Ensure that the created components are compatible within the same format family.

### Instructions

1. Implement the `AudioFactory` interface with methods to create audio decoders, processors, and renderers.
2. Create concrete implementations of the `AudioFactory` interface for MP3, WAV, and FLAC audio formats. Implement the methods to create compatible audio decoders, processors, and renderers.
3. Run the provided test cases in the `AudioFactoryTest` class to verify the correctness of your implementation. The tests will check if all audio components have a common parent class, and if the factory classes can correctly create audio decoders, processors, and renderers based on the audio format.

## Graded Contract (from tests)

- **AudioFactory abstract parent class:** Must exist as abstract class
- **AudioFactory methods (all abstract):**
  - `supportsFormat()` - returns `MediaFormat`, no parameters
  - `createAudioPlayer(int volume, double playbackRate)` - returns `AudioPlayer`
  - `createAudioDecoder(byte[] audioData)` - returns `AudioDecoder`
  - `createAudioProcessor(byte[] audioData)` - returns `AudioProcessor`
- **Number of concrete factories:** Exactly 2 implementations (MP3AudioFactory and FLACAudioFactory are required; note test says 2, not 3)
- **AudioPlayer abstract class:** Must exist with `supportsFormat()` abstract method
- **AudioDecoder abstract class:** Must exist with `supportsFormat()` abstract method
- **AudioProcessor abstract class:** Must exist with `supportsFormat()` abstract method
- **Concrete implementations:** Must correctly implement all abstract methods and return format-specific components
- **Format matching:** Each factory's created components must return the matching MediaFormat from their `supportsFormat()` method

## Learner Template

```java
// AudioFactory.java - Abstract Factory
package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.processor.AudioProcessor;

public abstract class AudioFactory {
    public abstract MediaFormat supportsFormat();

    public abstract AudioPlayer createAudioPlayer(int volume, double playbackRate);
    public abstract AudioDecoder createAudioDecoder(byte[] audioData);
    public abstract AudioProcessor createAudioProcessor(byte[] audioData);
}
```

```java
// MP3AudioFactory.java - Concrete Factory
package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.processor.AudioProcessor;

public class MP3AudioFactory extends AudioFactory {
    
    @Override
    public MediaFormat supportsFormat() {
        // TODO: implement
    }

    @Override
    public AudioPlayer createAudioPlayer(int volume, double playbackRate) {
        // TODO: implement
    }

    @Override
    public AudioDecoder createAudioDecoder(byte[] audioData) {
        // TODO: implement
    }

    @Override
    public AudioProcessor createAudioProcessor(byte[] audioData) {
        // TODO: implement
    }
}
```

```java
// FLACAudioFactory.java - Concrete Factory
package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.processor.AudioProcessor;

public class FLACAudioFactory extends AudioFactory {
    
    @Override
    public MediaFormat supportsFormat() {
        // TODO: implement
    }

    @Override
    public AudioPlayer createAudioPlayer(int volume, double playbackRate) {
        // TODO: implement
    }

    @Override
    public AudioDecoder createAudioDecoder(byte[] audioData) {
        // TODO: implement
    }

    @Override
    public AudioProcessor createAudioProcessor(byte[] audioData) {
        // TODO: implement
    }
}
```

```java
// AudioPlayer.java - Abstract parent (reference)
package com.assignment.question.player;

import com.assignment.question.MediaFormat;

public abstract class AudioPlayer {
    public abstract MediaFormat supportsFormat();
}
```

```java
// AudioDecoder.java - Abstract parent (reference)
package com.assignment.question.decoder;

import com.assignment.question.MediaFormat;

public abstract class AudioDecoder {
    public abstract MediaFormat supportsFormat();
}
```

```java
// AudioProcessor.java - Abstract parent (reference)
package com.assignment.question.processor;

import com.assignment.question.MediaFormat;

public abstract class AudioProcessor {
    public abstract MediaFormat supportsFormat();
}
```

```java
// MediaFormat.java - Enumeration
package com.assignment.question;

public enum MediaFormat {
    MP3, WAV, FLAC
}
```

## Deliberately Left Out (for the learner to design)

- Concrete implementations of MP3Decoder, MP3Player, MP3AudioProcessor classes
- Concrete implementations of FLACDecoder, FLACPlayer, FLACAudioProcessor classes
- WAV format factory and concrete implementations (may be added for future extension)
- Implementation logic for all abstract methods in concrete factories
- Implementation logic for process/decode/play methods in concrete audio components
- Constructor implementations and field management in concrete classes
