package com.assignment.question;

// TODO: implement QualityAdjustmentStrategy — supportsType() returns HIGH,
// adjust(...) sets the video's codec to VP9 and bitrate to 2000, then returns it.
public class HighVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        return null;
    }

    @Override
    public Video adjust(Video video) {
        return null;
    }
}
