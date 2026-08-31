package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.decoder.MP3Decoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.player.MP3Player;
import com.assignment.question.processor.AudioProcessor;
import com.assignment.question.processor.MP3AudioProcessor;

// TODO: extend AudioFactory, wiring up the MP3 family: MP3Player, MP3Decoder, MP3AudioProcessor.
public class MP3AudioFactory extends AudioFactory {
    public MediaFormat supportsFormat() {
        return null;
    }

    public AudioPlayer createAudioPlayer(int volume, double playbackRate) {
        return null;
    }

    public AudioDecoder createAudioDecoder(byte[] audioData) {
        return null;
    }

    public AudioProcessor createAudioProcessor(byte[] audioData) {
        return null;
    }
}
