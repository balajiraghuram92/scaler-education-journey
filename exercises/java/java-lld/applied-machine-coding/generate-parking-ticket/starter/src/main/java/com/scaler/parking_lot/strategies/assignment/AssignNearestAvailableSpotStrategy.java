package com.scaler.parking_lot.strategies.assignment;

import com.scaler.parking_lot.models.*;

import java.util.Optional;

public class AssignNearestAvailableSpotStrategy implements SpotAssignmentStrategy{
    @Override
    public Optional<ParkingSpot> assignSpot(ParkingLot parkingLot, VehicleType vehicleType) {
        // TODO: Iterate over operational floors and spots, assign the first available spot matching vehicleType and mark OCCUPIED
        return Optional.empty();
    }
}
