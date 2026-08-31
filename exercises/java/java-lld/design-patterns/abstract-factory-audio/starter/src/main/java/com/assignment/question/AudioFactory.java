package com.assignment.question;

import com.assignment.question.decoder.AudioDecoder;
import com.assignment.question.player.AudioPlayer;
import com.assignment.question.processor.AudioProcessor;

public abstract class AudioFactory {
    public abstract MediaFormat supportsFormat();

    public abstract AudioPlayer createAudioPlayer(int volume, double playbackRate);
    public abstract AudioDecoder createAudioDecoder(byte[] audioData);
    public abstract AudioProcessor createAudioProcessor(byte[] audioData);

}
