import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.lang.reflect.*;

import static org.junit.jupiter.api.Assertions.*;

public class ThreedPointTest {

    @Test
    public void testPointHasX() {
        try {
            Field field = Point.class.getDeclaredField("x");
            assertTrue(Modifier.isProtected(field.getModifiers()));
            assertEquals("int", field.getType().getSimpleName());
        } catch (NoSuchFieldException e) {
            fail("Field x does not exist");
        }
    }


    @Test
    public void testPointHasY() {
        try {
            Field field = Point.class.getDeclaredField("y");
            assertTrue(Modifier.isProtected(field.getModifiers()));
            assertEquals("int", field.getType().getSimpleName());
        } catch (NoSuchFieldException e) {
            fail("Field y does not exist");
        }
    }


    @Test
    public void testPointHasDisplay() {
        try {
            Method method = Point.class.getDeclaredMethod("display");
            assertTrue(Modifier.isPublic(method.getModifiers()));
            assertEquals(void.class, method.getReturnType());
            assertEquals(0, method.getParameterCount());
        } catch (NoSuchMethodException e) {
            fail("Method display does not exist");
        }
    }


    @Test
    public void testPointDisplay() throws Exception {
        try {
            ByteArrayOutputStream outContent = new ByteArrayOutputStream();
            System.setOut(new PrintStream(outContent));
            Constructor<Point> constructor = Point.class.getDeclaredConstructor();
            Point p = constructor.newInstance();

            Field xField = Point.class.getDeclaredField("x");
            xField.setAccessible(true);
            xField.set(p, 1);

            Field yField = Point.class.getDeclaredField("y");
            yField.setAccessible(true);
            yField.set(p, 2);

            Method displayMethod = Point.class.getDeclaredMethod("display");
            displayMethod.invoke(p);

            assertEquals("[1, 2]\n", outContent.toString());
        } catch (Exception e) {
            fail("Exception thrown: " + e);
        }
    }


    @Test
    public void testThreedPointInheritsPoint(){
        assertTrue(Point.class.isAssignableFrom(ThreedPoint.class));
    }

    @Test
    public void testThreedPointDisplayMethodOverride() throws Exception{
        try {
            Method method = ThreedPoint.class.getDeclaredMethod("display");
            assertTrue(Modifier.isPublic(method.getModifiers()));
            assertEquals(void.class, method.getReturnType());
            assertEquals(0, method.getParameterCount());
        } catch (Exception e) {
            fail("Exception thrown: " + e);
        }
    }
    

    @Test
    public void testThreedPointDisplayMethodOutput() throws Exception {
        try {
                ByteArrayOutputStream outContent = new ByteArrayOutputStream();
                System.setOut(new PrintStream(outContent));

                Constructor<ThreedPoint> constructor = ThreedPoint.class.getDeclaredConstructor();
                Field xField = Point.class.getDeclaredField("x");
                xField.setAccessible(true);
                Field yField = Point.class.getDeclaredField("y");
                yField.setAccessible(true);
                Field zField = ThreedPoint.class.getDeclaredField("z");
                zField.setAccessible(true);

                ThreedPoint p = constructor.newInstance();
                xField.set(p, 1);
                yField.set(p, 2);
                zField.set(p, 3);

                Method displayMethod = ThreedPoint.class.getDeclaredMethod("display");
                displayMethod.invoke(p);

                assertEquals("[1, 2, 3]\n", outContent.toString());
        } catch (Exception e) {
            fail("Exception thrown: " + e);
        }
    }



}
