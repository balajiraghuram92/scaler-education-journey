import org.junit.jupiter.api.Test;
import java.lang.reflect.*;

import static org.junit.jupiter.api.Assertions.*;

public class CounterTest {

    @Test
    public void testExistenceOfClassNamedCounter() {
        try {
            Class counterClass = Class.forName("Counter");
        } catch (Exception e) {
            fail("Counter class not found");
        }
    }


    @Test
    public void testFieldsOfCounterClass() {
        try {
            Class counterClass = Class.forName("Counter");
            Field field = counterClass.getDeclaredField("count");
            if(!Modifier.isPrivate(field.getModifiers())){
                fail("count field is not private");
            }
            if(!field.getType().getSimpleName().equals("int")){
                fail("count field is not of type int");
            }
        } catch (Exception e) {
            fail("count field does not exist");
        }
    }


    @Test
    public void testConstructor() {
        try {
            Class counterClass = Class.forName("Counter");
            Constructor constructor = counterClass.getDeclaredConstructor(int.class);
            if(!Modifier.isPublic(constructor.getModifiers())){
                fail("constructor is not public");
            }
        } catch (Exception e) {
            fail("Appropriate constructor not found");
        }
    }

    @Test
    public void testConstructorWorks() {
        try {
            Class counterClass = Class.forName("Counter");
            Constructor constructor = counterClass.getDeclaredConstructor(int.class);

            int initialCount = 5;
            Object counterObj = constructor.newInstance(initialCount);

            Field countField = counterClass.getDeclaredField("count");
            countField.setAccessible(true);
            int countValue = countField.getInt(counterObj);

            if(initialCount != countValue){
                fail("Constructor is not setting value of count variable.");
            }
        } catch (Exception e) {
            fail("Appropriate constructor not found");
        }
    }

    @Test
    public void testIncValueMethodSignatureAndModifiers() {
        try {
            Class counterClass = Class.forName("Counter");
            Method incValueMethod = counterClass.getDeclaredMethod("incValue", int.class);

            if (!incValueMethod.getReturnType().equals(void.class)) {
                fail("incValue method should've have void return type");
            }

            Class[] parameterTypes = incValueMethod.getParameterTypes();
            if (parameterTypes.length != 1) {
                fail("incValue method should have 1 parameter only");
            }

            if (!parameterTypes[0].equals(int.class)) {
                fail("incValue method should have 1 parameter of int type only");
            }

            if (!Modifier.isPublic(incValueMethod.getModifiers())) {
                fail("incValue method should be public");
            }

            if (!Modifier.isSynchronized(incValueMethod.getModifiers())) {
                fail("incValue method should be synchronized");
            }
        } catch (Exception e) {
            fail("incValue method not found");
        }
    }

    @Test
    public void testDecValueMethodSignatureAndModifiers() {
        try {
            Class counterClass = Class.forName("Counter");
            Method decValueMethod = counterClass.getDeclaredMethod("decValue", int.class);

            if (!decValueMethod.getReturnType().equals(void.class)) {
                fail("decValue method should've have void return type");
            }

            Class[] parameterTypes = decValueMethod.getParameterTypes();
            if (parameterTypes.length != 1) {
                fail("decValue method should have 1 parameter only");
            }

            if (!parameterTypes[0].equals(int.class)) {
                fail("decValue method should have 1 parameter of int type only");
            }

            if (!Modifier.isPublic(decValueMethod.getModifiers())) {
                fail("decValue method should be public");
            }

            if (!Modifier.isSynchronized(decValueMethod.getModifiers())) {
                fail("decValue method should be synchronized");
            }
        } catch (Exception e) {
            fail("decValue method not found");
        }
    }

    @Test
    public void testGetValueMethodSignatureAndModifiers() {
        try {
            Class counterClass = Class.forName("Counter");
            Method getValueMethod = counterClass.getDeclaredMethod("getValue");

            if (!getValueMethod.getReturnType().equals(int.class)) {
                fail("getValue method should've have int return type");
            }

            Class[] parameterTypes = getValueMethod.getParameterTypes();
            if (parameterTypes.length != 0) {
                fail("getValue method should have 0 parameters only");
            }

            if (!Modifier.isPublic(getValueMethod.getModifiers())) {
                fail("getValue method should be public");
            }

            if (!Modifier.isSynchronized(getValueMethod.getModifiers())) {
                fail("getValue method should be synchronized");
            }
        } catch (Exception e) {
            fail("getValue method not found");
        }
    }

    @Test
    public void testFunctionality() throws Exception {
        int initialCount = 0;
        int incrementValue = 5;
        int decrementValue = 3;

        // Use reflection to obtain the Counter class
        Class counterClass = Class.forName("Counter");

        // Get the constructor of the Counter class that takes an int parameter
        Constructor<?> constructor = counterClass.getDeclaredConstructor(int.class);
        constructor.setAccessible(true);

        // Create an instance of Counter using the constructor
        Object counterObj = constructor.newInstance(initialCount);

        // Verify initial count using reflection
        Method getValueMethod = counterClass.getDeclaredMethod("getValue");
        int countValue = (int) getValueMethod.invoke(counterObj);
        if(initialCount != countValue){
            fail("getValue not returning the correct value of count");
        }

        Method incValueMethod = counterClass.getDeclaredMethod("incValue", int.class);
        incValueMethod.invoke(counterObj, incrementValue);
        countValue = (int) getValueMethod.invoke(counterObj);
        if(initialCount + incrementValue != countValue){
            fail("incValue not incrementing the value of count");
        }

        Method decValueMethod = counterClass.getDeclaredMethod("decValue", int.class);
        decValueMethod.invoke(counterObj, decrementValue);
        countValue = (int) getValueMethod.invoke(counterObj);
        if(initialCount + incrementValue - decrementValue != countValue){
            fail("decValue not decrementing the value of count");
        }
    }
}
