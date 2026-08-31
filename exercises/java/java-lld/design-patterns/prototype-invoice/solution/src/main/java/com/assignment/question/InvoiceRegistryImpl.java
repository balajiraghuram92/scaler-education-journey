package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

public class InvoiceRegistryImpl implements InvoicePrototypeRegistry {
    private Map<InvoiceType, Invoice> invoices = new HashMap<>();
    @Override
    public void addPrototype(Invoice user) {
        invoices.put(user.getType(), user);
    }

    @Override
    public Invoice getPrototype(InvoiceType type) {
        return invoices.get(type);
    }

    @Override
    public Invoice clone(InvoiceType type) {
        return invoices.get(type).cloneObject();
    }
}
