# Lesson 3 — Exercise Directory Setup Prompt

**Purpose:** Create the in-browser coding exercise for Lesson 3 (OOP-2: Encapsulation & Copy Semantics).  
This exercise mirrors the structure of `exercises/java/java-lld/oop-2/rider-entity/` exactly.  
It is the **Point & Rectangle deep copy** exercise — the primary Scaler exercise for this lesson.

---

## CONTEXT

The exercise system works as follows:
- The API loads exercises from directories under `exercises/java/java-lld/`
- Each exercise has: `exercise.json`, `pom.xml`, `starter/`, `tests/`, `solution/`
- `starter/` = stub files the student edits in the browser
- `tests/` = trusted JUnit 5 test class (hidden from student, runs server-side)
- `solution/` = reference solution shown via "View Solution"
- `exercise.json` declares which files are editable, which test class to run, and the evidence mapping

---

## YOUR TASK

Create all 7 files listed below under `exercises/java/java-lld/oop-2/point-rectangle/`.  
Then update one line in `app/src/data/lessonExerciseAssociations.js`.

Do **not** modify any other file.

---

## FILE 1 — `exercises/java/java-lld/oop-2/point-rectangle/exercise.json`

```json
{
  "id": "java-lld-oop2-point-rectangle",
  "lessonSlug": "03-oop-2-access-modifiers-encapsulation",
  "title": "Point & Rectangle Deep Copy",
  "language": "java",
  "difficulty": "intermediate",
  "estimatedMinutes": 30,
  "runtime": {
    "profile": "java-maven",
    "javaVersion": 11,
    "timeoutSeconds": 10
  },
  "files": [
    {
      "id": "point",
      "path": "src/main/java/Point.java",
      "displayName": "Point.java",
      "editable": true
    },
    {
      "id": "rectangle",
      "path": "src/main/java/Rectangle.java",
      "displayName": "Rectangle.java",
      "editable": true
    }
  ],
  "testSuite": {
    "visible": false,
    "path": "tests/src/test/java/PointRectangleTest.java",
    "className": "PointRectangleTest"
  },
  "evidence": [
    {
      "id": "point-x-field",
      "label": "Point has an int field named x",
      "testMethod": "testXDataMemberExists"
    },
    {
      "id": "point-y-field",
      "label": "Point has an int field named y",
      "testMethod": "testYDataMemberExists"
    },
    {
      "id": "point-two-param-sig",
      "label": "Point(int x, int y) constructor exists with correct signature",
      "testMethod": "testTwoParamConstructorSignature"
    },
    {
      "id": "point-two-param-values",
      "label": "Point(int, int) correctly assigns x and y",
      "testMethod": "testTwoParamConstructor"
    },
    {
      "id": "point-copy-sig",
      "label": "Point(Point p) copy constructor exists",
      "testMethod": "testCopyConstructorSignature"
    },
    {
      "id": "point-copy-independence",
      "label": "Copy constructor creates a distinct object with identical coordinates",
      "testMethod": "testCopyConstructor"
    },
    {
      "id": "rect-topleft-field",
      "label": "Rectangle has a Point field named topLeft",
      "testMethod": "testTopLeftFieldExists"
    },
    {
      "id": "rect-bottomright-field",
      "label": "Rectangle has a Point field named bottomRight",
      "testMethod": "testBottomRightFieldExists"
    },
    {
      "id": "rect-four-param-exists",
      "label": "Rectangle(int, int, int, int) constructor exists and is public",
      "testMethod": "testFourParamConstructorExists"
    },
    {
      "id": "rect-two-point-exists",
      "label": "Rectangle(Point, Point) constructor exists and is public",
      "testMethod": "testTwoPointParamConstructorExists"
    },
    {
      "id": "rect-copy-exists",
      "label": "Rectangle(Rectangle) copy constructor exists and is public",
      "testMethod": "testRectangleCopyConstructorExists"
    },
    {
      "id": "rect-two-point-deep-copy",
      "label": "Rectangle(Point, Point) stores deep copies — not the same references",
      "testMethod": "testRectangleDeepCopyWith2Points"
    },
    {
      "id": "rect-copy-deep-copy",
      "label": "Rectangle(Rectangle) copy constructor deep copies topLeft",
      "testMethod": "testRectangleCopyConstructorDeepCopy"
    },
    {
      "id": "rect-four-param-values",
      "label": "Rectangle(int, int, int, int) correctly initialises all four coordinates",
      "testMethod": "testFourParamConstructorValues"
    }
  ]
}
```

