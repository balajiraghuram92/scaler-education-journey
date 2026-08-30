# Decorator Pattern for Image Editing Application

Source folder: `1773392372_b68eda7052e83f71 / Decorator_Image-solution`

## Problem Statement

You are working on an image editing application where users can apply various filters and effects to their images. However, the current implementation of the application is becoming monolithic, with each filter or effect tightly coupled to the main image editor class. Moreover, adding new filters or effects requires modifying the existing code, leading to maintenance issues and potential bugs.

You want to refactor the image editing application to make it more flexible and maintainable. You decide to use the Decorator pattern to allow users to dynamically add filters and effects to images without modifying the existing codebase.

## Detailed Requirements

Your task is to implement the Decorator pattern to enhance the image editing application. The Decorator pattern allows behavior to be added to individual objects dynamically, without affecting the behavior of other objects of the same class. This pattern is particularly useful when you need to add or modify the behavior of objects at runtime.

### Task 1 - Implement the ImageEditor Interface

You have been provided with a base class named `StorageManager`, which represents the main image editing functionality. Your first task is to create the `ImageEditor` interface. You need to complete the `ImageEditor` interface by adding a method:

- Add a method `readImage` that takes a `String filePath` parameter and returns an `Image` object.

### Task 2 - Implement the RawImageEditor Class

Next, you need to implement the `RawImageEditor` class, which is a concrete implementation of the `ImageEditor` and simply renders the raw image. The tasks are as follows:

- Implement the `ImageEditor` interface to render the raw image.
- Use the `ImageUtils.read(String)` method to read and return the image.

### Task 3 - Implement the BaseImageDecorator Class

Now, you need to implement the `BaseImageDecorator` abstract class, which is the base class for all decorators. Each decorator should have the same methods as the product it decorates, i.e., `readImage`. It also needs to call the next decorator in the chain and finally call the raw image editor. The tasks are as follows:

- Inherit from the `ImageEditor` interface.
- Store a reference to the next layer of type `ImageEditor`.
- Add a constructor that accepts an `ImageEditor` parameter and stores it.

### Task 4 - Implement the BlurImageDecorator, SharpenImageDecorator, and GrayscaleImageDecorator Classes

Finally, you need to implement the `BlurImageDecorator`, `SharpenImageDecorator`, and `GrayscaleImageDecorator` classes, which are concrete decorators that add specific filters to the image editing application. The tasks are as follows:

- Implement the `BlurImageDecorator` class to apply a blur effect to the image. Use the `ImageUtils.applyBlur` method for this purpose. Remember to call the next layer in the chain while rendering the image.
- Implement the `SharpenImageDecorator` class to apply a sharpen effect to the image. Use the `ImageUtils.applySharpen` method for this purpose. Remember to call the next layer in the chain while rendering the image.
- Implement the `GrayscaleImageDecorator` class to apply a grayscale effect to the image. Use the `ImageUtils.applyGrayscale` method for this purpose. Remember to call the next layer in the chain while rendering the image.

## Graded Contract (from tests)

- `ImageEditor` interface must have:
  - `Image readImage(String filePath)` method
- `RawImageEditor` must implement `ImageEditor`
- `BaseImageDecorator` must:
  - Implement `ImageEditor` interface
  - Have a field of type `ImageEditor` (to store the next layer)
  - Have a constructor accepting `ImageEditor` parameter
- `BlurImageDecorator` must:
  - Extend `BaseImageDecorator`
  - Have a constructor accepting `ImageEditor` parameter
- `GrayscaleImageDecorator` must:
  - Extend `BaseImageDecorator`
  - Have a constructor accepting `ImageEditor` parameter
- Tests use reflection to verify class hierarchy, interface implementation, and constructor signatures

## Learner Template

```java
package decorator;

import decorator.utils.Image;

public interface ImageEditor {

    Image readImage(String filePath);
}
```

```java
package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class RawImageEditor implements ImageEditor {
    @Override
    public Image readImage(String filePath) {
        // TODO: Implement
    }
}
```

```java
package decorator;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public abstract class BaseImageDecorator implements ImageEditor {
    
    protected ImageEditor nextLayer;
}
```

```java
package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class BlurImageDecorator extends BaseImageDecorator {

    public BlurImageDecorator(ImageEditor nextLayer) {
        // TODO: Implement
    }

    @Override
    public Image readImage(String filePath) {
        // TODO: Implement
    }
}
```

```java
package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class SharpenImageDecorator extends BaseImageDecorator {

    public SharpenImageDecorator(ImageEditor nextLayer) {
        // TODO: Implement
    }

    @Override
    public Image readImage(String filePath) {
        // TODO: Implement
    }
}
```

```java
package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class GrayscaleImageDecorator extends BaseImageDecorator {

    public GrayscaleImageDecorator(ImageEditor nextLayer) {
        // TODO: Implement
    }

    @Override
    public Image readImage(String filePath) {
        // TODO: Implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- The constructor implementation in `BaseImageDecorator` (must call super with the nextLayer parameter)
- The specific decorator implementations with the correct filter application logic (calling `ImageUtils.applyBlur()`, `ImageUtils.applySharpen()`, `ImageUtils.applyGrayscale()`)
- The pattern of chaining decorators together (calling `nextLayer.readImage()` before applying the filter)
