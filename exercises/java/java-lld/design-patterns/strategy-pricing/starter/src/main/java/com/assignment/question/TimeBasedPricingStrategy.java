package com.assignment.question;

import static com.assignment.question.PricingManager.BASE_FARE;

// TODO: implement PricingStrategy — supportsType() returns TIME_BASED,
// calculatePrice(...) returns BASE_FARE + a per-minute rate times duration.
public class TimeBasedPricingStrategy implements PricingStrategy {

    private static final double PER_MINUTE_RATE = 0.5; // Rate per minute

    @Override
    public PricingType supportsType() {
        return null;
    }

    @Override
    public Double calculatePrice(RideDetails rideDetails) {
        return null;
    }
}
