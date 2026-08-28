import org.junit.jupiter.api.Test;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import static org.junit.jupiter.api.Assertions.*;

public class TripTest {

    @Test
    public void testTripFieldsArePrivate() {
        for (String fieldName : new String[]{"status", "driverId", "passengerId", "tripId"}) {
            try {
                Field field = Trip.class.getDeclaredField(fieldName);
                assertTrue(Modifier.isPrivate(field.getModifiers()), "Field " + fieldName + " must be private");
            } catch (NoSuchFieldException e) {
                fail("Field " + fieldName + " does not exist on Trip class");
            }
        }
    }

    @Test
    public void testAcceptTripValidTransition() throws Exception {
        Trip trip = new Trip("T1", "P100");
        assertEquals("REQUESTED", trip.getStatus());
        trip.acceptTrip("D500");
        assertEquals("ACCEPTED_BY_DRIVER", trip.getStatus());
        assertEquals("D500", trip.getDriverId());
    }

    @Test
    public void testAcceptTripInvalidTransitionThrows() throws Exception {
        Trip trip = new Trip("T1", "P100");
        trip.acceptTrip("D500");
        assertThrows(TripException.class, () -> trip.acceptTrip("D501"));
    }

    @Test
    public void testCancelTripValidTransition() throws Exception {
        Trip trip = new Trip("T1", "P100");
        trip.cancelTrip();
        assertEquals("CANCELLED", trip.getStatus());
    }

    @Test
    public void testCancelTripInvalidTransitionThrows() throws Exception {
        Trip trip = new Trip("T1", "P100");
        trip.cancelTrip();
        
        Field statusField = Trip.class.getDeclaredField("status");
        statusField.setAccessible(true);
        
        statusField.set(trip, "IN_PROGRESS");
        assertThrows(TripException.class, () -> trip.cancelTrip());

        statusField.set(trip, "COMPLETED");
        assertThrows(TripException.class, () -> trip.cancelTrip());
    }

    @Test
    public void testNoPublicStatusSetter() {
        for (Method method : Trip.class.getDeclaredMethods()) {
            if (method.getName().equalsIgnoreCase("setStatus") && Modifier.isPublic(method.getModifiers())) {
                fail("Trip must not declare a public setStatus method; state must be encapsulated");
            }
        }
    }
}
