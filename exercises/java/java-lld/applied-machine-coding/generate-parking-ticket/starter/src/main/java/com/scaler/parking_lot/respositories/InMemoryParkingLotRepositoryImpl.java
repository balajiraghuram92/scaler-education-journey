package com.scaler.parking_lot.respositories;

import com.scaler.parking_lot.models.ParkingLot;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryParkingLotRepositoryImpl implements ParkingLotRepository{

    private Map<Long, ParkingLot> parkingLotMap;
    private static int id = 1;

    public InMemoryParkingLotRepositoryImpl() {
        this.parkingLotMap = new HashMap<>();
    }

    public Optional<ParkingLot> getParkingLotByGateId(long gateId) {
        // TODO: Find parking lot containing the gate with gateId
        return Optional.empty();
    }

    public Optional<ParkingLot> getParkingLotById(long id) {
        // TODO: Look up parking lot by id
        return Optional.empty();
    }

    @Override
    public ParkingLot save(ParkingLot parkingLot) {
        // TODO: Save parking lot to memory with auto-increment id if id is 0
        return null;
    }
}
