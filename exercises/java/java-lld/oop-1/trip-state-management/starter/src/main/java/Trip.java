public class Trip {
    private String tripId;
    private String passengerId;
    private String driverId;
    private String status;

    public Trip(String tripId, String passengerId) {
        this.tripId = tripId;
        this.passengerId = passengerId;
        this.status = "REQUESTED";
    }

    public String getTripId() {
        return tripId;
    }

    public String getPassengerId() {
        return passengerId;
    }

    public String getDriverId() {
        return driverId;
    }

    public String getStatus() {
        return status;
    }

    // TODO: Implement acceptTrip(String driverId) throws TripException
    // Invariants:
    // 1. Can only accept if status is "REQUESTED". Otherwise throw TripException.
    // 2. driverId must not be null or blank. Otherwise throw TripException.
    // 3. Sets this.driverId to driverId and this.status to "ACCEPTED_BY_DRIVER".
    public void acceptTrip(String driverId) throws TripException {
        // TODO: Implement method
    }

    // TODO: Implement cancelTrip() throws TripException
    // Invariants:
    // 1. Cannot cancel if status is "IN_PROGRESS" or "COMPLETED". Throw TripException.
    // 2. Sets this.status to "CANCELLED".
    public void cancelTrip() throws TripException {
        // TODO: Implement method
    }
}