---

## FILE 2 — `exercises/java/java-lld/oop-2/point-rectangle/pom.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.scaler.oops</groupId>
    <artifactId>point-rectangle</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.7.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M7</version>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## FILE 3 — `exercises/java/java-lld/oop-2/point-rectangle/starter/src/main/java/Point.java`

```java
public class Point {
    // write the code of point class here
}
```

---

## FILE 4 — `exercises/java/java-lld/oop-2/point-rectangle/starter/src/main/java/Rectangle.java`

```java
public class Rectangle {
    // write the code of Rectangle class here
}
```

---

## FILE 5 — `exercises/java/java-lld/oop-2/point-rectangle/tests/src/test/java/PointRectangleTest.java`

This is a merged test class combining PointTest and RectangleTest from the Scaler source ZIPs.

```java
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;

import static org.junit.jupiter.api.Assertions.*;

public class PointRectangleTest {

    private static Class<?> pointClass;
    private static Class<?> rectangleClass;

    @BeforeEach
    public void setUp() throws Exception {
        try {
            pointClass = Class.forName("Point");
            rectangleClass = Class.forName("Rectangle");
        } catch (Exception e) {
            fail("Class Point or Rectangle not found");
        }
    }

    // ── Point tests ──────────────────────────────────────────────────────────

    @Test
    public void testXDataMemberExists() throws Exception {
        Field xField = pointClass.getDeclaredField("x");
        assertEquals(int.class, xField.getType(), "Data member x is not of type int");
    }

    @Test
    public void testYDataMemberExists() throws Exception {
        Field yField = pointClass.getDeclaredField("y");
        assertEquals(int.class, yField.getType(), "Data member y is not of type int");
    }

    @Test
    public void testTwoParamConstructorSignature() throws Exception {
        Constructor<?> cons = Point.class.getConstructor(int.class, int.class);
        Class<?>[] paramTypes = cons.getParameterTypes();
        assertEquals(2, paramTypes.length);
        assertEquals(int.class, paramTypes[0]);
        assertEquals(int.class, paramTypes[1]);
    }

    @Test
    public void testTwoParamConstructor() throws Exception {
        Constructor<?> cons = Point.class.getConstructor(int.class, int.class);
        Point p = (Point) cons.newInstance(3, 4);
        Field xField = Point.class.getDeclaredField("x");
        xField.setAccessible(true);
        Field yField = Point.class.getDeclaredField("y");
        yField.setAccessible(true);
        assertEquals(3, (int) xField.get(p));
        assertEquals(4, (int) yField.get(p));
    }

    @Test
    public void testCopyConstructorSignature() throws Exception {
        Constructor<?> cons = Point.class.getConstructor(Point.class);
        Class<?>[] paramTypes = cons.getParameterTypes();
        assertEquals(1, paramTypes.length);
        assertEquals(Point.class, paramTypes[0]);
    }

    @Test
    public void testCopyConstructor() throws Exception {
        Constructor<Point> twoParam = Point.class.getDeclaredConstructor(int.class, int.class);
        Point p1 = twoParam.newInstance(3, 4);
        Constructor<Point> copyParam = Point.class.getDeclaredConstructor(Point.class);
        Point p2 = copyParam.newInstance(p1);
        assertNotSame(p1, p2);
        Field xField = Point.class.getDeclaredField("x");
        xField.setAccessible(true);
        Field yField = Point.class.getDeclaredField("y");
        yField.setAccessible(true);
        assertEquals((int) xField.get(p1), (int) xField.get(p2));
        assertEquals((int) yField.get(p1), (int) yField.get(p2));
    }

    // ── Rectangle tests ──────────────────────────────────────────────────────

    @Test
    public void testTopLeftFieldExists() throws Exception {
        Field field = Rectangle.class.getDeclaredField("topLeft");
        assertEquals("Point", field.getType().getSimpleName());
    }

    @Test
    public void testBottomRightFieldExists() throws Exception {
        Field field = Rectangle.class.getDeclaredField("bottomRight");
        assertEquals("Point", field.getType().getSimpleName());
    }

    @Test
    public void testFourParamConstructorExists() throws Exception {
        Constructor<?> constructor = Rectangle.class.getDeclaredConstructor(
                int.class, int.class, int.class, int.class);
        assertTrue(Modifier.isPublic(constructor.getModifiers()));
    }

    @Test
    public void testTwoPointParamConstructorExists() throws Exception {
        Constructor<?> constructor = Rectangle.class.getDeclaredConstructor(Point.class, Point.class);
        assertTrue(Modifier.isPublic(constructor.getModifiers()));
    }

    @Test
    public void testRectangleCopyConstructorExists() throws Exception {
        Constructor<?> constructor = Rectangle.class.getDeclaredConstructor(Rectangle.class);
        assertTrue(Modifier.isPublic(constructor.getModifiers()));
    }

    @Test
    public void testRectangleDeepCopyWith2Points() throws Exception {
        Constructor<Rectangle> constructor = Rectangle.class.getDeclaredConstructor(Point.class, Point.class);
        Constructor<?> pointConstructor = Point.class.getConstructor(int.class, int.class);
        Point topLeft = (Point) pointConstructor.newInstance(1, 2);
        Point bottomRight = (Point) pointConstructor.newInstance(3, 4);
        Rectangle r1 = constructor.newInstance(topLeft, bottomRight);
        Field fieldTopLeft = Rectangle.class.getDeclaredField("topLeft");
        fieldTopLeft.setAccessible(true);
        Field fieldBottomRight = Rectangle.class.getDeclaredField("bottomRight");
        fieldBottomRight.setAccessible(true);
        assertFalse(topLeft == fieldTopLeft.get(r1), "topLeft must be a deep copy, not the same reference");
        assertFalse(bottomRight == fieldBottomRight.get(r1), "bottomRight must be a deep copy, not the same reference");
    }

    @Test
    public void testRectangleCopyConstructorDeepCopy() throws Exception {
        Constructor<Rectangle> twoParam = Rectangle.class.getDeclaredConstructor(Point.class, Point.class);
        Constructor<Rectangle> copyParam = Rectangle.class.getDeclaredConstructor(Rectangle.class);
        Constructor<?> pointConstructor = Point.class.getConstructor(int.class, int.class);
        Point topLeft = (Point) pointConstructor.newInstance(1, 2);
        Point bottomRight = (Point) pointConstructor.newInstance(3, 4);
        Rectangle r1 = twoParam.newInstance(topLeft, bottomRight);
        Rectangle r2 = copyParam.newInstance(r1);
        Field fieldTopLeft = Rectangle.class.getDeclaredField("topLeft");
        fieldTopLeft.setAccessible(true);
        assertFalse(fieldTopLeft.get(r1) == fieldTopLeft.get(r2),
                "Copy constructor must deep copy topLeft — not share the same reference");
    }

    @Test
    public void testFourParamConstructorValues() throws Exception {
        Constructor<Rectangle> constructor = Rectangle.class.getDeclaredConstructor(
                int.class, int.class, int.class, int.class);
        Rectangle r1 = constructor.newInstance(2, 3, 4, 5);
        Field fieldTopLeft = Rectangle.class.getDeclaredField("topLeft");
        fieldTopLeft.setAccessible(true);
        Field fieldBottomRight = Rectangle.class.getDeclaredField("bottomRight");
        fieldBottomRight.setAccessible(true);
        Object tl = fieldTopLeft.get(r1);
        Object br = fieldBottomRight.get(r1);
        Field fieldX = Point.class.getDeclaredField("x");
        fieldX.setAccessible(true);
        Field fieldY = Point.class.getDeclaredField("y");
        fieldY.setAccessible(true);
        assertEquals(2, fieldX.getInt(tl));
        assertEquals(3, fieldY.getInt(tl));
        assertEquals(4, fieldX.getInt(br));
        assertEquals(5, fieldY.getInt(br));
    }
}
```

