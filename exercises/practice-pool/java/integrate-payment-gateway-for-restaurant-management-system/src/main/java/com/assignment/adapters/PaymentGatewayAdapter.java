package com.assignment.adapters;

import com.scaler.models.Payment;

public interface PaymentGatewayAdapter {

    Payment makePayment(long billId, double amount);
}