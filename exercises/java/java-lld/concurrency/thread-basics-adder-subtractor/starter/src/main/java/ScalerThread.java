import java.util.HashMap;

// TODO: override start() — call super.start() to actually launch the thread, then
// record which thread name ran this Runnable by putting (target, this.getName())
// into the static map.
public class ScalerThread extends Thread {
    public static HashMap<String, String> map = new HashMap<>();
    private String target;

    ScalerThread(Runnable r){
        super(r);
        target = r.getClass().getName();
    }

    @Override
    public void start() {

    }
}
