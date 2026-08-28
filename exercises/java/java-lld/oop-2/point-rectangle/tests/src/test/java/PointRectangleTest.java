import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;

import static org.junit.jupiter.api.Assertions.*;

public class PointRectangleTest {

    private static Class<?> pointClass;
    private static Class<?> rectangleClass;

    @BeforeEach
    public void setUp() throws Exception {
        try {
            pointClass = Class.forName("Point");
            rectangleClass = Class.forName("Rectangle");
        } catch (Exception e) {
            fail("Class Point or Rectangle not found");
        }
    }

    // ── Point tests ──────────────────────────────────────────────────────────

    @Test
    public void testXDataMemberExists() throws Exception {
        Field xField = pointClass.getDeclaredField("x");
        assertEquals(int.class, xField.getType(), "Data member x is not of type int");
    }

    @Test
    public void testYDataMemberExists() throws Exception {
        Field yField = pointClass.getDeclaredField("y");
        assertEquals(int.class, yField.getType(), "Data member y is not of type int");
    }

    @Test
    public void testTwoParamConstructorSignature() throws Exception {
        Constructor<?> cons = Point.class.getConstructor(int.class, int.class);
        Class<?>[] paramTypes = cons.getParameterTypes();
        assertEquals(2, paramTypes.length);
        assertEquals(int.class, paramTypes[0]);
        assertEquals(int.class, paramTypes[1]);
    }

    @Test
    public void testTwoParamConstructor() throws Exception {
        Constructor<?> cons = Point.class.getConstructor(int.class, int.class);
        Point p = (Point) cons.newInstance(3, 4);
        Field xField = Point.class.getDeclaredField("x");
        xField.setAccessible(true);
        Field yField = Point.class.getDeclaredField("y");
        yField.setAccessible(true);
        assertEquals(3, (int) xField.get(p));
        assertEquals(4, (int) yField.get(p));
    }

    @Test
    public void testCopyConstructorSignature() throws Exception {
        Constructor<?> cons = Point.class.getConstructor(Point.class);
        Class<?>[] paramTypes = cons.getParameterTypes();
        assertEquals(1, paramTypes.length);
        assertEquals(Point.class, paramTypes[0]);
    }

    @Test
    public void testCopyConstructor() throws Exception {
        Constructor<Point> twoParam = Point.class.getDeclaredConstructor(int.class, int.class);
        Point p1 = twoParam.newInstance(3, 4);
        Constructor<Point> copyParam = Point.class.getDeclaredConstructor(Point.class);
        Point p2 = copyParam.newInstance(p1);
        assertNotSame(p1, p2);
        Field xField = Point.class.getDeclaredField("x");
        xField.setAccessible(true);
        Field yField = Point.class.getDeclaredField("y");
        yField.setAccessible(true);
        assertEquals((int) xField.get(p1), (int) xField.get(p2));
        assertEquals((int) yField.get(p1), (int) yField.get(p2));
    }

    // ── Rectangle tests ──────────────────────────────────────────────────────

    @Test
    public void testTopLeftFieldExists() throws Exception {
        Field field = Rectangle.class.getDeclaredField("topLeft");
        assertEquals("Point", field.getType().getSimpleName());
    }

    @Test
    public void testBottomRightFieldExists() throws Exception {
        Field field = Rectangle.class.getDeclaredField("bottomRight");
        assertEquals("Point", field.getType().getSimpleName());
    }

    @Test
    public void testFourParamConstructorExists() throws Exception {
        Constructor<?> constructor = Rectangle.class.getDeclaredConstructor(
                int.class, int.class, int.class, int.class);
        assertTrue(Modifier.isPublic(constructor.getModifiers()));
    }

    @Test
    public void testTwoPointParamConstructorExists() throws Exception {
        Constructor<?> constructor = Rectangle.class.getDeclaredConstructor(Point.class, Point.class);
        assertTrue(Modifier.isPublic(constructor.getModifiers()));
    }

    @Test
    public void testRectangleCopyConstructorExists() throws Exception {
        Constructor<?> constructor = Rectangle.class.getDeclaredConstructor(Rectangle.class);
        assertTrue(Modifier.isPublic(constructor.getModifiers()));
    }

    @Test
    public void testRectangleDeepCopyWith2Points() throws Exception {
        Constructor<Rectangle> constructor = Rectangle.class.getDeclaredConstructor(Point.class, Point.class);
        Constructor<?> pointConstructor = Point.class.getConstructor(int.class, int.class);
        Point topLeft = (Point) pointConstructor.newInstance(1, 2);
        Point bottomRight = (Point) pointConstructor.newInstance(3, 4);
        Rectangle r1 = constructor.newInstance(topLeft, bottomRight);
        Field fieldTopLeft = Rectangle.class.getDeclaredField("topLeft");
        fieldTopLeft.setAccessible(true);
        Field fieldBottomRight = Rectangle.class.getDeclaredField("bottomRight");
        fieldBottomRight.setAccessible(true);
        assertFalse(topLeft == fieldTopLeft.get(r1), "topLeft must be a deep copy, not the same reference");
        assertFalse(bottomRight == fieldBottomRight.get(r1), "bottomRight must be a deep copy, not the same reference");
    }

    @Test
    public void testRectangleCopyConstructorDeepCopy() throws Exception {
        Constructor<Rectangle> twoParam = Rectangle.class.getDeclaredConstructor(Point.class, Point.class);
        Constructor<Rectangle> copyParam = Rectangle.class.getDeclaredConstructor(Rectangle.class);
        Constructor<?> pointConstructor = Point.class.getConstructor(int.class, int.class);
        Point topLeft = (Point) pointConstructor.newInstance(1, 2);
        Point bottomRight = (Point) pointConstructor.newInstance(3, 4);
        Rectangle r1 = twoParam.newInstance(topLeft, bottomRight);
        Rectangle r2 = copyParam.newInstance(r1);
        Field fieldTopLeft = Rectangle.class.getDeclaredField("topLeft");
        fieldTopLeft.setAccessible(true);
        assertFalse(fieldTopLeft.get(r1) == fieldTopLeft.get(r2),
                "Copy constructor must deep copy topLeft — not share the same reference");
    }

    @Test
    public void testFourParamConstructorValues() throws Exception {
        Constructor<Rectangle> constructor = Rectangle.class.getDeclaredConstructor(
                int.class, int.class, int.class, int.class);
        Rectangle r1 = constructor.newInstance(2, 3, 4, 5);
        Field fieldTopLeft = Rectangle.class.getDeclaredField("topLeft");
        fieldTopLeft.setAccessible(true);
        Field fieldBottomRight = Rectangle.class.getDeclaredField("bottomRight");
        fieldBottomRight.setAccessible(true);
        Object tl = fieldTopLeft.get(r1);
        Object br = fieldBottomRight.get(r1);
        Field fieldX = Point.class.getDeclaredField("x");
        fieldX.setAccessible(true);
        Field fieldY = Point.class.getDeclaredField("y");
        fieldY.setAccessible(true);
        assertEquals(2, fieldX.getInt(tl));
        assertEquals(3, fieldY.getInt(tl));
        assertEquals(4, fieldX.getInt(br));
        assertEquals(5, fieldY.getInt(br));
    }
}
