package org.example.main.controllers;

import org.example.ImagePainter;
import org.junit.jupiter.api.Test;

public class TestImagePainter {

    public static boolean twoDArrayEquals(int[][] arr1, int[][] arr2) {
        if (arr1.length != arr2.length || arr1[0].length != arr2[0].length) {
            return false;
        }

        for (int i = 0; i < arr1.length; i++) {
            for (int j = 0; j < arr1[0].length; j++) {
                if (arr1[i][j] != arr2[i][j]) {
                    return false;
                }
            }
        }
        return true;
    }

    @Test
    public void testPaintImage_color1() throws InterruptedException {
        int[][] image = new int[4][4];
        ImagePainter painter = new ImagePainter(image);
        painter.paintImage(1);
        int[][] expectedImage = {{1,1,2,2},{1,1,2,2}, {3,3,4,4},{3,3,4,4}};
        int[][] paintedImage = painter.getImage();
        // Verify that each pixel in the painted image is set to desired color
        assert twoDArrayEquals(expectedImage, paintedImage);
    }
    @Test
    public void testPaintImage_color2() throws InterruptedException {
        int[][] image = new int[20][20];
        ImagePainter painter = new ImagePainter(image);
        painter.paintImage(0);
        int[][] expectedImage = new int[20][20];
        int[][] paintedImage = painter.getImage();
        // Verify that each pixel in the painted image is set to desired color
        assert twoDArrayEquals(expectedImage, paintedImage);
    }
}
