package com.scaler.parking_lot.controllers;

import com.scaler.parking_lot.dtos.GetParkingLotCapacityRequestDto;
import com.scaler.parking_lot.dtos.GetParkingLotCapacityResponseDto;
import com.scaler.parking_lot.dtos.Response;
import com.scaler.parking_lot.dtos.ResponseStatus;
import com.scaler.parking_lot.exceptions.GetParkingLotRequestValidationException;
import com.scaler.parking_lot.models.ParkingFloor;
import com.scaler.parking_lot.models.VehicleType;
import com.scaler.parking_lot.services.ParkingLotService;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ParkingLotController {

    private final ParkingLotService parkingLotService;

    public ParkingLotController(ParkingLotService parkingLotService) {
        this.parkingLotService = parkingLotService;
    }

    public GetParkingLotCapacityResponseDto getParkingLotCapacity(GetParkingLotCapacityRequestDto getParkingLotCapacityRequestDto) {
        try{
            validateRequest(getParkingLotCapacityRequestDto);
            List<VehicleType> vehicleTypes = new ArrayList<>();
            if(getParkingLotCapacityRequestDto.getVehicleTypes() != null) {
                for (String vehicleType : getParkingLotCapacityRequestDto.getVehicleTypes()) {
                    vehicleTypes.add(VehicleType.valueOf(vehicleType));
                }
            }
            Map<ParkingFloor, Map<String, Integer>> parkingLotCapacity = parkingLotService.getParkingLotCapacity(getParkingLotCapacityRequestDto.getParkingLotId(), getParkingLotCapacityRequestDto.getParkingFloorIds(), vehicleTypes);
            GetParkingLotCapacityResponseDto getParkingLotCapacityResponseDto = new GetParkingLotCapacityResponseDto();
            getParkingLotCapacityResponseDto.setCapacityMap(parkingLotCapacity);
            getParkingLotCapacityResponseDto.setResponse(new Response(ResponseStatus.SUCCESS, "Parking Lot Capacity retrieved successfully"));
            return getParkingLotCapacityResponseDto;
        } catch (Exception e){
            GetParkingLotCapacityResponseDto getParkingLotCapacityResponseDto = new GetParkingLotCapacityResponseDto();
            getParkingLotCapacityResponseDto.setResponse(new Response(ResponseStatus.FAILURE, e.getMessage()));
            return getParkingLotCapacityResponseDto;
        }
    }

    private void validateRequest(GetParkingLotCapacityRequestDto getParkingLotCapacityRequestDto) throws GetParkingLotRequestValidationException{
        if(getParkingLotCapacityRequestDto.getParkingLotId() <= 0){
            throw new GetParkingLotRequestValidationException("Invalid Parking Lot Id");
        }
    }


}
