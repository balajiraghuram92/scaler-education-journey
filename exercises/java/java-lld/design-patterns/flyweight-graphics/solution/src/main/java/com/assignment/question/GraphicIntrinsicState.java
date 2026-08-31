package com.assignment.question;

@IntrinsicState
public class GraphicIntrinsicState {
    private Image image;
    private int width;
    private int height;
    private String color;

    private GraphicType type;

    public Image getImage() {
        return image;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public String getColor() {
        return color;
    }

    public GraphicType getType() {
        return type;
    }
}
