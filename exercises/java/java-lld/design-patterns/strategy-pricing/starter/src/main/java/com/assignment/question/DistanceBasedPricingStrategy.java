package com.assignment.question;

import static com.assignment.question.PricingManager.BASE_FARE;

// TODO: implement PricingStrategy — supportsType() returns DISTANCE_BASED,
// calculatePrice(...) returns BASE_FARE + a per-kilometer rate times distance.
public class DistanceBasedPricingStrategy implements PricingStrategy {

    private static final double PER_KILOMETER_RATE = 2.0; // Rate per kilometer

    @Override
    public PricingType supportsType() {
        return null;
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        return null;
    }
}
