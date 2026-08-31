package decorator;

import decorator.utils.Image;
import decorator.utils.ImageUtils;

public class BlurImageDecorator extends BaseImageDecorator {

        public BlurImageDecorator(ImageEditor nextLayer) {
            super(nextLayer);
        }

        @Override
        public Image readImage(String filePath) {
            Image image = nextLayer.readImage(filePath);
            return ImageUtils.applyBlur(image);
        }
}
