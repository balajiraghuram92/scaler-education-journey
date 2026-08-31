package com.example.bookrooms.repositories;

import com.example.bookrooms.models.CustomerSession;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// TODO: implement CustomerSessionRepository as an in-memory store keyed by session id —
// save(...) assigns an id when absent (id == 0) and stores it;
// findActiveCustomerSessionByUserId(...) returns the first stored session whose user id
// matches and whose isActive() is true, or empty if none matches.
public class InMemoryCustomerSessionRepository implements CustomerSessionRepository {
    private Map<Long, CustomerSession> customerSessionMap;
    private static long idCounter = 0;

    public InMemoryCustomerSessionRepository() {
        customerSessionMap = new HashMap<>();
    }

    @Override
    public CustomerSession save(CustomerSession customerSession) {
        return null;
    }

    @Override
    public Optional<CustomerSession> findActiveCustomerSessionByUserId(long userId) {
        return null;
    }
}
