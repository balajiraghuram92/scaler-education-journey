package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.decoder.MP3Decoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.player.MP3Player;
import com.assignment.question.processor.AudioProcessor;
import com.assignment.question.processor.MP3AudioProcessor;

public class MP3AudioFactory extends AudioFactory {
    public MediaFormat supportsFormat() {
        return MediaFormat.MP3;
    }

    public AudioPlayer createAudioPlayer(int volume, double playbackRate) {
        return new MP3Player(volume, playbackRate);
    }

    public AudioDecoder createAudioDecoder(byte[] audioData) {
        return new MP3Decoder(audioData);
    }

    public AudioProcessor createAudioProcessor(byte[] audioData) {
        return new MP3AudioProcessor(audioData);
    }
}
