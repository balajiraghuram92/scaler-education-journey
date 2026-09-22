package com.scaler.parking_lot.strategies.assignment;

import com.scaler.parking_lot.models.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class EqualDistributionAssignmentStrategy implements SpotAssignmentStrategy {

    @Override
    public Optional<ParkingSpot> assignSpot(ParkingLot parkingLot, VehicleType vehicleType) {
        // TODO: Calculate floor-wise available spots for vehicleType, pick floor with the highest available spots (or lowest floor number on tie), assign spot and mark OCCUPIED
        return Optional.empty();
    }
}
