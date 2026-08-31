package org.example;

public class Bicycle implements Rentable {
    String bicycleModel;
    public boolean isRented;

    public Bicycle(String bicycleModel) {
        this.bicycleModel = bicycleModel;
        this.isRented = false;
    }

    @Override
    public void rent() {
        if (!isRented) {
            System.out.println("Renting bicycle: " + bicycleModel);
            isRented = true;
        } else {
            System.out.println("Bicycle " + bicycleModel + " is already rented");
        }
    }

    @Override
    public void returnItem() {
        if (isRented) {
            System.out.println("Returning bicycle: " + bicycleModel);
            isRented = false;
        } else {
            System.out.println("Bicycle " + bicycleModel + " is not rented");
        }
    }
}
