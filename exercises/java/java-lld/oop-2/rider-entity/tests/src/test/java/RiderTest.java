import org.junit.jupiter.api.Test;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import static org.junit.jupiter.api.Assertions.*;

public class RiderTest {

    @Test
    public void testConstructorValidInitialState() throws Exception {
        Rider rider = new Rider("Rahul", "rahul@gmail.com", "+919876543210");
        assertEquals("Rahul", rider.getName());
        assertEquals("rahul@gmail.com", rider.getEmail());
        assertEquals("+919876543210", rider.getPhoneNumber());
        assertTrue(rider.isActive());
        assertEquals(5.0, rider.getRating(), 0.001);
        assertNull(rider.getSavedHomeAddress());
    }

    @Test
    public void testConstructorInvalidEmailThrows() {
        assertThrows(RiderException.class, () -> new Rider("Rahul", null, "+919876543210"));
        assertThrows(RiderException.class, () -> new Rider("Rahul", "   ", "+919876543210"));
        assertThrows(RiderException.class, () -> new Rider("Rahul", "", "+919876543210"));
    }

    @Test
    public void testSetRatingValidAndInvalid() throws Exception {
        Rider rider = new Rider("Rahul", "rahul@gmail.com", "+919876543210");
        rider.setRating(4.2);
        assertEquals(4.2, rider.getRating(), 0.001);

        assertThrows(RiderException.class, () -> rider.setRating(0.9));
        assertThrows(RiderException.class, () -> rider.setRating(5.1));
        assertThrows(RiderException.class, () -> rider.setRating(6.0));
    }

    @Test
    public void testSaveHomeAddressWhenActiveAndInactive() throws Exception {
        Rider rider = new Rider("Rahul", "rahul@gmail.com", "+919876543210");
        rider.saveHomeAddress("123 Indiranagar, Bengaluru");
        assertEquals("123 Indiranagar, Bengaluru", rider.getSavedHomeAddress());

        rider.deactivate();
        assertThrows(RiderException.class, () -> rider.saveHomeAddress("456 Koramangala"));
    }

    @Test
    public void testDeactivateIdempotencyThrows() throws Exception {
        Rider rider = new Rider("Rahul", "rahul@gmail.com", "+919876543210");
        assertTrue(rider.isActive());
        rider.deactivate();
        assertFalse(rider.isActive());
        assertThrows(RiderException.class, () -> rider.deactivate());
    }

    @Test
    public void testGetMaskedEmail() throws Exception {
        Rider rider1 = new Rider("Rahul", "rahul@gmail.com", "+919876543210");
        assertEquals("****@gmail.com", rider1.getMaskedEmail());

        Rider rider2 = new Rider("Priya", "priya.sharma123@yahoo.co.in", "+919876543211");
        assertEquals("****@yahoo.co.in", rider2.getMaskedEmail());
    }

    @Test
    public void testStaticTotalRidersCount() throws Exception {
        int initialCount = Rider.getTotalRiders();
        new Rider("R1", "r1@test.com", "111");
        new Rider("R2", "r2@test.com", "222");
        new Rider("R3", "r3@test.com", "333");
        assertEquals(initialCount + 3, Rider.getTotalRiders());
    }

    @Test
    public void testFieldsArePrivateAndEncapsulated() {
        for (String fieldName : new String[]{"name", "email", "phoneNumber", "savedHomeAddress", "rating", "isActive"}) {
            try {
                Field field = Rider.class.getDeclaredField(fieldName);
                assertTrue(Modifier.isPrivate(field.getModifiers()), "Field " + fieldName + " must be private");
            } catch (NoSuchFieldException e) {
                fail("Field " + fieldName + " does not exist on Rider class");
            }
        }

        for (Method method : Rider.class.getDeclaredMethods()) {
            if (method.getName().equalsIgnoreCase("setActive") || method.getName().equalsIgnoreCase("setIsActive") ||
                method.getName().equalsIgnoreCase("setEmail")) {
                if (Modifier.isPublic(method.getModifiers())) {
                    fail("Rider must not declare public setter: " + method.getName());
                }
            }
        }
    }
}
