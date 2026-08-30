# Facade Pattern for Image Editing Application

Source folder: `1773391246_4be703b4bc4c6574/Facade_Image-solution`

## Problem Statement

You are developing an image editing software that offers various features like loading images, applying filters, adjusting brightness, and saving images. The editing module has complex interactions and dependencies. Your goal is to simplify the interface for users by providing a unified way to access and control these editing functionalities.

## Detailed Requirements

1. **Review the original class**: Take a closer look at the `ImageEditingManager` class and its methods. Understand how each editing module is handled and the interactions involved.

2. **Create the facade class**: Create a new class named `ImageEditingFacade` that implements the Facade pattern. This class will encapsulate the interactions with the image editing module, providing a simplified way to edit images.

3. **Remember to call the constructor of your facade using the same arguments from the `ImageEditingManager` class**: Ensure that the constructor of your `ImageEditingFacade` class takes the same arguments that the `ImageEditingManager` class constructor does. This will allow you to pass the necessary dependencies to the facade.

4. **Test your implementation**: Test cases have been provided for you to verify your implementation. Run the test cases to ensure that your facade class works correctly and provides the expected image editing functionality.

## Graded Contract (from tests)

The tests verify the following:

- **ImageEditingManager** must NOT have any direct fields referencing: `ImageLoader`, `FilterService`, `ImageModifier`, `ImageWriter`, or `AnalyticsService`
- **ImageEditingManager constructor** accepts 5 parameters: `ImageLoader`, `FilterService`, `ImageModifier`, `ImageWriter`, `AnalyticsService` (in that order)
- **editImage(String imagePath, String filterType, int brightness) -> void** method exists
- When `editImage()` is called, all of these must occur in sequence:
  - `imageLoader.loadImage(imagePath)` is called
  - `filterService.applyFilter(image, filterType)` is called
  - `imageModifier.adjustBrightness(image, brightness)` is called
  - `imageWriter.saveImage(image)` is called
  - `analyticsService.store(image)` is called

## Any Given "Before" Code

The existing tightly-coupled workflow:

```java
public class ImageProcessor {
    private ImageLoader imageLoader;
    private FilterService filterService;
    private ImageModifier imageModifier;
    private ImageWriter imageWriter;
    private AnalyticsService analyticsService;

    public ImageProcessor(ImageLoader imageLoader, FilterService filterService, 
                          ImageModifier imageModifier, ImageWriter imageWriter, 
                          AnalyticsService analyticsService) {
        this.imageLoader = imageLoader;
        this.filterService = filterService;
        this.imageModifier = imageModifier;
        this.imageWriter = imageWriter;
        this.analyticsService = analyticsService;
    }

    public void process(String imagePath, String filterType, int brightness) {
        Image image = imageLoader.loadImage(imagePath);
        filterService.applyFilter(image, filterType);
        imageModifier.adjustBrightness(image, brightness);
        imageWriter.saveImage(image);
        analyticsService.store(image);
    }
}
```

The Facade pattern refactoring involves creating `ImageEditingManager` that abstracts away this complexity by delegating to a `ImageProcessor`.

## Learner Template

```java
package com.assignment.question;

import com.assignment.question.services.*;

public class ImageEditingManager {
    private ImageProcessor imageProcessor;

    public ImageEditingManager(ImageLoader imageLoader, FilterService filterService, 
                               ImageModifier imageModifier, ImageWriter imageWriter, 
                               AnalyticsService analyticsService) {
        // TODO: initialize imageProcessor with the dependencies
    }

    public void editImage(String imagePath, String filterType, int brightness) {
        // TODO: delegate to imageProcessor
    }
}
```

## Deliberately Left Out (for the learner to design)

- The initialization of `ImageProcessor` inside the constructor
- The delegation logic in `editImage()` method to call `imageProcessor.process()`
- The understanding that `ImageProcessor` encapsulates all the complex dependencies and their interactions
- The awareness that the facade pattern hides `ImageProcessor` from the client, exposing only `ImageEditingManager`