---

## FILE 6 — `exercises/java/java-lld/oop-2/point-rectangle/solution/src/main/java/Point.java`

```java
public class Point {
    int x;
    int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public Point(Point p) {
        this.x = p.x;
        this.y = p.y;
    }
}
```

---

## FILE 7 — `exercises/java/java-lld/oop-2/point-rectangle/solution/src/main/java/Rectangle.java`

```java
public class Rectangle {
    Point topLeft;
    Point bottomRight;

    public Rectangle(int tlX, int tlY, int brX, int brY) {
        this.topLeft = new Point(tlX, tlY);
        this.bottomRight = new Point(brX, brY);
    }

    public Rectangle(Point topLeft, Point bottomRight) {
        this.topLeft = new Point(topLeft);
        this.bottomRight = new Point(bottomRight);
    }

    public Rectangle(Rectangle r) {
        this.topLeft = new Point(r.topLeft);
        this.bottomRight = new Point(r.bottomRight);
    }
}
```

---

## FILE 8 — Update `app/src/data/lessonExerciseAssociations.js`

Find the line:

```js
'java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation': null,
```

Replace it with:

```js
'java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation': {
  exerciseId: 'java-lld-oop2-point-rectangle'
},
```

Do not change any other entry in this file.

---

## CONSTRAINTS

