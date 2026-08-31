package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

// TODO: implement InvoicePrototypeRegistry — addPrototype(...) stores the given
// Invoice keyed by its type; getPrototype(...) returns the stored prototype as-is;
// clone(...) looks up the stored prototype and returns cloneObject() on it.
public class InvoiceRegistryImpl implements InvoicePrototypeRegistry {
    private Map<InvoiceType, Invoice> invoices = new HashMap<>();
    @Override
    public void addPrototype(Invoice user) {

    }

    @Override
    public Invoice getPrototype(InvoiceType type) {
        return null;
    }

    @Override
    public Invoice clone(InvoiceType type) {
        return null;
    }
}
