package com.assignment.question;

import java.util.Optional;

// TODO: implement the Singleton pattern with double-checked locking —
//  - a private static volatile instance field.
//  - a private constructor.
//  - getInstance(): if instance is null, synchronize on the class and check again
//    inside the lock before creating the single instance (this is what keeps it both
//    thread-safe and cheap on the common path where instance already exists).
//  - resetInstance(): sets instance back to null (used by tests to get a fresh instance).
//  - delegate getConfiguration/setConfiguration/removeConfiguration/clear to the
//    Properties object from getProperties(), converting values via convert(...) where a
//    target type is requested.
public class FileBasedConfigurationManagerImpl extends FileBasedConfigurationManager {

    private FileBasedConfigurationManagerImpl() {
        super();
    }

    public static FileBasedConfigurationManager getInstance() {
        return null;
    }

    public static void resetInstance() {

    }

    @Override
    public String getConfiguration(String key) {
        return null;
    }

    @Override
    public <T> T getConfiguration(String key, Class<T> type) {
        return null;
    }

    @Override
    public void setConfiguration(String key, String value) {

    }

    @Override
    public <T> void setConfiguration(String key, T value) {

    }

    @Override
    public void removeConfiguration(String key) {

    }

    @Override
    public void clear() {

    }

}
