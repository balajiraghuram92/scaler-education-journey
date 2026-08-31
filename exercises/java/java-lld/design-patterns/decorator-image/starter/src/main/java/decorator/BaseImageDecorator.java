package decorator;

/**
 * TODO - Each decorator should have the same methods as the product it decorates, i.e. readImage.
 * Inherit from the image editor interface {@link ImageEditor}.
 *
 * TODO - Each decorator will have to call the next decorator in the chain and finally call the raw
 * image editor. To achieve this, add a protected field of type {@link ImageEditor} storing the
 * next layer, and a constructor taking that next layer.
 */
public abstract class BaseImageDecorator implements ImageEditor {

}
