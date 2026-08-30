# Adapter Pattern for Insurance Providers Integration

Source folder: `1773391216_3da13e0d30eeb5d6/Adaptor_Insuranc-solution`

## Problem Statement

Your company needs to integrate with various insurance providers, each having different APIs and data formats. To simplify the integration and ensure a consistent data format, you decide to implement the Adapter pattern. This pattern will allow you to create adapter classes for different insurance providers, converting their APIs into a common format that your application can use.

## Detailed Requirements

1. **Review the existing APIs**: Study the APIs and data formats of the insurance providers you need to integrate with. Understand the differences in their APIs and how they interact with their respective systems.

2. **Implement the adapter interface**: You have been provided with a `TravelInsuranceAdapter` interface. Your task is to implement this interface in different adapter classes, each corresponding to a different insurance provider. The adapters should adapt the provider-specific APIs into a format that matches the `TravelInsuranceAdapter` interface.

3. **Use composition**: Create adapter classes that internally use instances of the actual insurance provider APIs. You should not modify the provider APIs directly. Instead, create methods in the adapter classes that map to the provider APIs and perform the necessary transformations.

4. **Test your implementation**: Run the provided test cases in the `TravelInsuranceAdapterTest` class to ensure that your adapter classes work correctly. These test cases will check if your adapters have the required methods and if they interact with the provider APIs properly.

## Graded Contract (from tests)

The tests verify the following:

- **TravelInsuranceAdapter interface** must have at least 2 methods
- **add(String reference, Double amount) -> void** method exists (2 params: String and Double/double, returns void)
- **get(String reference) -> ClaimStatus** method exists (1 param of type String, returns non-void type ClaimStatus)
- **At least 2 implementations** of TravelInsuranceAdapter exist (e.g., AutoProtectAdapter, TravelGuardAdapter)
- Each adapter implementation must have a field reference to an external insurance API (AutoProtectApi or TravelGuardApi)
- The `add` method in each adapter must call the corresponding external API's claim-adding method
- The `get` method in each adapter must call the corresponding external API's status-checking method

## Learner Template

```java
package com.assignment.question;

public interface TravelInsuranceAdapter {
    void add(String reference, Double amount);
    
    ClaimStatus get(String reference);
}
```

```java
package com.assignment.question;

import com.assignment.question.external.AutoProtectApi;

public class AutoProtectAdapter implements TravelInsuranceAdapter {
    private AutoProtectApi autoProtectApi;
    
    @Override
    public void add(String reference, Double amount) {
        // TODO: implement
    }
    
    @Override
    public ClaimStatus get(String reference) {
        // TODO: implement
    }
}
```

```java
package com.assignment.question;

import com.assignment.question.external.TravelGuardApi;

public class TravelGuardAdapter implements TravelInsuranceAdapter {
    private TravelGuardApi travelGuardApi;
    
    @Override
    public void add(String reference, Double amount) {
        // TODO: implement
    }
    
    @Override
    public ClaimStatus get(String reference) {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- The implementation logic of the `add()` method in each adapter
- The implementation logic of the `get()` method in each adapter
- The initialization/construction of the external API instances in each adapter
- The mapping logic between the generic interface and provider-specific API calls
- Any transformation of data between the interface and the external APIs
