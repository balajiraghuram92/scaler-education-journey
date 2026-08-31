package com.assignment.question;

import com.assignment.question.models.Image;
import com.assignment.question.services.*;

public class ImageProcessor {

    private ImageLoader imageLoader;
    private FilterService filterService;
    private ImageModifier imageModifier;
    private ImageWriter imageWriter;
    private AnalyticsService analyticsService;

    public ImageProcessor(ImageLoader imageLoader, FilterService filterService, ImageModifier imageModifier, ImageWriter imageWriter, AnalyticsService analyticsService) {
        this.imageLoader = imageLoader;
        this.filterService = filterService;
        this.imageModifier = imageModifier;
        this.imageWriter = imageWriter;
        this.analyticsService = analyticsService;
    }

    public void process(String imagePath, String filterType, int brightness) {
        // TODO: load the image, apply the filter, adjust brightness,
        // save the result, and record it via analyticsService — in that order
    }

}
