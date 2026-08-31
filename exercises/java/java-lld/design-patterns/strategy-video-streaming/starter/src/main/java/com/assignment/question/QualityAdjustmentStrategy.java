package com.assignment.question;

public interface QualityAdjustmentStrategy {
    VideoQuality supportsType();

    Video adjust(Video video);
}
