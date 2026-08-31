package contest;

import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

public class FileStorageTest {

  private static final Class < ? > rawFileStorageClass = RawFileStorage.class;
  private static final Class < ? > baseFileDecoratorClass = BaseFileDecorator.class;
  private static final Class < ? > compressionDecoratorClass = CompressionDecorator.class;
  private static final Class < ? > virusScanningDecoratorClass = VirusScanningDecorator.class;

  @Test
  public void testFileStorageInterfaceMethods() {
    Method[] methods = FileStorage.class.getDeclaredMethods();
    assertTrue(methods.length >= 2, "If the decorator pattern is implemented correctly, contest.FileStorage should have at least 2 methods: storeFile and getFile.");

    boolean hasStoreFileMethod = Stream.of(methods).anyMatch(method -> method.getName().equals("storeFile") && method.getParameterCount() == 2 && method.getParameterTypes()[0] == String.class && method.getParameterTypes()[1] == byte[].class);

    boolean hasGetFileMethod = Stream.of(methods).anyMatch(method -> method.getName().equals("getFile") && method.getParameterCount() == 1 && method.getParameterTypes()[0] == String.class && method.getReturnType() == byte[].class);

    assertTrue(hasStoreFileMethod, "If the decorator pattern is implemented correctly, contest.FileStorage should have a storeFile method that takes a String and a byte[].");
    assertTrue(hasGetFileMethod, "If the decorator pattern is implemented correctly, contest.FileStorage should have a getFile method that takes a String and returns a byte[].");
  }

  @Test
  public void testRawFileStorageImplementation() {
    assertTrue(FileStorage.class.isAssignableFrom(rawFileStorageClass), "If the decorator pattern is implemented correctly, contest.RawFileStorage should implement the contest.FileStorage interface.");
  }

  @Test
  public void testBaseFileDecoratorImplementation() {
    assertTrue(FileStorage.class.isAssignableFrom(baseFileDecoratorClass), "If the decorator pattern is implemented correctly, contest.BaseFileDecorator should implement the contest.FileStorage interface.");

    var fields = baseFileDecoratorClass.getDeclaredFields();
    boolean hasNextLayerField = Stream.of(fields).anyMatch(field -> field.getType().equals(FileStorage.class));

    // This is the CORRECT place to check for the nextLayer field
    assertTrue(hasNextLayerField, "If the decorator pattern is implemented correctly, contest.BaseFileDecorator should have a field to store the next layer.");

    try {
      Constructor < ? > constructor = baseFileDecoratorClass.getConstructor(FileStorage.class);
      assertNotNull(constructor, "If the decorator pattern is implemented correctly, contest.BaseFileDecorator should have a constructor that takes a contest.FileStorage instance.");
    } catch (NoSuchMethodException e) {
      fail("If the decorator pattern is implemented correctly, contest.BaseFileDecorator should have a constructor that takes a contest.FileStorage instance.");
    }
  }

  @Test
  public void testCompressionDecoratorImplementation() {
    assertTrue(baseFileDecoratorClass.isAssignableFrom(compressionDecoratorClass), "If the decorator pattern is implemented correctly, contest.CompressionDecorator should extend the contest.BaseFileDecorator class.");

    // [REMOVED FLAWED DECLARED FIELDS CHECK]

    Constructor < ? > [] constructors = compressionDecoratorClass.getDeclaredConstructors();
    boolean hasConstructorWithFileStorage = Stream.of(constructors).anyMatch(constructor -> {
      Class < ? > [] parameterTypes = constructor.getParameterTypes();
      return parameterTypes.length == 1 && parameterTypes[0].equals(FileStorage.class);
    });

    assertTrue(hasConstructorWithFileStorage, "If the decorator pattern is implemented correctly, contest.CompressionDecorator should have a constructor that takes a contest.FileStorage instance.");
  }

  @Test
  public void testVirusScanningDecoratorImplementation() {
    assertTrue(baseFileDecoratorClass.isAssignableFrom(virusScanningDecoratorClass), "If the decorator pattern is implemented correctly, contest.VirusScanningDecorator should extend the contest.BaseFileDecorator class.");

    // [REMOVED FLAWED DECLARED FIELDS CHECK]

    Constructor < ? > [] constructors = virusScanningDecoratorClass.getDeclaredConstructors();
    boolean hasConstructorWithFileStorage = Stream.of(constructors).anyMatch(constructor -> {
      Class < ? > [] parameterTypes = constructor.getParameterTypes();
      return parameterTypes.length == 1 && parameterTypes[0].equals(FileStorage.class);
    });

    assertTrue(hasConstructorWithFileStorage, "If the decorator pattern is implemented correctly, contest.VirusScanningDecorator should have a constructor that takes a contest.FileStorage instance.");
  }
}
