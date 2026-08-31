package com.assignment.question.player;

import com.assignment.question.MediaFormat;

public class MP3Player extends AudioPlayer {

    public MP3Player(int volume, double playBackRate) {
        super(volume, playBackRate);
    }

    @Override
    public void play() {
        System.out.println("Playing MP3 audio");
    }

    @Override
    public void pause() {
        System.out.println("Pausing MP3 audio");
    }

    @Override
    public void stop() {
        System.out.println("Stopping MP3 audio");
    }

    public MediaFormat supportsFormat() {
        return MediaFormat.MP3;
    }
}
