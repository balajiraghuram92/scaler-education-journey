package com.assignment.question;

// TODO: implement QualityAdjustmentStrategy — supportsType() returns MEDIUM,
// adjust(...) sets the video's codec to H265 and bitrate to 1000, then returns it.
public class MediumVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        return null;
    }

    @Override
    public Video adjust(Video video) {
        return null;
    }
}
