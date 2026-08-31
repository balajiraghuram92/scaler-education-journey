package com.assignment.question;

import static com.assignment.question.PricingManager.BASE_FARE;

// TODO: implement PricingStrategy — supportsType() returns SURGE,
// calculatePrice(...) returns BASE_FARE times a surge multiplier.
public class SurgePricingStrategy implements PricingStrategy {
    private static final double SURGE_MULTIPLIER = 2.0; // Surge pricing multiplier

    @Override
    public PricingType supportsType() {
        return null;
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        return null;
    }
}
