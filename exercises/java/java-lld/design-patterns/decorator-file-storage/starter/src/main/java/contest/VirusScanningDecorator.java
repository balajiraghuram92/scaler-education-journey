package contest;

import contest.utils.StorageUtils;

/**
 * TODO - Extend {@link BaseFileDecorator} to scan content for viruses before storing and
 * after reading, throwing if a virus is found.
 * Use {@link contest.utils.StorageUtils#scanForVirus(byte[])}.
 * Also add a constructor taking the next layer of type {@link FileStorage} and calling super.
 */
public class VirusScanningDecorator extends BaseFileDecorator {

}
