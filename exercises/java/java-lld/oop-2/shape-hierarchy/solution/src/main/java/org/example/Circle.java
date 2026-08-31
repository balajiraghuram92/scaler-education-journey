package org.example;

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
        return Math.PI * radius * radius;
    }

    @Override
    public double calculatePerimeter() {
        return 2 * Math.PI * radius;
    }
}
