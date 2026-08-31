package org.example;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.*;

// TODO: implement paintImage(...) — split the image into 4 quadrants (top-left,
// top-right, bottom-left, bottom-right) and submit one paintQuadrant(...) task per
// quadrant to the fixed thread pool, each with its own color (color, color*2, color*3,
// color*4 respectively, matching top-left/top-right/bottom-left/bottom-right order).
// Wait for all 4 Futures to complete (via get()) before shutting the executor down.
public class ImagePainter {
    static ExecutorService executor;
    private final int[][] image;
    public ImagePainter(int[][] image) {
        this.image = image;
        executor = Executors.newFixedThreadPool(4);
    }

    public void paintImage(int color) throws InterruptedException {

    }

    private void paintQuadrant(int startRow, int endRow, int startCol, int endCol, int color) {
        for (int i = startRow; i < endRow; i++) {
            for (int j = startCol; j < endCol; j++) {
                image[i][j] = color;
            }
        }
    }

    public int[][] getImage() {
        return image;
    }
}
