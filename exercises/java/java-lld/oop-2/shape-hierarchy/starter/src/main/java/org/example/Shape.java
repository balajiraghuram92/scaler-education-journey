package org.example;

// TODO: implement the shared shape state — private fields for positionX, positionY,
// fillColor and borderColor, set via the constructor, exposed through getters.
// calculateArea()/calculatePerimeter() stay abstract for each concrete shape to define.
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
        return 0;
    }

    public int getPositionY() {
        return 0;
    }

    public String getFillColor() {
        return null;
    }

    public String getBorderColor() {
        return null;
    }

    public abstract double calculateArea();

    public abstract double calculatePerimeter();
}
