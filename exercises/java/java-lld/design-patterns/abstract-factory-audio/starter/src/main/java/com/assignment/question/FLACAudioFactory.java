package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.decoder.FLACDecoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.player.FLACPlayer;
import com.assignment.question.processor.AudioProcessor;
import com.assignment.question.processor.FLACAudioProcessor;

// TODO: extend AudioFactory, wiring up the FLAC family: FLACPlayer, FLACDecoder, FLACAudioProcessor.
public class FLACAudioFactory extends AudioFactory {

    public AudioPlayer createAudioPlayer(int volume, double playbackRate) {
        return null;
    }

    public AudioDecoder createAudioDecoder(byte[] audioData) {
        return null;
    }

    public AudioProcessor createAudioProcessor(byte[] audioData) {
        return null;
    }

    public MediaFormat supportsFormat() {
        return null;
    }
}
