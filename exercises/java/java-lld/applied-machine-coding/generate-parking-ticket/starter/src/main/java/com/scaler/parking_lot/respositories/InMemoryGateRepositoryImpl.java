package com.scaler.parking_lot.respositories;

import com.scaler.parking_lot.models.Gate;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryGateRepositoryImpl implements GateRepository {

    private Map<Long, Gate> gateMap;
    private static int id = 1;

    public InMemoryGateRepositoryImpl() {
        this.gateMap = new HashMap<>();
    }

    public Optional<Gate> findById(long gateId) {
        // TODO: Look up gate by id in memory
        return Optional.empty();
    }

    @Override
    public Gate save(Gate gate) {
        // TODO: Save gate to memory with auto-increment id if id is 0
        return null;
    }
}
