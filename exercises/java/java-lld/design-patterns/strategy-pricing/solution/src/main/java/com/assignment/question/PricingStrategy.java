package com.assignment.question;

public interface PricingStrategy {
    PricingType supportsType();

    Double calculatePrice(RideDetails rideDetails);
}
