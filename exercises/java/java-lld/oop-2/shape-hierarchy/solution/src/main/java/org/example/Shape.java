package org.example;

public abstract class Shape {
    private final int positionX;
    private final int positionY;
    private final String fillColor;
    private final String borderColor;

    public Shape(int positionX, int positionY, String fillColor, String borderColor) {
        this.positionX = positionX;
        this.positionY = positionY;
        this.fillColor = fillColor;
        this.borderColor = borderColor;
    }

    public int getPositionX() {
        return positionX;
    }

    public int getPositionY() {
        return positionY;
    }

    public String getFillColor() {
        return fillColor;
    }

    public String getBorderColor() {
        return borderColor;
    }

    public abstract double calculateArea();

    public abstract double calculatePerimeter();
}
