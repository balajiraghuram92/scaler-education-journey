package contest;

import static contest.utils.StorageUtils.compress;
import static contest.utils.StorageUtils.decompress;

public class CompressionDecorator extends BaseFileDecorator {

    private FileStorage fileStorage;
    public CompressionDecorator(FileStorage fileStorage) {
        super(fileStorage);
        this.fileStorage = fileStorage;
    }

    @Override
    public void storeFile(String fileName, byte[] content) {
        byte[] compressedContent = compress(content);
        fileStorage.storeFile(fileName, compressedContent);
    }

    @Override
    public byte[] getFile(String fileName) {
        byte[] compressedContent = fileStorage.getFile(fileName);
        return decompress(compressedContent);
    }
}
