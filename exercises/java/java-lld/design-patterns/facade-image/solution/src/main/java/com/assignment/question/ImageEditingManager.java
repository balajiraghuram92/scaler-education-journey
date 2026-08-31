package com.assignment.question;

import com.assignment.question.services.*;

public class ImageEditingManager {
    private ImageProcessor imageProcessor;

    public ImageEditingManager(ImageLoader imageLoader, FilterService filterService, ImageModifier imageModifier, ImageWriter imageWriter, AnalyticsService analyticsService) {
        this.imageProcessor = new ImageProcessor(imageLoader, filterService, imageModifier, imageWriter, analyticsService);
    }

    public void editImage(String imagePath, String filterType, int brightness) {
        imageProcessor.process(imagePath, filterType, brightness);
    }

}
