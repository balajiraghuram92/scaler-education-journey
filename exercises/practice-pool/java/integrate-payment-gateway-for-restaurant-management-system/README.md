# Integrate Payment Gateway for Restaurant Management System

## Problem Statement
You are building a Restaurant Management System. As a part of this system, you need to integrate Paytm and Razorpay's payment gateway in to your system.

## Assignment

Your task is to integrate both Paytm and Razorpay payment gateway in a SOLID compliant manner with the make payment functionality of our system.

#### Requirements

1. Make request functionality will get bill id as input.
2. If an invalid bill id is given to this functionality, we should get an error saying "Invalid bill id".
3. When a valid bill id is given, you need to get the total amount from the bill details stored in the database and make a call to payment gateway to start the transaction. Once the transaction completes, we need to give the payment status and transaction id in response.
4. We need to implement the payment gateways integration in such a way that it should be very easy for us to migrate from 1 gateway to another.

#### Instructions

* Refer the `makePayment` method inside `PaymentController` class.
* Refer the libraries package to understand the Paytm and Razorpay libraries.
* Refer the `MakePaymentRequestDto` and `MakePaymentResponseDto` for understanding the expected input and output to the functionality.
* Refer the `PaymentGatewayAdapter` class and see how it can be used in this scenario.
* Refer the models package to understand the models.
* Implement the `PaymentService` and `BillRepository` interfaces to achieve the above requirements.