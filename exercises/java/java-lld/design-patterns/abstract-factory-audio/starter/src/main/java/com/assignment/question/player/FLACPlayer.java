package com.assignment.question.player;

import com.assignment.question.MediaFormat;

// TODO: extend AudioPlayer and implement play/pause/stop and supportsFormat() (MediaFormat.FLAC).
public class FLACPlayer extends AudioPlayer {

    public FLACPlayer(int volume, double playBackRate) {
        super(volume, playBackRate);
    }

    @Override
    public void play() {

    }

    @Override
    public void pause() {

    }

    @Override
    public void stop() {

    }

    public MediaFormat supportsFormat() {
        return null;
    }
}
