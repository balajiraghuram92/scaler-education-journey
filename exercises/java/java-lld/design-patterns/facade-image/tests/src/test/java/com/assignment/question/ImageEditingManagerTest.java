package com.assignment.question;

import com.assignment.question.models.Image;
import com.assignment.question.services.*;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.*;

public class ImageEditingManagerTest {
    private static final Set<Class<?>> DEPENDENCIES = Set.of(ImageLoader.class, FilterService.class, ImageModifier.class, ImageWriter.class, AnalyticsService.class);

    @Test
    public void testDependencies() {

        Class<?> imageManagerClass = ImageEditingManager.class;
        Field[] fields = imageManagerClass.getDeclaredFields();

        Arrays.stream(fields).forEach(field -> field.setAccessible(true));
        boolean anyDependencyPresent = DEPENDENCIES.stream().anyMatch(dependency -> Arrays.stream(fields).anyMatch(field -> field.getType().equals(dependency)));

        assertFalse(anyDependencyPresent, "If the facade pattern is implemented correctly, the ImageEditingManager class should not have any dependencies");
    }

    @Test
    public void testImageEditingProcess() {

        String imagePath = "src/test/resources/testImage.jpg";
        String filter = "sepia";
        int brightness = 50;

        ImageLoader imageLoader = mock(ImageLoader.class);
        Image image = new Image();
        when(imageLoader.loadImage(imagePath)).thenReturn(image);

        FilterService filterService = mock(FilterService.class);
        ImageModifier imageModifier = mock(ImageModifier.class);
        ImageWriter imageWriter = mock(ImageWriter.class);
        AnalyticsService analyticService = mock(AnalyticsService.class);

        ImageEditingManager imageEditingManager = new ImageEditingManager(imageLoader, filterService, imageModifier, imageWriter, analyticService);
        imageEditingManager.editImage(imagePath, filter, brightness);

        verify(imageLoader).loadImage(imagePath);
        verify(filterService).applyFilter(image, filter);
        verify(imageModifier).adjustBrightness(image, brightness);
        verify(imageWriter).saveImage(image);
        verify(analyticService).store(image);
    }


}
