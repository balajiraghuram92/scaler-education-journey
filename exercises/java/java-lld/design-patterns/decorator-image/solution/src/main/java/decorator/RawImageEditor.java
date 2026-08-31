package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class RawImageEditor implements ImageEditor {
    @Override
    public Image readImage(String filePath) {
        return ImageUtils.read(filePath);
    }
}
