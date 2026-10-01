package com.example.bmsbookticket.exceptions;

import java.util.List;

public class SeatsUnavailableException extends Exception {
    private final List<Integer> unavailableShowSeatIds;

    public SeatsUnavailableException(List<Integer> unavailableShowSeatIds) {
        super("Seats are not available: " + unavailableShowSeatIds);
        this.unavailableShowSeatIds = List.copyOf(unavailableShowSeatIds);
    }

    public List<Integer> getUnavailableShowSeatIds() {
        return unavailableShowSeatIds;
    }
}
