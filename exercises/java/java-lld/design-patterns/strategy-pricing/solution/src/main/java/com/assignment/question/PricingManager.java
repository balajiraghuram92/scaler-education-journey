package com.assignment.question;

public class PricingManager {

    static final double BASE_FARE = 5.0; // Base fare amount

    private PricingType pricingType;
    private PricingStrategy pricingStrategy;
    public PricingManager(PricingType pricingType, PricingStrategy pricingStrategy) {
        this.pricingType = pricingType;
        this.pricingStrategy = pricingStrategy;
    }

    public Double calculatePrice(RideDetails rideDetails) {
        return pricingStrategy.calculatePrice(rideDetails);
    }

}
