package com.assignment.question.player;

import com.assignment.question.MediaFormat;

public class FLACPlayer extends AudioPlayer {

    public FLACPlayer(int volume, double playBackRate) {
        super(volume, playBackRate);
    }

    @Override
    public void play() {
        System.out.println("Playing FLAC audio");
    }

    @Override
    public void pause() {
        System.out.println("Pausing FLAC audio");
    }

    @Override
    public void stop() {
        System.out.println("Stopping FLAC audio");
    }

    public MediaFormat supportsFormat() {
        return MediaFormat.FLAC;
    }
}
