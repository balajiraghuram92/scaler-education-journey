package contest;

public interface FileStorage {
    void storeFile(String fileName, byte[] content);

    byte[] getFile(String fileName);
}
