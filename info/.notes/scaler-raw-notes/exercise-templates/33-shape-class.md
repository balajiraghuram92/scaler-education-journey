# Shape Class Hierarchy

Source folder: 1773391696_e8560bcba2357cf2/Shape_Class_-_I-solution

## Problem Statement

You are required to implement a Shape class hierarchy for a graphic design toolbox. There are three types of shapes: Rectangle, Circle, and Triangle. Each shape has common properties such as positionX, positionY, fillColor, and borderColor. You must create an abstract Shape superclass containing common properties and methods, and implement concrete subclasses for each shape type. All data members should be declared private, and you must implement getter methods for each attribute following naming conventions. Each shape must also implement abstract methods `calculateArea()` and `calculatePerimeter()` to compute the area and perimeter of the respective shapes.

## Graded Contract (from tests)

- **Shape abstract class**: Must have private fields for positionX, positionY, fillColor, borderColor; constructor initializing all; getter methods `getPositionX()`, `getPositionY()`, `getFillColor()`, `getBorderColor()`; abstract methods `calculateArea()` and `calculatePerimeter()` returning double
- **Rectangle class**: Extends Shape; constructor `(int positionX, int positionY, String fillColor, String borderColor, int width, int height)`; methods `getWidth()`, `getHeight()`, `calculateArea()`, `calculatePerimeter()`
- **Circle class**: Extends Shape; constructor `(int positionX, int positionY, String fillColor, String borderColor, int radius)`; methods `getRadius()`, `calculateArea()`, `calculatePerimeter()`
- **Triangle class**: Extends Shape; constructor `(int positionX, int positionY, String fillColor, String borderColor, int side1, int side2, int side3)`; methods `getSide1()`, `getSide2()`, `getSide3()`, `calculateArea()`, `calculatePerimeter()`

## Learner Template

```java
package org.example;

public abstract class Shape {
    // TODO: Declare private fields for positionX, positionY, fillColor, borderColor
    
    public Shape(int positionX, int positionY, String fillColor, String borderColor) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getPositionX() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getPositionY() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getFillColor() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getBorderColor() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public abstract double calculateArea();

    public abstract double calculatePerimeter();
}
```

```java
package org.example;

public class Rectangle extends Shape {
    // TODO: Declare private fields for width and height
    
    public Rectangle(int positionX, int positionY, String fillColor, String borderColor, int width, int height) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getWidth() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getHeight() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public double calculateArea() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public double calculatePerimeter() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class Circle extends Shape {
    // TODO: Declare private field for radius
    
    public Circle(int positionX, int positionY, String fillColor, String borderColor, int radius) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getRadius() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public double calculateArea() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public double calculatePerimeter() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class Triangle extends Shape {
    // TODO: Declare private fields for side1, side2, side3
    
    public Triangle(int positionX, int positionY, String fillColor, String borderColor, int side1, int side2, int side3) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getSide1() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getSide2() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getSide3() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public double calculateArea() {
        // TODO: implement (use Heron's formula for triangle)
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public double calculatePerimeter() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field declarations and their initialization in all classes
- Constructor bodies and super() calls
- Implementation of area and perimeter calculation formulas
- Getter method implementations
- Helper logic for mathematical calculations (e.g., Heron's formula)
- Main method if any

