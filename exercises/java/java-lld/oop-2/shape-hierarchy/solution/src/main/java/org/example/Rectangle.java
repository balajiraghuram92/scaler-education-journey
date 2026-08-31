package org.example;

public class Rectangle extends Shape {
    private final int width;
    private final int height;

    public Rectangle(int positionX, int positionY, String fillColor, String borderColor, int width, int height) {
        super(positionX, positionY, fillColor, borderColor);
        this.width = width;
        this.height = height;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    @Override
    public double calculateArea() {
        return width * height;
    }

    @Override
    public double calculatePerimeter() {
        return 2 * (width + height);
    }
}
