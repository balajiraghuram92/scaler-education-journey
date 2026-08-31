package decorator.utils;

public class ImageUtils {
    public static Image read(String filePath) {
        return new Image(filePath);
    }

    public static Image convertToGrayscale(Image image) {
        return image;
    }

    public static Image applyBlur(Image image) {
        return image;
    }

    public static void render(Image image) {

    }
}
