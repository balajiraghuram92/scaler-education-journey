package com.scaler.parking_lot.respositories;

import com.scaler.parking_lot.models.Vehicle;
import com.scaler.parking_lot.models.VehicleType;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryVehicleRepositoryImpl implements VehicleRepository{

    private Map<Long, Vehicle> vehicleMap;
    private static long id = 0;

    public InMemoryVehicleRepositoryImpl() {
        this.vehicleMap = new HashMap<>();
    }

    public Optional<Vehicle> getVehicleByRegistrationNumber(String registrationNumber) {
        // TODO: Look up vehicle by registration number
        return Optional.empty();
    }

    @Override
    public Vehicle save(Vehicle vehicle) {
        // TODO: Save vehicle to memory with auto-increment id if id is 0
        return null;
    }
}
