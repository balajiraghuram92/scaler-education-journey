# Prototype Invoice

Source folder: `1773391199_b98ab42a222f47de/Prototype_Invoic-solution`

## Problem Statement

Implement the Prototype design pattern for efficient invoice object cloning. Create prototype invoice objects that can be efficiently cloned during testing, avoiding the overhead of fetching data from a database for each invoice generation.

## Graded Contract (from tests)

From `InvoiceTest.java`, the following must be present and function correctly:

- **Interface `ClonableObject<T>`** (generic interface)
  - Must be located in package `com.assignment.question`
  - Must define a method `T cloneObject()` that returns a cloned copy of the implementing object

- **Enum `InvoiceType`**
  - Must have at least: SALES, PURCHASE, SERVICE

- **Class `Invoice` implements `ClonableObject<Invoice>`**
  - Must implement the `ClonableObject<Invoice>` interface
  - Must have fields: Long invoiceId, String customerName, Double amount, String paymentMethod, InvoiceType type
  - Must have a public constructor accepting all these parameters in order
  - Must have public getters for all fields: getInvoiceId(), getCustomerName(), getAmount(), getPaymentMethod(), getType()
  - Must implement `Invoice cloneObject()` method
    - Must return a new Invoice object with the same field values
    - The returned object must NOT be the same object in memory (assertNotSame check)

- **Interface `InvoicePrototypeRegistry`**
  - Must define: `void addPrototype(Invoice user)`
  - Must define: `Invoice getPrototype(InvoiceType type)`
  - Must define: `Invoice clone(InvoiceType type)`

- **Class implementing `InvoicePrototypeRegistry`** (exactly one non-abstract implementation must exist)
  - Must have a public no-args constructor
  - `addPrototype()` must store invoice by its type
  - `getPrototype()` must return the stored invoice (same object reference)
  - `clone()` must call cloneObject() on the stored invoice and return the clone

## Learner Template

```java
package com.assignment.question;

public interface ClonableObject<T> {
    T cloneObject();
}
```

```java
package com.assignment.question;

public enum InvoiceType {
    SALES,
    PURCHASE,
    SERVICE
}
```

```java
package com.assignment.question;

public class Invoice implements ClonableObject<Invoice> {
    private Long invoiceId;
    private String customerName;
    private Double amount;
    private String paymentMethod;
    private InvoiceType type;
    
    public Invoice(Long invoiceId, String customerName, Double amount, String paymentMethod, InvoiceType type) {
        // TODO: implement
    }
    
    public Long getInvoiceId() {
        // TODO: implement
    }
    
    public String getCustomerName() {
        // TODO: implement
    }
    
    public Double getAmount() {
        // TODO: implement
    }
    
    public String getPaymentMethod() {
        // TODO: implement
    }
    
    public InvoiceType getType() {
        // TODO: implement
    }
    
    @Override
    public Invoice cloneObject() {
        // TODO: implement - create and return new Invoice with same field values
    }
}
```

```java
package com.assignment.question;

public interface InvoicePrototypeRegistry {
    void addPrototype(Invoice user);
    Invoice getPrototype(InvoiceType type);
    Invoice clone(InvoiceType type);
}
```

```java
package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

public class InvoiceRegistryImpl implements InvoicePrototypeRegistry {
    private Map<InvoiceType, Invoice> invoices = new HashMap<>();
    
    @Override
    public void addPrototype(Invoice user) {
        // TODO: implement
    }
    
    @Override
    public Invoice getPrototype(InvoiceType type) {
        // TODO: implement
    }
    
    @Override
    public Invoice clone(InvoiceType type) {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Field assignment in constructor
- Getter implementation logic
- HashMap storage and retrieval logic
- Cloning logic (copying all field values to new object)
- Any validation or null-checking beyond the contract
- Setter methods or mutators (not in graded contract)
- toString(), equals(), or hashCode() methods
- Database interaction or persistence logic
