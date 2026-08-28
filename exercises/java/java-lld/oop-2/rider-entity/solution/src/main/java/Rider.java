public class Rider {
    private String name;
    private String email;
    private String phoneNumber;
    private String savedHomeAddress;
    private double rating;
    private boolean isActive;
    private static int totalRiders = 0;

    public Rider(String name, String email, String phoneNumber) throws RiderException {
        if (email == null || email.trim().isEmpty()) {
            throw new RiderException("Email cannot be null or empty");
        }
        this.name = name;
        this.email = email;
        this.phoneNumber = phoneNumber;
        this.rating = 5.0;
        this.isActive = true;
        this.savedHomeAddress = null;
        totalRiders++;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public String getSavedHomeAddress() {
        return savedHomeAddress;
    }

    public double getRating() {
        return rating;
    }

    public boolean isActive() {
        return isActive;
    }

    public void setRating(double r) throws RiderException {
        if (r < 1.0 || r > 5.0) {
            throw new RiderException("Rating must be between 1.0 and 5.0, got: " + r);
        }
        this.rating = r;
    }

    public void saveHomeAddress(String address) throws RiderException {
        if (!this.isActive) {
            throw new RiderException("Cannot save address for inactive rider");
        }
        this.savedHomeAddress = address;
    }

    public void deactivate() throws RiderException {
        if (!this.isActive) {
            throw new RiderException("Rider is already inactive");
        }
        this.isActive = false;
    }

    public String getMaskedEmail() {
        if (email == null) return null;
        int atIndex = email.indexOf('@');
        if (atIndex < 0) {
            return "****";
        }
        return "****" + email.substring(atIndex);
    }

    public static int getTotalRiders() {
        return totalRiders;
    }
}
