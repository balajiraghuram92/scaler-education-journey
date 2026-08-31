package com.assignment.question;

import static com.assignment.question.PricingManager.BASE_FARE;

public class SurgePricingStrategy implements PricingStrategy {
    private static final double SURGE_MULTIPLIER = 2.0; // Surge pricing multiplier

    @Override
    public PricingType supportsType() {
        return PricingType.SURGE;
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        return BASE_FARE * SURGE_MULTIPLIER;
    }
}
