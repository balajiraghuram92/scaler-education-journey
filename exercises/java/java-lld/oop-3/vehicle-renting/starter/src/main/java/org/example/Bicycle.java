package org.example;

// TODO: implement Rentable — rent() marks the bicycle rented (and prints a message) only
// if it isn't already rented, otherwise prints that it's already rented; returnItem()
// marks it not-rented (and prints a message) only if it is currently rented, otherwise
// prints that it isn't rented.
public class Bicycle implements Rentable {
    String bicycleModel;
    public boolean isRented;

    public Bicycle(String bicycleModel) {
        this.bicycleModel = bicycleModel;
        this.isRented = false;
    }

    @Override
    public void rent() {

    }

    @Override
    public void returnItem() {

    }
}
