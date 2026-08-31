package com.assignment.question.processor;

import com.assignment.question.MediaFormat;

// TODO: extend AudioProcessor and implement supportsFormat() (MediaFormat.FLAC) and process().
public class FLACAudioProcessor extends AudioProcessor {

    public FLACAudioProcessor(byte[] audioData) {
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
