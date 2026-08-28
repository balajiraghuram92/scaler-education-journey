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
