package org.example;

import java.math.BigInteger;

// TODO: extend Thread — run() should compute number! (using BigInteger, since the
// result can be arbitrarily large) and store it so getFactorial() can return it
// after the thread finishes.
public class BigFactorial extends Thread {
    private final int number;
    private BigInteger factorial;

    public BigFactorial(int number) {
        this.number = number;
    }

    @Override
    public void run() {

    }

    public BigInteger getFactorial() {
        return factorial;
    }
}
