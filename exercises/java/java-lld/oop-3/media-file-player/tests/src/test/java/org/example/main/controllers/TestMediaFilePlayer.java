package org.example.main.controllers;

import org.example.AudioFile;
import org.example.MediaFile;
import org.example.MediaFilePlayer;
import org.example.VideoFile;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestMediaFilePlayer {

    @Test
    public void testPlayMediaWithAudioFile() {
        ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        System.setOut(new PrintStream(outContent));

        MediaFile audioFile = new AudioFile("Song Title", "Artist Name", "audio.mp3");
        MediaFilePlayer.playMedia(audioFile);

        String expectedOutput = "Title: Song Title, File: audio.mp3, Artist: Artist Name" + System.lineSeparator() + "Playing audio file: audio.mp3" + System.lineSeparator();
        assertEquals(expectedOutput, outContent.toString());
    }

    @Test
    public void testPlayMediaWithVideoFile() {
        ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        System.setOut(new PrintStream(outContent));

        MediaFile videoFile = new VideoFile("Video Title", "video.mp4","30");
        MediaFilePlayer.playMedia(videoFile);

        String expectedOutput = "Title: Video Title, File: video.mp4, Duration: 30" + System.lineSeparator() + "Playing video file: video.mp4" + System.lineSeparator();
        assertEquals(expectedOutput, outContent.toString());
    }

    @Test
    public void testGetDetailsAudioFile() {
        MediaFile audioFile = new AudioFile("Song Title", "Artist Name", "audio.mp3");
        String expectedDetails = "Title: Song Title, File: audio.mp3, Artist: Artist Name";
        assertEquals(expectedDetails, audioFile.getDetails());
    }

    @Test
    public void testGetDetailsVideoFile() {
        MediaFile videoFile = new VideoFile("Video Title", "video.mp4", "30");
        String expectedDetails = "Title: Video Title, File: video.mp4, Duration: 30";
        assertEquals(expectedDetails, videoFile.getDetails());
    }

    @Test
    public void testPlayAudioFile() {
        ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        System.setOut(new PrintStream(outContent));

        MediaFile audioFile = new AudioFile("Song Title", "Artist Name", "audio.mp3");
        audioFile.play();

        String expectedOutput = "Playing audio file: audio.mp3" + System.lineSeparator();
        assertEquals(expectedOutput, outContent.toString());
    }

    @Test
    public void testPlayVideoFile() {
        ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        System.setOut(new PrintStream(outContent));

        MediaFile videoFile = new VideoFile("Video Title", "video.mp4", "30");
        videoFile.play();

        String expectedOutput = "Playing video file: video.mp4" + System.lineSeparator();
        assertEquals(expectedOutput, outContent.toString());
    }
}
