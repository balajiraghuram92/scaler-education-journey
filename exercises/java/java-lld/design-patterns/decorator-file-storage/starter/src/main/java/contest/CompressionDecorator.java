package contest;

import static contest.utils.StorageUtils.compress;
import static contest.utils.StorageUtils.decompress;

/**
 * TODO - Extend {@link BaseFileDecorator} to compress content before storing and decompress
 * it after reading.
 * 1. Implement storeFile: compress the content, then delegate to the next layer.
 * 2. Implement getFile: read from the next layer, then decompress before returning.
 * 3. Add a constructor taking the next layer of type {@link FileStorage} and calling super.
 */
public class CompressionDecorator extends BaseFileDecorator {

}
