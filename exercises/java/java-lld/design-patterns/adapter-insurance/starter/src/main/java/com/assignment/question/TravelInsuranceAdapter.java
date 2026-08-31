package com.assignment.question;

public interface TravelInsuranceAdapter {

    void add(String reference, Double amount);

    ClaimStatus get(String reference);
}
