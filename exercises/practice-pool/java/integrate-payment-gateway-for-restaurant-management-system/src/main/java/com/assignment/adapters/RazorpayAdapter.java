package com.assignment.adapters;

import com.assignment.libraries.razorpay.RazorpayApi;
import com.assignment.libraries.razorpay.RazorpayPaymentResponse;
import com.assignment.models.Payment;
import com.assignment.models.PaymentStatus;

public class RazorpayAdapter implements PaymentGatewayAdapter{

    private RazorpayApi razorpayApi = new RazorpayApi();
    @Override
    public Payment makePayment(long billId, double amount) {
        RazorpayPaymentResponse razorpayPaymentResponse = razorpayApi.processPayment(billId, amount);
        Payment payment = new Payment();
        payment.setTxnId(razorpayPaymentResponse.getTransactionId());
        payment.setPaymentStatus(PaymentStatus.valueOf(razorpayPaymentResponse.getPaymentStatus()));
        payment.setBillId(billId);
        return payment;
    }
}