- Match the exact directory path: `exercises/java/java-lld/oop-2/point-rectangle/`
- The test class name must be `PointRectangleTest` (single class, not two separate files)
- Do not add a `package` declaration to any file under `point-rectangle/` — all classes use the default package
- Do not alter rider-entity or any other existing exercise directory
- Do not change `exercise.json` indentation style — use 2-space indent, double quotes (same as rider-entity)

---

## EXPECTED OUTPUT

After applying these changes, running the API container should log:

```
Loaded exercise manifest java-lld-oop2-point-rectangle from /app/exercises/java/java-lld/oop-2/point-rectangle/exercise.json.
```

And the lesson 3 page at `/chapter/java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation` should render the in-browser code editor with two editable tabs: `Point.java` and `Rectangle.java`.

---

## POST-SETUP CHECKLIST

1. Verify directory exists: `exercises/java/java-lld/oop-2/point-rectangle/`
2. Verify `exercise.json` has `"id": "java-lld-oop2-point-rectangle"`
3. Verify `tests/src/test/java/PointRectangleTest.java` exists (single merged class)
4. Verify `starter/src/main/java/Point.java` has only the stub comment
5. Verify `starter/src/main/java/Rectangle.java` has only the stub comment
6. Verify `solution/` has both `Point.java` and `Rectangle.java` with full implementations
7. Rebuild API: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build api`
8. Check API logs for: `Loaded exercise manifest java-lld-oop2-point-rectangle`
9. Open lesson 3 page — confirm exercise panel renders with Point.java and Rectangle.java tabs
10. Click Run without changes — confirm 14 tests fail (stubs are empty)
11. Enter the solution manually — confirm all 14 evidence items turn green
