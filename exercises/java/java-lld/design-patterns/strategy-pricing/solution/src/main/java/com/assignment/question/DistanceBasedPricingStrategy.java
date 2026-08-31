package com.assignment.question;

import static com.assignment.question.PricingManager.BASE_FARE;

public class DistanceBasedPricingStrategy implements PricingStrategy {

    private static final double PER_KILOMETER_RATE = 2.0; // Rate per kilometer

    @Override
    public PricingType supportsType() {
        return PricingType.DISTANCE_BASED;
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        return BASE_FARE + PER_KILOMETER_RATE * rideDetails.getDistance();
    }
}
