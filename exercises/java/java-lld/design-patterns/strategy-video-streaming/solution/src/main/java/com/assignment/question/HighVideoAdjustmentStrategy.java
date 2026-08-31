package com.assignment.question;

public class HighVideoAdjustmentStrategy implements QualityAdjustmentStrategy {
    @Override
    public VideoQuality supportsType() {
        return VideoQuality.HIGH;
    }

    @Override
    public Video adjust(Video video) {
        video.setCodec(VideoCodec.VP9);
        video.setBitrate(2000);
        return video;
    }
}
