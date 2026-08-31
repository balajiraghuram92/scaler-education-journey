package com.assignment.question.processor;

import com.assignment.question.MediaFormat;

public class MP3AudioProcessor extends AudioProcessor {

    public MP3AudioProcessor(byte[] audioData) {
        super(audioData);
    }

    @Override
    public MediaFormat supportsFormat() {
        return MediaFormat.MP3;
    }

    @Override
    public byte[] process() {
        System.out.println("Processing MP3 audio data...");
        return getAudioData();
    }
}
