package com.scaler.parking_lot.services;

import com.scaler.parking_lot.exceptions.InvalidParkingLotException;
import com.scaler.parking_lot.models.ParkingFloor;
import com.scaler.parking_lot.models.ParkingLot;
import com.scaler.parking_lot.models.VehicleType;
import com.scaler.parking_lot.respositories.ParkingLotRepository;
import com.scaler.parking_lot.utils.ParkingFloorUtils;

import java.util.*;

public class ParkingLotServiceImpl implements ParkingLotService{

    private final ParkingLotRepository parkingLotRepository;

    public ParkingLotServiceImpl(ParkingLotRepository parkingLotRepository) {
        this.parkingLotRepository = parkingLotRepository;
    }

    @Override
    public Map<ParkingFloor, Map<String, Integer>> getParkingLotCapacity(long parkingLotId, List<Long> parkingFloorIds, List<VehicleType> requiredVehicleTypes) throws InvalidParkingLotException {
        // TODO: 1. Look up parking lot by id from repository, throw InvalidParkingLotException if not found. 2. Filter floors by parkingFloorIds if provided. 3. Filter vehicle types by requiredVehicleTypes (default to all types if empty/null). 4. Calculate available spots per floor per vehicle type via ParkingFloorUtils. 5. Return nested capacity map.
        return null;
    }
}
