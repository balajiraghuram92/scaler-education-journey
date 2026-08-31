package contest;

import contest.utils.StorageUtils;

public class RawFileStorage implements FileStorage {
    @Override
    public void storeFile(String fileName, byte[] content) {
        StorageUtils.store(fileName, content);
    }

    @Override
    public byte[] getFile(String fileName) {
        return StorageUtils.read(fileName);
    }

}
