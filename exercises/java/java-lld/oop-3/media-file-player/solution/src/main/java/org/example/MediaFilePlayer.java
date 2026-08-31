package org.example;

public class MediaFilePlayer {

    // Todo: Implement a method called playMedia
    // The play media will print the details of the file and then call the play method.
    // that demonstrates run-time polymorphism

    public static void playMedia(MediaFile mediaFile) {
        System.out.println(mediaFile.getDetails());
        mediaFile.play();
    }
}
