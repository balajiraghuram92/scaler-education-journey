package com.assignment.services;

import com.assignment.exceptions.InvalidBillException;
import com.assignment.models.Payment;

public interface PaymentService {

    Payment makePayment(long billId) throws InvalidBillException;
}