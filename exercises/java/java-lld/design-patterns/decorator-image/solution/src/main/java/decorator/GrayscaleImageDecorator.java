package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class GrayscaleImageDecorator extends BaseImageDecorator {

    public GrayscaleImageDecorator(ImageEditor nextLayer) {
        super(nextLayer);
    }

    @Override
    public Image readImage(String filePath) {
        Image image = nextLayer.readImage(filePath);
        return ImageUtils.convertToGrayscale(image);
    }
}
