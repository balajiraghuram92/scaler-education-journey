package contest;

import contest.utils.StorageUtils;

/**
 * TODO: Implement the FileStorage interface to simply store and get the raw file content.
 * Methods you can use: {@link contest.utils.StorageUtils#store(String, byte[])} and
 * {@link contest.utils.StorageUtils#read(String)}
 */
public class RawFileStorage implements FileStorage {
    @Override
    public void storeFile(String fileName, byte[] content) {

    }

    @Override
    public byte[] getFile(String fileName) {
        return null;
    }

}
