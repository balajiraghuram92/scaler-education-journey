package com.assignment.question;

import com.assignment.question.external.TravelGuardApi;

public class TravelGuardAdapter implements TravelInsuranceAdapter {

    private TravelGuardApi travelGuardApi = new TravelGuardApi();

    @Override
    public void add(String reference, Double amount) {
        // TODO: delegate to travelGuardApi.submitClaim(...)
    }

    @Override
    public ClaimStatus get(String reference) {
        // TODO: call travelGuardApi.getClaimStatus(reference) and translate the
        // String status into a ClaimStatus
        return null;
    }
}
