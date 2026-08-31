package org.example;

import java.math.BigInteger;

public class BigFactorial extends Thread {
    private final int number;
    private BigInteger factorial;

    public BigFactorial(int number) {
        this.number = number;
    }

    @Override
    public void run() {
        factorial = calculateFactorial(number);
    }

    public BigInteger getFactorial() {
        return factorial;
    }

    private BigInteger calculateFactorial(int n) {
        BigInteger result = BigInteger.ONE;
        for (int i = 2; i <= n; i++) {
            result = result.multiply(BigInteger.valueOf(i));
        }
        return result;
    }
}
