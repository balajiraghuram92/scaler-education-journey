# Image Painter

Source folder: 1773391674_bdb79daae980c9c5/Image_Painter-solution

## Problem Statement

Implement a Java program that simulates image re-painting using 4 threads. You are provided with a square image represented as a 2D integer array. The task is to divide the image into four quadrants and let each thread paint one quadrant of the image. Each quadrant should use a different color: the first quadrant uses the base color, the second uses 2x the base color, the third uses 3x the base color, and the fourth uses 4x the base color. The painting process should use Java's `ExecutorService` with a fixed thread pool of 4 threads.

## Graded Contract (from tests)

- **ImagePainter class**: Must have constructor `(int[][] image)` that accepts a 2D int array
- **paintImage method**: Must accept int parameter (color) and throw `InterruptedException`; divides image into 4 quadrants and paints each with multiplied color values
- **getImage method**: Must return the 2D int array `int[][]` that represents the painted image
- Tests verify correct quadrant coloring with base color multipliers (1, 2, 3, 4)

## Learner Template

```java
package org.example;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ImagePainter {
    // TODO: Declare ExecutorService and image field
    
    public ImagePainter(int[][] image) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public void paintImage(int color) throws InterruptedException {
        // TODO: Divide image into 4 quadrants
        // TODO: Submit painting tasks to ExecutorService
        // TODO: Wait for all tasks to complete using get()
        // TODO: Shutdown executor
        throw new UnsupportedOperationException("TODO");
    }

    public int[][] getImage() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private helper method `paintQuadrant()` to paint a single quadrant
- Field declarations and their initialization logic
- The logic for calculating halfRows and halfCols
- The loop logic within paintQuadrant for setting pixel values
- ExecutorService management and Future handling details
- Main method
- Exception handling specifics

