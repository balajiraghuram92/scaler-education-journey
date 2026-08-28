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

    public void acceptTrip(String driverId) throws TripException {
        if (!"REQUESTED".equals(this.status)) {
            throw new TripException("Cannot accept trip in state: " + this.status);
        }
        if (driverId == null || driverId.trim().isEmpty()) {
            throw new TripException("Driver ID cannot be empty");
        }
        this.driverId = driverId;
        this.status = "ACCEPTED_BY_DRIVER";
    }

    public void cancelTrip() throws TripException {
        if ("IN_PROGRESS".equals(this.status) || "COMPLETED".equals(this.status)) {
            throw new TripException("Cannot cancel trip in state: " + this.status);
        }
        this.status = "CANCELLED";
    }
}
