package com.assignment.controllers;

import com.assignment.dtos.MakePaymentRequestDto;
import com.assignment.dtos.MakePaymentResponseDto;
import com.assignment.dtos.ResponseStatus;
import com.assignment.models.Payment;
import com.assignment.services.PaymentService;

public class PaymentController {

    private PaymentService paymentService;

    public PaymentController(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    public MakePaymentResponseDto makePayment(MakePaymentRequestDto makePaymentRequestDto) {
        MakePaymentResponseDto makePaymentResponseDto = new MakePaymentResponseDto();
        try{
            Payment payment = paymentService.makePayment(makePaymentRequestDto.getBillId());
            makePaymentResponseDto.setResponseStatus(ResponseStatus.SUCCESS);
            makePaymentResponseDto.setPaymentStatus(payment.getPaymentStatus());
            makePaymentResponseDto.setTxnId(payment.getTxnId());
            return makePaymentResponseDto;
        } catch (Exception e) {
            makePaymentResponseDto.setResponseStatus(ResponseStatus.FAILURE);
            return makePaymentResponseDto;
        }
    }
}