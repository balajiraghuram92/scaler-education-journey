package com.assignment.repositories;

import com.assignment.models.Bill;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryBillRepositoryImpl implements BillRepository{

    private Map<Long, Bill> billMap;

    public InMemoryBillRepositoryImpl() {
        this.billMap = new HashMap<>();
    }

    @Override
    public Bill save(Bill bill) {
        if(bill.getId() == 0){
            bill.setId(billMap.size() + 1);
        }
        billMap.put(bill.getId(), bill);
        return bill;
    }

    @Override
    public Optional<Bill> findById(long billId) {
        return Optional.ofNullable(billMap.get(billId));
    }
}