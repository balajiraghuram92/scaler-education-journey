package com.assignment.services;

import com.assignment.adapters.PaymentGatewayAdapter;
import com.assignment.exceptions.InvalidBillException;
import com.assignment.models.Bill;
import com.assignment.models.Payment;
import com.assignment.repositories.BillRepository;

public class PaymentServiceImpl implements PaymentService{

    private BillRepository billRepository;
    private PaymentGatewayAdapter paymentGatewayAdapter;

    public PaymentServiceImpl(BillRepository billRepository, PaymentGatewayAdapter paymentGatewayAdapter) {
        this.billRepository = billRepository;
        this.paymentGatewayAdapter = paymentGatewayAdapter;
    }

    @Override
    public Payment makePayment(long billId) throws InvalidBillException {
        Bill bill = billRepository.findById(billId).orElseThrow(() -> new InvalidBillException("Bill not found"));
        return paymentGatewayAdapter.makePayment(billId, bill.getTotalAmount());
    }
}