# Prototype Configuration

Source folder: `1773391196_5bc9ddd0c91d4438/Prototype_Config-solution`

## Problem Statement

Implement the Prototype design pattern for efficient configuration object cloning. Create prototype configuration objects that can be efficiently cloned for testing and development, avoiding the overhead of creating configurations from scratch.

## Graded Contract (from tests)

From `ConfigurationTest.java`, the following must be present and function correctly:

- **Interface `ClonableObject<T>`** (generic interface)
  - Must be located in package `com.assignment.question`
  - Must define a method `T cloneObject()` that returns a cloned copy of the implementing object

- **Enum `ConfigurationType`**
  - Must have at least: BASIC, ADVANCED, CUSTOM, DEFAULT

- **Class `Configuration` implements `ClonableObject<Configuration>`**
  - Must implement the `ClonableObject<Configuration>` interface
  - Must have fields: String themeColor, Boolean autoSave, String language, Boolean darkMode, Integer fontSize, String fontFamily, ConfigurationType type
  - Must have a public constructor accepting all these parameters in order
  - Must have public getters for all fields: getThemeColor(), getAutoSave(), getLanguage(), getDarkMode(), getFontSize(), getFontFamily(), getType()
  - Must implement `Configuration cloneObject()` method
    - Must return a new Configuration object with the same field values
    - The returned object must NOT be the same object in memory (assertNotSame check)

- **Interface `ConfigurationPrototypeRegistry`**
  - Must define: `void addPrototype(Configuration user)`
  - Must define: `Configuration getPrototype(ConfigurationType type)`
  - Must define: `Configuration clone(ConfigurationType type)`

- **Class implementing `ConfigurationPrototypeRegistry`** (exactly one non-abstract implementation must exist)
  - Must have a public no-args constructor
  - `addPrototype()` must store configuration by its type
  - `getPrototype()` must return the stored configuration (same object reference)
  - `clone()` must call cloneObject() on the stored configuration and return the clone

## Learner Template

```java
package com.assignment.question;

public interface ClonableObject<T> {
    T cloneObject();
}
```

```java
package com.assignment.question;

public enum ConfigurationType {
    BASIC,
    ADVANCED,
    CUSTOM,
    DEFAULT
}
```

```java
package com.assignment.question;

public class Configuration implements ClonableObject<Configuration> {
    private String themeColor;
    private Boolean autoSave;
    private String language;
    private Boolean darkMode;
    private Integer fontSize;
    private String fontFamily;
    private ConfigurationType type;
    
    public Configuration(String themeColor, Boolean autoSave, String language, Boolean darkMode, Integer fontSize, String fontFamily, ConfigurationType type) {
        // TODO: implement
    }
    
    public String getThemeColor() {
        // TODO: implement
    }
    
    public Boolean getAutoSave() {
        // TODO: implement
    }
    
    public String getLanguage() {
        // TODO: implement
    }
    
    public Boolean getDarkMode() {
        // TODO: implement
    }
    
    public Integer getFontSize() {
        // TODO: implement
    }
    
    public String getFontFamily() {
        // TODO: implement
    }
    
    public ConfigurationType getType() {
        // TODO: implement
    }
    
    @Override
    public Configuration cloneObject() {
        // TODO: implement - create and return new Configuration with same field values
    }
}
```

```java
package com.assignment.question;

public interface ConfigurationPrototypeRegistry {
    void addPrototype(Configuration user);
    Configuration getPrototype(ConfigurationType type);
    Configuration clone(ConfigurationType type);
}
```

```java
package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

public class ConfigurationPrototypeRegistryImpl implements ConfigurationPrototypeRegistry {
    private Map<ConfigurationType, Configuration> configurations = new HashMap<>();
    
    @Override
    public void addPrototype(Configuration configuration) {
        // TODO: implement
    }
    
    @Override
    public Configuration getPrototype(ConfigurationType type) {
        // TODO: implement
    }
    
    @Override
    public Configuration clone(ConfigurationType type) {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learer to design)

- Field assignment in constructor
- Getter implementation logic
- HashMap storage and retrieval logic
- Cloning logic (copying all field values to new object)
- Any validation or null-checking beyond the contract
- Setter methods or mutators (not in graded contract)
- toString(), equals(), or hashCode() methods
