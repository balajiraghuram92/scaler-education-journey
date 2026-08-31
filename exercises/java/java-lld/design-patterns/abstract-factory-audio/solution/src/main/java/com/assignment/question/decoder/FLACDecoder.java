package com.assignment.question.decoder;

import com.assignment.question.MediaFormat;

public class FLACDecoder extends AudioDecoder {

    public FLACDecoder(byte[] audioData) {
        super(audioData);
    }

    @Override
    public MediaFormat supportsFormat() {
        return MediaFormat.FLAC;
    }

    @Override
    public byte[] decode() {
        System.out.println("Decoding FLAC audio data...");
        return getAudioData();
    }
}
