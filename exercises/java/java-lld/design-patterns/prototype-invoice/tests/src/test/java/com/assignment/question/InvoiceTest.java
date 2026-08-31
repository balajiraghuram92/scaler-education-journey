package com.assignment.question;

import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

public class InvoiceTest {

    private static InvoicePrototypeRegistry getRegistry() {
        // Use Reflections to find the class implementing InvoicePrototypeRegistry
        Reflections reflections = new Reflections(InvoiceTest.class.getPackageName(),
                new SubTypesScanner(false));
        Set<Class<? extends InvoicePrototypeRegistry>> classes = reflections.getSubTypesOf(InvoicePrototypeRegistry.class);

        // Ensure there is exactly one class implementing the interface
        assertEquals(1, classes.size(), "If the registry pattern is implemented correctly, there should be exactly one class implementing InvoicePrototypeRegistry");

        // Instantiate the registry implementation
        Class<? extends InvoicePrototypeRegistry> registryClass = classes.iterator().next();
        try {
            return registryClass.getDeclaredConstructor().newInstance();
        } catch (Exception e) {
            fail("If the registry pattern is implemented correctly, the registry class should have a public no-args constructor");
        }
        return null;
    }

    @Test
    public void testInvoiceImplementsClonableObject() {
        Class<?> invoiceClass = Invoice.class;
        Class<?>[] interfaces = invoiceClass.getInterfaces();

        boolean implementsClonableObject = false;

        for (Class<?> iface : interfaces) {
            if (iface == ClonableObject.class) {
                implementsClonableObject = true;
                break;
            }
        }

        assertTrue(implementsClonableObject, "If the prototype pattern is implemented correctly, the Invoice class should implement the ClonableObject interface");
    }

    @Test
    public void testInvoiceCloneMethodCreatesDistinctObject() {
        Invoice invoice = new Invoice(1L, "testinvoice", 100.0, "CARD", InvoiceType.SALES);

        // Using reflection to find and invoke the clone method
        try {
            Method cloneMethod = invoice.getClass().getMethod("cloneObject");
            assertNotNull(cloneMethod, "If the prototype pattern is implemented correctly, the Invoice class should have a cloneObject method");

            // Calling the clone method to create a copy
            Invoice clonedInvoice = (Invoice) cloneMethod.invoke(invoice);
            assertNotNull(clonedInvoice, "If the clone method is implemented correctly, it should return a non-null object");

            // Validating that the clonedInvoice is not the same object as invoice
            assertNotSame(invoice, clonedInvoice, "If the clone method is implemented correctly, it should return a new object");

            // Asserting that the cloned invoice has the same values as the original invoice
            assertEquals(invoice.getInvoiceId(), clonedInvoice.getInvoiceId(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
            assertEquals(invoice.getAmount(), clonedInvoice.getAmount(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
            assertEquals(invoice.getPaymentMethod(), clonedInvoice.getPaymentMethod(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
            assertEquals(invoice.getCustomerName(), clonedInvoice.getCustomerName(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
            assertEquals(invoice.getType(), clonedInvoice.getType(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
        } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
            fail("If the prototype pattern is implemented correctly, the Invoice class should have a cloneObject method");
        }
    }

    @Test
    public void testRegistry() {

        InvoicePrototypeRegistry registry = getRegistry();
        assertNotNull(registry, "If the registry pattern is implemented correctly, the registry should not be null");

        Invoice invoice = new Invoice(1L, "testinvoice", 100.0, "CARD", InvoiceType.SALES);
        registry.addPrototype(invoice);

        Invoice prototype = registry.getPrototype(invoice.getType());
        assertNotNull(prototype, "If the clone method is implemented correctly, it should return a non-null object");
        assertSame(invoice, prototype, "If the registry pattern is implemented correctly, the registry should return the same object that was added");
    }

    @Test
    public void testRegistryClone() {

        Invoice invoice = new Invoice(1L, "testinvoice", 100.0, "CARD", InvoiceType.SALES);
        InvoicePrototypeRegistry registry = getRegistry();
        assertNotNull(registry, "If the registry pattern is implemented correctly, the registry should not be null");

        registry.addPrototype(invoice);

        // Clone the prototype and validate it's a distinct object with the same values
        Invoice clonedInvoice = registry.clone(invoice.getType());
        assertNotNull(clonedInvoice, "If the clone method is implemented correctly, it should return a non-null object");
        assertNotSame(invoice, clonedInvoice, "If the clone method is implemented correctly, it should return a new object");

        assertEquals(invoice.getInvoiceId(), clonedInvoice.getInvoiceId(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
        assertEquals(invoice.getAmount(), clonedInvoice.getAmount(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
        assertEquals(invoice.getPaymentMethod(), clonedInvoice.getPaymentMethod(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
        assertEquals(invoice.getCustomerName(), clonedInvoice.getCustomerName(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
        assertEquals(invoice.getType(), clonedInvoice.getType(), "If the clone method is implemented correctly, it should return a new object with the same values as the original object");
    }
}
