package com.assignment.question.decoder;

import com.assignment.question.MediaFormat;

// TODO: extend AudioDecoder and implement supportsFormat() (MediaFormat.FLAC) and decode().
public class FLACDecoder extends AudioDecoder {

    public FLACDecoder(byte[] audioData) {
        super(audioData);
    }

    @Override
    public MediaFormat supportsFormat() {
        return null;
    }

    @Override
    public byte[] decode() {
        return null;
    }
}
