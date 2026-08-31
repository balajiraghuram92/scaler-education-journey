package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.decoder.FLACDecoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.player.FLACPlayer;
import com.assignment.question.processor.AudioProcessor;
import com.assignment.question.processor.FLACAudioProcessor;

public class FLACAudioFactory extends AudioFactory {

    public AudioPlayer createAudioPlayer(int volume, double playbackRate) {
        return new FLACPlayer(volume, playbackRate);
    }

    public AudioDecoder createAudioDecoder(byte[] audioData) {
        return new FLACDecoder(audioData);
    }

    public AudioProcessor createAudioProcessor(byte[] audioData) {
        return new FLACAudioProcessor(audioData);
    }

    public MediaFormat supportsFormat() {
        return MediaFormat.FLAC;
    }
}
