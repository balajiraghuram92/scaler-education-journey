package com.scaler.parking_lot.respositories;

import com.scaler.parking_lot.models.ParkingLot;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryParkingLotRepositoryImpl implements ParkingLotRepository{

    private Map<Long, ParkingLot> parkingLotMap;

    public InMemoryParkingLotRepositoryImpl(Map<Long, ParkingLot> parkingLotMap) {
        this.parkingLotMap = parkingLotMap;
    }

    public InMemoryParkingLotRepositoryImpl() {
        this.parkingLotMap = new HashMap<>();
    }

    public Optional<ParkingLot> getParkingLotByGateId(long gateId) {
        // TODO: Look up parking lot by gate id
        return Optional.empty();
    }

    public Optional<ParkingLot> getParkingLotById(long id) {
        // TODO: Look up parking lot by id
        return Optional.empty();
    }

    @Override
    public ParkingLot save(ParkingLot parkingLot) {
        // TODO: Save parking lot in map, assigning id if id is 0
        return null;
    }
}
