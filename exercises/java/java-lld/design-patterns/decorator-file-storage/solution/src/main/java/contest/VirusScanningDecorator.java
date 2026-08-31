package contest;

import contest.utils.StorageUtils;

public class VirusScanningDecorator extends BaseFileDecorator {

    private FileStorage fileStorage;
    public VirusScanningDecorator(FileStorage fileStorage) {
        super(fileStorage);
        this.fileStorage = fileStorage;
    }

    @Override
    public void storeFile(String fileName, byte[] content) {
        boolean hasVirus = StorageUtils.scanForVirus(content);
        if (hasVirus) {
            throw new RuntimeException("Virus detected in file: " + fileName);
        }

        fileStorage.storeFile(fileName, content);
    }

    @Override
    public byte[] getFile(String fileName) {
        byte[] content = fileStorage.getFile(fileName);
        boolean hasVirus = StorageUtils.scanForVirus(content);
        if (hasVirus) {
            throw new RuntimeException("Virus detected in file: " + fileName);
        }

        return content;
    }
}
