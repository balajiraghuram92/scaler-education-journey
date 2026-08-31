package com.assignment.question;

import com.assignment.question.external.AutoProtectApi;
import com.assignment.question.external.AutoProtectStatus;

public class AutoProtectAdapter implements TravelInsuranceAdapter {

    private AutoProtectApi autoProtectApi = new AutoProtectApi();

    @Override
    public void add(String reference, Double amount) {
        autoProtectApi.addClaim(amount);
    }

    @Override
    public ClaimStatus get(String reference) {
        AutoProtectStatus status =  autoProtectApi.getStatus(reference);
        if (status == AutoProtectStatus.APPROVED) {
            return ClaimStatus.APPROVED;
        }

        return ClaimStatus.PENDING;
    }
}
