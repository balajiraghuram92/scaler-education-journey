package org.example.main.controllers;

import org.example.BigFactorial;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;

import static org.junit.jupiter.api.Assertions.*;

public class TestBigFactorial {

    @Test
    public void testComputeFactorial() throws InterruptedException {
        BigFactorial calculator = new BigFactorial(10);
        calculator.start();
        calculator.join();

        // Verify the computed factorial value
        assertEquals(new BigInteger("3628800"), calculator.getFactorial());

        // Verify if a separate thread was created
        assertSame(calculator.getState(), Thread.State.TERMINATED);
    }

    @Test
    public void testFactorialOfZero() throws InterruptedException {
        BigFactorial calculator = new BigFactorial(0);
        calculator.start();
        calculator.join();
        assertEquals(BigInteger.ONE, calculator.getFactorial(), "Factorial of 0 should be 1");
    }

    @Test
    public void testFactorialOfLargeNumber() throws InterruptedException {
        BigFactorial calculator = new BigFactorial(1000);
        calculator.start();
        calculator.join();
        assertNotNull(calculator.getFactorial(), "Factorial of 1000 should compute without error");
    }

    @Test
    public void testThreadInterruption() throws InterruptedException {
        BigFactorial calculator = new BigFactorial(100);
        calculator.start();
        calculator.interrupt();
        calculator.join();
        assertTrue(calculator.isInterrupted(), "Thread should be interrupted gracefully");
    }

    @Test
    public void testMultipleInstances() throws InterruptedException {
        BigFactorial calculator1 = new BigFactorial(10);
        BigFactorial calculator2 = new BigFactorial(20);
        calculator1.start();
        calculator2.start();
        calculator1.join();
        calculator2.join();

        assertEquals(new BigInteger("3628800"), calculator1.getFactorial(), "Factorial of 10 should be correctly computed");
        assertEquals(new BigInteger("2432902008176640000"), calculator2.getFactorial(), "Factorial of 20 should be correctly computed");
    }
}
