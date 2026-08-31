// TODO: implement a thread-safe counter — a private int field set via the constructor,
// with incValue/decValue/getValue all declared synchronized so concurrent callers can't
// interleave reads/writes of count.
public class Counter {
    private int count;
    public Counter(int count){

    }

    public synchronized void incValue(int offset){

    }

    public synchronized void decValue(int offset){

    }

    public synchronized int getValue(){
        return 0;
    }
}
