package com.assignment.controllers;

import com.assignment.adapters.PaymentGatewayAdapter;
import com.assignment.dtos.MakePaymentRequestDto;
import com.assignment.dtos.MakePaymentResponseDto;
import com.assignment.libraries.paytm.PaytmApi;
import com.assignment.libraries.razorpay.RazorpayApi;
import com.assignment.models.Bill;
import com.assignment.repositories.BillRepository;
import com.assignment.services.PaymentService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class TestPaymentController {

    private PaymentController paymentControllerWithPaytmAdapter;
    private PaymentController paymentControllerWithRazorpayAdapter;
    private PaymentService paymentServiceWithPaytmAdapter;
    private PaymentService paymentServiceWithRazorpayAdapter;
    private BillRepository billRepository;
    private PaymentGatewayAdapter paytmAdapterImpl;
    private PaymentGatewayAdapter razorpayAdapterImpl;

    @BeforeEach
    public void setupTest() throws Exception {
        initializeComponents();
    }

    private void initializeComponents() throws Exception {
        initializeRepositories();
        initializeAdapters();
        initializePaymentService();
        initializePaymentController();
    }

    private <T> T createInstance(Class<T> interfaceClass, Reflections reflections) throws Exception {
        Set<Class<? extends T>> implementations = reflections.getSubTypesOf(interfaceClass);
        if (implementations.isEmpty()) {
            throw new Exception("No implementation for " + interfaceClass.getSimpleName() + " found");
        }

        Class<? extends T> implementationClass = implementations.iterator().next();
        return getT(implementationClass);
    }

    private static <T> T getT(Class<? extends T> implementationClass) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {
        Constructor<? extends T> constructor = implementationClass.getDeclaredConstructor();
        constructor.setAccessible(true);
        return constructor.newInstance();
    }

    private <T> T createInstanceWithArgs(Class<T> interfaceClass, Reflections reflections, List<Object> dependencies) throws Exception {
        Set<Class<? extends T>> implementations = reflections.getSubTypesOf(interfaceClass);
        if (implementations.isEmpty()) {
            throw new Exception("No implementation for " + interfaceClass.getSimpleName() + " found");
        }
        Class<? extends T> implementationClass = implementations.iterator().next();
        Constructor<?>[] constructors = implementationClass.getConstructors();
        Constructor<?> constructor = Arrays.stream(constructors)
                .filter(constructor1 -> constructor1.getParameterCount() == dependencies.size())
                .findFirst().orElseThrow(() -> new Exception("No constructor with " + dependencies.size() + " arguments found"));
        constructor.setAccessible(true);
        Object[] args = new Object[constructor.getParameterCount()];
        for (int i = 0; i < constructor.getParameterCount(); i++) {
            for (Object dependency : dependencies) {
                if (constructor.getParameterTypes()[i].isInstance(dependency)) {
                    args[i] = dependency;
                    break;
                }
            }
        }
        return (T) constructor.newInstance(args);
    }

    private void initializeRepositories() throws Exception {
        Reflections repositoryReflections = new Reflections(BillRepository.class.getPackageName(), new SubTypesScanner(false));
        this.billRepository = createInstance(BillRepository.class, repositoryReflections);
    }

    private void initializeAdapters() throws Exception {
        Reflections adapterReflections = new Reflections(PaymentGatewayAdapter.class.getPackageName(), new SubTypesScanner(false));
        Set<Class<? extends PaymentGatewayAdapter>> implementations = adapterReflections.getSubTypesOf(PaymentGatewayAdapter.class);
        if (implementations.isEmpty()) {
            throw new Exception("No implementation for " + PaymentGatewayAdapter.class.getSimpleName() + " found");
        }
        if(implementations.size() != 2){
            throw new Exception("There should be exactly 2 implementation for" + PaymentGatewayAdapter.class.getSimpleName() + " interface, 1 for Paytm and 1 for Razorpay");
        }
        Optional<Class<? extends PaymentGatewayAdapter>> paytmAdapterOptional = implementations.stream().filter(implementation -> Arrays.stream(implementation.getDeclaredFields()).anyMatch(field -> field.getType().equals(PaytmApi.class))).findFirst();
        if(!paytmAdapterOptional.isPresent()){
            throw new Exception("No adapter found for PaytmAPI");
        }
        Optional<Class<? extends PaymentGatewayAdapter>> razorpayAdapterOptional = implementations.stream().filter(implementation -> Arrays.stream(implementation.getDeclaredFields()).anyMatch(field -> field.getType().equals(RazorpayApi.class))).findFirst();
        if(!razorpayAdapterOptional.isPresent()){
            throw new Exception("No adapter found for RazorpayAPI");
        }
        Class<? extends PaymentGatewayAdapter> paytmAdapterClass = paytmAdapterOptional.get();
        this.paytmAdapterImpl = getT(paytmAdapterClass);
        Class<? extends PaymentGatewayAdapter> razorpayAdapterClass = razorpayAdapterOptional.get();
        this.razorpayAdapterImpl = getT(razorpayAdapterClass);
    }

    private void initializePaymentService() throws Exception {
        Reflections serviceReflections = new Reflections(PaymentService.class.getPackageName(), new SubTypesScanner(false));
        this.paymentServiceWithPaytmAdapter = createInstanceWithArgs(PaymentService.class, serviceReflections, Arrays.asList(this.billRepository, this.paytmAdapterImpl));
        this.paymentServiceWithRazorpayAdapter = createInstanceWithArgs(PaymentService.class, serviceReflections, Arrays.asList(this.billRepository, this.razorpayAdapterImpl));
    }


    private void initializePaymentController() {
        this.paymentControllerWithPaytmAdapter = new PaymentController(this.paymentServiceWithPaytmAdapter);
        this.paymentControllerWithRazorpayAdapter = new PaymentController(this.paymentServiceWithRazorpayAdapter);
    }

    @Test
    public void testMakePaymentWithPaytmAdapter_WithValidBillId() throws Exception {
        Bill bill = new Bill();
        bill.setTotalAmount(1000);
        bill.setGst(bill.getTotalAmount() * 0.05);
        bill.setServiceCharge(bill.getTotalAmount() * 0.1);
        bill = this.billRepository.save(bill);

        MakePaymentRequestDto makePaymentRequestDto = new MakePaymentRequestDto();
        makePaymentRequestDto.setBillId(bill.getId());
        MakePaymentResponseDto makePaymentResponseDto = this.paymentControllerWithPaytmAdapter.makePayment(makePaymentRequestDto);
        assertNotNull(makePaymentResponseDto, "MakePaymentResponseDto should not be null");
        assertNotNull(makePaymentResponseDto.getTxnId(), "TxnId should not be null");
        assertNotNull(makePaymentResponseDto.getPaymentStatus(), "PaymentStatus should not be null");
    }

    @Test
    public void testMakePaymentWithPaytmAdapter_WithInvalidBillId() throws Exception {
        Bill bill = new Bill();
        bill.setTotalAmount(1000);
        bill.setGst(bill.getTotalAmount() * 0.05);
        bill.setServiceCharge(bill.getTotalAmount() * 0.1);
        bill = this.billRepository.save(bill);

        MakePaymentRequestDto makePaymentRequestDto = new MakePaymentRequestDto();
        makePaymentRequestDto.setBillId(bill.getId() + 1);
        MakePaymentResponseDto makePaymentResponseDto = this.paymentControllerWithPaytmAdapter.makePayment(makePaymentRequestDto);
        assertNotNull(makePaymentResponseDto, "MakePaymentResponseDto should not be null");
        assertNull(makePaymentResponseDto.getTxnId(), "TxnId should be null");
        assertNull(makePaymentResponseDto.getPaymentStatus(), "PaymentStatus should be null");
    }

    @Test
    public void testMakePaymentWithRazorpayAdapter_WithValidBillId() throws Exception {
        Bill bill = new Bill();
        bill.setTotalAmount(1000);
        bill.setGst(bill.getTotalAmount() * 0.05);
        bill.setServiceCharge(bill.getTotalAmount() * 0.1);
        bill = this.billRepository.save(bill);

        MakePaymentRequestDto makePaymentRequestDto = new MakePaymentRequestDto();
        makePaymentRequestDto.setBillId(bill.getId());
        MakePaymentResponseDto makePaymentResponseDto = this.paymentControllerWithRazorpayAdapter.makePayment(makePaymentRequestDto);
        assertNotNull(makePaymentResponseDto, "MakePaymentResponseDto should not be null");
        assertNotNull(makePaymentResponseDto.getTxnId(), "TxnId should not be null");
        assertNotNull(makePaymentResponseDto.getPaymentStatus(), "PaymentStatus should not be null");
    }

    @Test
    public void testMakePaymentWithRazorpayAdapter_WithInvalidBillId() throws Exception {
        Bill bill = new Bill();
        bill.setTotalAmount(1000);
        bill.setGst(bill.getTotalAmount() * 0.05);
        bill.setServiceCharge(bill.getTotalAmount() * 0.1);
        bill = this.billRepository.save(bill);

        MakePaymentRequestDto makePaymentRequestDto = new MakePaymentRequestDto();
        makePaymentRequestDto.setBillId(bill.getId() + 1);
        MakePaymentResponseDto makePaymentResponseDto = this.paymentControllerWithRazorpayAdapter.makePayment(makePaymentRequestDto);
        assertNotNull(makePaymentResponseDto, "MakePaymentResponseDto should not be null");
        assertNull(makePaymentResponseDto.getTxnId(), "TxnId should be null");
        assertNull(makePaymentResponseDto.getPaymentStatus(), "PaymentStatus should be null");
    }
}