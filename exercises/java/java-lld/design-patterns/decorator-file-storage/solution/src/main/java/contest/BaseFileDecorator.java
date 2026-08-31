package contest;

public abstract class BaseFileDecorator implements FileStorage {

    protected FileStorage next;

    public BaseFileDecorator(FileStorage next) {
        this.next = next;
    }

    @Override
    public void storeFile(String fileName, byte[] content) {
        next.storeFile(fileName, content);
    }

    @Override
    public byte[] getFile(String fileName) {
        return next.getFile(fileName);
    }
}
