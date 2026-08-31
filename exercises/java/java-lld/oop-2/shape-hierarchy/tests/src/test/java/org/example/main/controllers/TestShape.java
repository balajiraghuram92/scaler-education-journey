package org.example.main.controllers;

import org.example.Circle;
import org.example.Rectangle;
import org.example.Triangle;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestShape {

    @Test
    public void testRectangle() {
        Rectangle rectangle = new Rectangle(10, 20, "blue", "red", 5, 8);
        assertEquals(10, rectangle.getPositionX());
        assertEquals(20, rectangle.getPositionY());
        assertEquals("blue", rectangle.getFillColor());
        assertEquals("red", rectangle.getBorderColor());
        assertEquals(5, rectangle.getWidth());
        assertEquals(8, rectangle.getHeight());
        assertEquals(40, rectangle.calculateArea(), 0);
        assertEquals(26, rectangle.calculatePerimeter(), 0);

        // Test with zero width and height
        Rectangle zeroAreaRectangle = new Rectangle(0, 0, "green", "yellow", 0, 0);
        assertEquals(0, zeroAreaRectangle.calculateArea(), 0);
        assertEquals(0, zeroAreaRectangle.calculatePerimeter(), 0);
    }

    @Test
    public void testCircle() {
        Circle circle = new Circle(30, 40, "green", "yellow", 10);
        assertEquals(30, circle.getPositionX());
        assertEquals(40, circle.getPositionY());
        assertEquals("green", circle.getFillColor());
        assertEquals("yellow", circle.getBorderColor());
        assertEquals(10, circle.getRadius());
        assertEquals(314.159, circle.calculateArea(), 0.001);
        assertEquals(62.832, circle.calculatePerimeter(), 0.001);

        // Test with zero radius
        Circle zeroAreaCircle = new Circle(0, 0, "red", "blue", 0);
        assertEquals(0, zeroAreaCircle.calculateArea(), 0);
        assertEquals(0, zeroAreaCircle.calculatePerimeter(), 0);
    }

    @Test
    public void testTriangle() {
        Triangle triangle = new Triangle(50, 60, "purple", "orange", 3, 4, 5);
        assertEquals(50, triangle.getPositionX());
        assertEquals(60, triangle.getPositionY());
        assertEquals("purple", triangle.getFillColor());
        assertEquals("orange", triangle.getBorderColor());
        assertEquals(3, triangle.getSide1());
        assertEquals(4, triangle.getSide2());
        assertEquals(5, triangle.getSide3());
        assertEquals(6, triangle.calculateArea(), 0);
        assertEquals(12, triangle.calculatePerimeter(), 0);

        // Test with zero side lengths
        Triangle zeroLengthTriangle = new Triangle(0, 0, "yellow", "purple", 0, 0, 0);
        assertEquals(0, zeroLengthTriangle.calculateArea(), 0);
        assertEquals(0, zeroLengthTriangle.calculatePerimeter(), 0);
    }
}
