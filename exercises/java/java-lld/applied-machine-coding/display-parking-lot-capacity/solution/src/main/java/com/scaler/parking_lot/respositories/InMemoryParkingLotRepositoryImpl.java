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
        return this.parkingLotMap.values().stream().filter(parkingLot -> parkingLot.getGates().stream().anyMatch(gate -> gate.getId() == gateId)).findFirst();
    }

    public Optional<ParkingLot> getParkingLotById(long id) {
        return Optional.ofNullable(this.parkingLotMap.get(id));
    }

    @Override
    public ParkingLot save(ParkingLot parkingLot) {
        if(parkingLot.getId() == 0) {
            parkingLot.setId(this.parkingLotMap.size() + 1);
        }
        this.parkingLotMap.put(parkingLot.getId(), parkingLot);
        return parkingLot;
    }
}
