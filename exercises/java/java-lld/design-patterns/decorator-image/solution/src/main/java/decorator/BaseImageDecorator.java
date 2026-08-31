package decorator;

public abstract class BaseImageDecorator implements ImageEditor {
    protected ImageEditor nextLayer;

    public BaseImageDecorator(ImageEditor nextLayer) {
        this.nextLayer = nextLayer;
    }
}
