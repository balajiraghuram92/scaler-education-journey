package org.example;

// TODO: implement Circle — calculateArea() is pi * radius^2, calculatePerimeter()
// is 2 * pi * radius.
public class Circle extends Shape {
    private final int radius;

    public Circle(int positionX, int positionY, String fillColor, String borderColor, int radius) {
        super(positionX, positionY, fillColor, borderColor);
        this.radius = radius;
    }

    public int getRadius() {
        return radius;
    }

    @Override
    public double calculateArea() {
        return 0;
    }

    @Override
    public double calculatePerimeter() {
        return 0;
    }
}
