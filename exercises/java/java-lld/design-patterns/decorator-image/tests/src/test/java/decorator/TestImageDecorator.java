package decorator;

import decorator.utils.Image;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

public class TestImageDecorator {

    private static final Class<?> rawImageEditorClass = RawImageEditor.class;
    private static final Class<?> baseImageDecoratorClass = BaseImageDecorator.class;
    private static final Class<?> blurImageDecoratorClass = BlurImageDecorator.class;
    private static final Class<?> grayscaleImageDecoratorClass = GrayscaleImageDecorator.class;

    @Test
    public void testImageEditorInterfaceMethods() {
        Method[] methods = ImageEditor.class.getDeclaredMethods();
        assertTrue(methods.length >= 1, "If the decorator pattern is implemented correctly, ImageEditor should have at least 1 methods: readImage.");

        boolean hasGetFileMethod = Stream.of(methods).anyMatch(method -> method.getName().equals("readImage") && method.getParameterCount() == 1 && method.getParameterTypes()[0] == String.class && method.getReturnType() == Image.class);
        assertTrue(hasGetFileMethod, "If the decorator pattern is implemented correctly, ImageEditor should have a readImage method that takes a String and returns an Image.");
    }

    @Test
    public void testRawImageEditorImplementation() {
        assertTrue(ImageEditor.class.isAssignableFrom(rawImageEditorClass), "If the decorator pattern is implemented correctly, RawImageEditor should implement the ImageEditor interface.");
    }

    @Test
    public void testBaseImageDecoratorImplementation() {
        assertTrue(ImageEditor.class.isAssignableFrom(baseImageDecoratorClass), "If the decorator pattern is implemented correctly, BaseImageDecorator should implement the ImageEditor interface.");

        var fields = baseImageDecoratorClass.getDeclaredFields();
        boolean hasNextLayerField = Stream.of(fields).anyMatch(field -> field.getType().equals(ImageEditor.class));

        assertTrue(hasNextLayerField, "If the decorator pattern is implemented correctly, BaseImageDecorator should have a field to store the next layer.");

        try {
            Constructor<?> constructor = baseImageDecoratorClass.getConstructor(ImageEditor.class);
            assertNotNull(constructor, "If the decorator pattern is implemented correctly, BaseImageDecorator should have a constructor that takes a ImageEditor instance.");
        } catch (NoSuchMethodException e) {
            fail("If the decorator pattern is implemented correctly, BaseImageDecorator should have a constructor that takes a ImageEditor instance.");
        }
    }

    @Test
    public void testBlurImageDecoratorImplementation() {
        assertTrue(baseImageDecoratorClass.isAssignableFrom(blurImageDecoratorClass), "If the decorator pattern is implemented correctly, BlurImageDecorator should extend the BaseImageDecorator class.");

        Constructor<?>[] constructors = blurImageDecoratorClass.getDeclaredConstructors();
        boolean hasConstructorWithImageEditor = Stream.of(constructors).anyMatch(constructor -> {
            Class<?>[] parameterTypes = constructor.getParameterTypes();
            return parameterTypes.length == 1 && parameterTypes[0].equals(ImageEditor.class);
        });

        assertTrue(hasConstructorWithImageEditor, "If the decorator pattern is implemented correctly, BlurImageDecorator should have a constructor that takes a ImageEditor instance.");
    }


    @Test
    public void testGrayscaleImageDecoratorImplementation() {

        assertTrue(baseImageDecoratorClass.isAssignableFrom(grayscaleImageDecoratorClass), "If the decorator pattern is implemented correctly, GrayscaleImageDecorator should extend the BaseImageDecorator class.");

        Constructor<?>[] constructors = grayscaleImageDecoratorClass.getDeclaredConstructors();
        boolean hasConstructorWithImageEditor = Stream.of(constructors).anyMatch(constructor -> {
            Class<?>[] parameterTypes = constructor.getParameterTypes();
            return parameterTypes.length == 1 && parameterTypes[0].equals(ImageEditor.class);
        });

        assertTrue(hasConstructorWithImageEditor, "If the decorator pattern is implemented correctly, GrayscaleImageDecorator should have a constructor that takes a ImageEditor instance.");

    }

}
