package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

// TODO: implement ConfigurationPrototypeRegistry — addPrototype(...) stores the given
// Configuration keyed by its type; getPrototype(...) returns the stored prototype as-is;
// clone(...) looks up the stored prototype and returns cloneObject() on it.
public class ConfigurationPrototypeRegistryImpl implements ConfigurationPrototypeRegistry {
    private Map<ConfigurationType, Configuration> configurations = new HashMap<>();
    @Override
    public void addPrototype(Configuration configuration) {

    }

    @Override
    public Configuration getPrototype(ConfigurationType type) {
        return null;
    }

    @Override
    public Configuration clone(ConfigurationType type) {
        return null;
    }
}
