public class Rider {
    private String name;
    private String email;
    private String phoneNumber;
    private String savedHomeAddress;
    private double rating;
    private boolean isActive;
    private static int totalRiders = 0;

    // TODO: Implement constructor Rider(String name, String email, String phoneNumber) throws RiderException
    // 1. Validate email is not null and not empty (trim().isEmpty()). Otherwise throw RiderException.
    // 2. Set this.name, this.email, this.phoneNumber.
    // 3. Set this.rating = 5.0 (default initial rating).
    // 4. Set this.isActive = true.
    // 5. Increment totalRiders.
    public Rider(String name, String email, String phoneNumber) throws RiderException {
        // TODO: Implement constructor
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

    // TODO: Implement setRating(double r) throws RiderException
    // Validate: rating must be between 1.0 and 5.0 inclusive. Outside range throws RiderException.
    public void setRating(double r) throws RiderException {
        // TODO: Implement method
    }

    // TODO: Implement saveHomeAddress(String address) throws RiderException
    // Validate: rider must be active (isActive == true). Otherwise throw RiderException.
    public void saveHomeAddress(String address) throws RiderException {
        // TODO: Implement method
    }

    // TODO: Implement deactivate() throws RiderException
    // Validate: if rider is already inactive (!isActive), throw RiderException.
    // Otherwise set isActive to false.
    public void deactivate() throws RiderException {
        // TODO: Implement method
    }

    // TODO: Implement getMaskedEmail()
    // Returns email with everything before '@' replaced with '****', e.g. "rahul@gmail.com" -> "****@gmail.com"
    public String getMaskedEmail() {
        return null;
    }

    public static int getTotalRiders() {
        return totalRiders;
    }
}
