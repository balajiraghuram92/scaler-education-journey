package com.assignment.question;

import com.assignment.question.external.AutoProtectApi;
import com.assignment.question.external.AutoProtectStatus;

public class AutoProtectAdapter implements TravelInsuranceAdapter {

    private AutoProtectApi autoProtectApi = new AutoProtectApi();

    @Override
    public void add(String reference, Double amount) {
        // TODO: delegate to autoProtectApi.addClaim(...)
    }

    @Override
    public ClaimStatus get(String reference) {
        // TODO: call autoProtectApi.getStatus(reference) and translate the
        // AutoProtectStatus into a ClaimStatus (APPROVED maps to APPROVED,
        // anything else maps to PENDING)
        return null;
    }
}
