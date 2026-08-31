package com.assignment.question.decoder;

import com.assignment.question.MediaFormat;

// TODO: extend AudioDecoder and implement supportsFormat() (MediaFormat.MP3) and decode().
public class MP3Decoder extends AudioDecoder {

    public MP3Decoder(byte[] audioData) {
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
