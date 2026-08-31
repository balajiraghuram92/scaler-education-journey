package org.example;

// TODO: implement Rentable — rent() marks the car rented (and prints a message) only if
// it isn't already rented, otherwise prints that it's already rented; returnItem() marks
// it not-rented (and prints a message) only if it is currently rented, otherwise prints
// that it isn't rented.
public class Car implements Rentable {
    String carModel;
    public boolean isRented;

    public Car(String carModel) {
        this.carModel = carModel;
        this.isRented = false;
    }

    @Override
    public void rent() {

    }

    @Override
    public void returnItem() {

    }
}
