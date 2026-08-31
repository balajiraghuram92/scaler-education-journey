package com.assignment.question;

import com.assignment.question.services.*;

public class ImageEditingManager {
    // TODO: this class must NOT hold direct fields of ImageLoader, FilterService,
    // ImageModifier, ImageWriter, or AnalyticsService — delegate the actual work
    // to ImageProcessor instead, so this facade stays a thin entry point.

    public ImageEditingManager(ImageLoader imageLoader, FilterService filterService, ImageModifier imageModifier, ImageWriter imageWriter, AnalyticsService analyticsService) {
        // TODO: construct the internal ImageProcessor from these dependencies
    }

    public void editImage(String imagePath, String filterType, int brightness) {
        // TODO: delegate to the internal ImageProcessor
    }

}
