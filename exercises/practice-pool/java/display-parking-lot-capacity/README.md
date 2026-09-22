## Display parking lot capacity

We want to create an API, which will display the capacity of the given parking lot.
The API should be flexible to give the overall capacity of the parking lot,
or the capacity of a specific parking floor or for specific vehicle type or combination of
all of these.

The request for this api will always get a parking lot id.
List of parking floor ids is optional, when given, the response should contain
the capacity of the given parking floors.
List of vehicle types is optional, when given, the response should contain details about
given vehicle types.

Refer GetParkingLotCapacityRequestDto for request details.

The response should contain Map<ParkingFloor, Map<String, Integer>>, outer map key is the parking floor,
inner map key is the vehicle type and value is the capacity of the given vehicle type in the given parking floor.
Refer GetParkingLotCapacityResponseDto for response details.