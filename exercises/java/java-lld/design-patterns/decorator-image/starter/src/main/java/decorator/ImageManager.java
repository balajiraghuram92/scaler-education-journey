package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class ImageManager {

    public Image readImage(String filePath, boolean enableGrayscale, boolean enableBlur) {

        Image image = ImageUtils.read(filePath);
        if (enableGrayscale) {
            image = ImageUtils.convertToGrayscale(image);
        }

        if (enableBlur) {
            image = ImageUtils.applyBlur(image);
        }

        return image;
    }
}
