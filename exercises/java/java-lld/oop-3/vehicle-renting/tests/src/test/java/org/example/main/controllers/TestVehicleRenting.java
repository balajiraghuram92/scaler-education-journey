package org.example.main.controllers;

import org.example.Bicycle;
import org.example.Car;
import org.example.Rentable;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestVehicleRenting {

    @Test
    public void testRentCar() {
        Rentable car = new Car("Toyota Camry");
        car.rent();
        assertTrue(((Car) car).isRented);
    }

    @Test
    public void testReturnCar() {
        Rentable car = new Car("Toyota Camry");
        car.rent();
        car.returnItem();
        assertFalse(((Car) car).isRented);
    }

    @Test
    public void testRentBicycle() {
        Rentable bicycle = new Bicycle("Mountain Bike");
        bicycle.rent();
        assertTrue(((Bicycle) bicycle).isRented);
    }

    @Test
    public void testReturnBicycle() {
        Rentable bicycle = new Bicycle("Mountain Bike");
        bicycle.rent();
        bicycle.returnItem();
        assertFalse(((Bicycle) bicycle).isRented);
    }

    @Test
    public void testAttemptToRentAlreadyRentedCar() {
        Rentable car = new Car("Toyota Camry");
        car.rent(); // First rent attempt
        assertTrue(((Car) car).isRented);
        car.rent(); // Second rent attempt
        // Assert isRented remains true, ensuring no change in state or unexpected behavior
        assertTrue(((Car) car).isRented, "Car should still be rented after second rent attempt");
    }

    @Test
    public void testAttemptToReturnNonRentedCar() {
        Rentable car = new Car("Toyota Camry");
        // Attempt to return before renting
        car.returnItem();
        assertFalse(((Car) car).isRented, "Car should not be marked as rented when returned without being rented");
    }

    @Test
    public void testMultipleConsecutiveOperationsOnCar() {
        Rentable car = new Car("Toyota Camry");
        car.rent();
        assertTrue(((Car) car).isRented);
        car.returnItem();
        assertFalse(((Car) car).isRented);
        car.rent(); // Rent again after returning
        assertTrue(((Car) car).isRented, "Car should be rentable again after being returned");
    }

    @Test
    public void testRentAndReturnDifferentInstances() {
        Rentable car1 = new Car("Toyota Camry");
        Rentable car2 = new Car("Toyota Camry");
        car1.rent();
        assertTrue(((Car) car1).isRented);
        assertFalse(((Car) car2).isRented, "Second instance of the same car model should not be affected by the rental status of the first instance");
        car2.rent();
        assertTrue(((Car) car2).isRented, "Second car instance should be rentable independently of the first");
    }
}
