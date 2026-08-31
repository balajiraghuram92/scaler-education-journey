package com.assignment.question;

// TODO: implement QualityAdjustmentStrategy — supportsType() returns LOW,
// adjust(...) sets the video's codec to H264 and bitrate to 500, then returns it.
public class LowVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        return null;
    }

    @Override
    public Video adjust(Video video) {
        return null;
    }
}
