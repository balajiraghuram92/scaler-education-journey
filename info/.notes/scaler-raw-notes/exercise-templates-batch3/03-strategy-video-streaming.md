# Strategy Pattern for Video Streaming Quality Adjustment

Source folder: `1773391194_f8a7d2a6fcf483d5 / Strategy_Streami-solution`

## Problem Statement

You are developing a video streaming platform that offers different streaming qualities, such as low, standard, and high definition. The platform should dynamically adjust the streaming quality based on the user's network conditions to ensure smooth playback. Additionally, more quality adjustment algorithms may be added in the future. Your task is to implement this dynamic quality adjustment system using the Strategy pattern.

## Detailed Requirements

### Task 1: Implement Strategy Interface
1. Use the existing `QualityAdjustmentStrategy` interface, which defines the `supportsType` method that returns the `VideoQuality` supported by the strategy.
2. Add a new method `adjust` to the `QualityAdjustmentStrategy` interface that accepts a `Video` object and returns a modified `Video` object with adjusted quality settings.

### Task 2: Implement Concrete Strategies
1. Create three concrete strategy classes, each corresponding to a different video quality (LOW, MEDIUM, HIGH). Implement the `supportsType` method to return the supported quality.
2. Implement the `adjust` method for each concrete strategy to adjust the `Video` object's quality settings based on the quality level.

**Quality Settings by Level:**
- **LOW Quality**:
  - Codec: H264
  - Bitrate: 500 kbps

- **MEDIUM Quality**:
  - Codec: H265
  - Bitrate: 1000 kbps

- **HIGH Quality**:
  - Codec: VP9
  - Bitrate: 2000 kbps

### Task 3: Update `VideoStreamingManager`
1. Modify the `VideoStreamingManager` class to accept a `Video` object and a `QualityAdjustmentStrategy` object in the constructor.
2. Implement the `streamVideo` method in the `VideoStreamingManager` class to use the provided strategy to adjust the video's quality settings.

### Testing Instructions
1. Ensure that you have implemented the Strategy pattern correctly by passing the provided test cases in the `VideoStreamingManagerTest` class.
2. The test cases validate that there are three concrete strategies, that the `QualityAdjustmentStrategy` interface has the required methods, and that the `VideoStreamingManager` class is correctly updated to use the strategy for quality adjustment.
3. Make sure that the `adjust` method in each strategy class correctly adjusts the video's quality settings based on the supported quality.

## Graded Contract (from tests)

- **3 concrete strategy classes** implementing `QualityAdjustmentStrategy`:
  - `LowVideoAdjustmentStrategy`
  - `MediumVideoAdjustmentStrategy`
  - `HighVideoAdjustmentStrategy`
- `QualityAdjustmentStrategy` interface has:
  - `VideoQuality supportsType()` method
  - `Video adjust(Video video)` method
- `VideoStreamingManager` has:
  - A private field of type `QualityAdjustmentStrategy`
  - Constructor accepting `Video` and `QualityAdjustmentStrategy` (2 parameters in that order)
  - `Video streamVideo()` method that delegates to the strategy's adjust method
- **Test values** (with Video created with url and quality):
  - LOW quality: codec=H264, bitrate=500
  - MEDIUM quality: codec=H265, bitrate=1000
  - HIGH quality: codec=VP9, bitrate=2000

## Learner Template

### Interface

```java
package com.assignment.question;

public interface QualityAdjustmentStrategy {
    VideoQuality supportsType();

    Video adjust(Video video);
}
```

### Concrete Strategy Classes (skeleton)

```java
package com.assignment.question;

public class LowVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        // TODO: return VideoQuality.LOW
    }

    @Override
    public Video adjust(Video video) {
        // TODO: set codec and bitrate for low quality
        // Set codec to H264 and bitrate to 500
    }
}
```

```java
package com.assignment.question;

public class MediumVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        // TODO: return VideoQuality.MEDIUM
    }

    @Override
    public Video adjust(Video video) {
        // TODO: set codec and bitrate for medium quality
        // Set codec to H265 and bitrate to 1000
    }
}
```

```java
package com.assignment.question;

public class HighVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        // TODO: return VideoQuality.HIGH
    }

    @Override
    public Video adjust(Video video) {
        // TODO: set codec and bitrate for high quality
        // Set codec to VP9 and bitrate to 2000
    }
}
```

### Manager Class (skeleton)

```java
package com.assignment.question;

public class VideoStreamingManager {
    private Video video;
    private QualityAdjustmentStrategy qualityAdjustmentStrategy;

    public VideoStreamingManager(Video video, QualityAdjustmentStrategy qualityAdjustmentStrategy) {
        // TODO: initialize both fields
    }

    public Video streamVideo() {
        // TODO: delegate to the strategy's adjust method
    }
}
```

## Deliberately Left Out (for the learner to design)

- Implementation logic for `adjust` in each concrete strategy (learner must set the correct codec and bitrate values)
- Proper initialization in the `VideoStreamingManager` constructor
- The `VideoQuality` enum (already provided in the repo with LOW, MEDIUM, HIGH values)
- The `VideoCodec` enum (already provided in the repo with H264, H265, VP9 values)
- The `Video` model class with getters and setters (already provided in the repo)
- Field initialization and constructor parameter handling

