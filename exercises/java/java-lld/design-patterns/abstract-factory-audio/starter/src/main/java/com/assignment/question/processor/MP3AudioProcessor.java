package com.assignment.question.processor;

import com.assignment.question.MediaFormat;

// TODO: extend AudioProcessor and implement supportsFormat() (MediaFormat.MP3) and process().
public class MP3AudioProcessor extends AudioProcessor {

    public MP3AudioProcessor(byte[] audioData) {
        super(audioData);
    }

    @Override
    public MediaFormat supportsFormat() {
        return null;
    }

    @Override
    public byte[] process() {
        return null;
    }
}
