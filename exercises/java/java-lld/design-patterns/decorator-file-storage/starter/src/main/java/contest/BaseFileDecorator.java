package contest;

/**
 * TODO - Implement the FileStorage interface, storing a protected reference to the next
 * layer of type FileStorage (via a constructor), and delegate storeFile/getFile to it by
 * default. Subclasses override these methods to add their own behavior around that
 * delegation.
 */
public abstract class BaseFileDecorator implements FileStorage {

}
