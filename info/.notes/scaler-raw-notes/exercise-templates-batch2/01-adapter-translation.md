# Adapter Pattern for Language Translation Integration

Source folder: `1773391210_078f77dc68eb8a6b/Adaptor_Translat-solution`

## Problem Statement

You are developing a language translation tool that needs to integrate with different translation services like Google Translate, Microsoft Translator, and Yandex.Translate. Each service offers its own API and response format, making integration complex. To simplify this process and ensure consistency in the codebase, you decide to implement the Adapter pattern. This pattern allows you to create adapter classes for different translation services, converting their APIs into a common format that your application can work with.

## Detailed Requirements

1. **Review the existing translation services**: Study the APIs and response formats of the translation services you need to integrate with. Understand how each service's API works and the data it provides.

2. **Implement the adapter interface**: You have been provided with a `TranslationProviderAdapter` interface. Your task is to create adapter classes for each translation service that implements this interface. These adapters should adapt the specific translation service's API into a format that matches the methods defined in the `TranslationProviderAdapter`.

3. **Use composition**: Create adapter classes that internally use instances of the actual translation service APIs, such as `GoogleTranslateApi` and `MicrosoftTranslateApi`. Avoid modifying the provider APIs directly; instead, create methods in the adapter classes that map to the provider APIs and perform the necessary data transformations.

4. **Additional method**: Apart from the `translate` method, you should implement another method as required by the assignment.

5. **Test your implementation**: Execute the provided test cases in the `TranslationProviderAdapterTest` class to validate the correctness of your adapter classes. These test cases will ensure that your adapters have the required methods and interact with the provider APIs properly.

## Any Given "Before" Code

The problem involves adapting two incompatible external translation API services with different interfaces into a unified interface:

**GoogleTranslateApi** (external service):
- Method: `convert(GoogleTranslationRequest request) -> String`
- Method: `getLanguages() -> List<String>`
- Uses: `GoogleTranslationRequest` object with custom parameters

**MicrosoftTranslateApi** (external service):
- Method: `translate(String text, String sourceLanguage, String targetLanguage) -> String`
- Method: `getSupportedLanguages() -> List<String>`
- Uses: individual string parameters

Both services return the same data (translated text, supported languages) but with different method signatures and parameter formats.

## Graded Contract (from tests)

The tests verify the following:

- **TranslationProviderAdapter interface** must have at least 2 methods
- **translate(TranslationRequest) -> String** method exists (1 param of type TranslationRequest, returns String)
- **getSupportedLanguages() -> List<String>** method exists (0 params, returns List of Strings)
- **At least 2 implementations** of TranslationProviderAdapter exist (e.g., GoogleTranslationAdapter, MicrosoftTranslationAdapter)
- Each adapter implementation must have a field reference to an external API (GoogleTranslateApi or MicrosoftTranslateApi)
- **TranslationRequest class** must have 4 fields: 3 String fields + 1 Double field
- The `translate` method in each adapter must call the corresponding external API's translate method
- The `getSupportedLanguages` method in each adapter must call the corresponding external API's method for getting supported languages

## Learner Template

```java
package com.assignment.question;

import java.util.List;

public interface TranslationProviderAdapter {
    String translate(TranslationRequest request);
    
    List<String> getSupportedLanguages();
}
```

```java
package com.assignment.question;

import lombok.Getter;
import lombok.NoArgsConstructor;

@NoArgsConstructor
@Getter
public class TranslationRequest {
    private String text;
    private String sourceLanguage;
    private String targetLanguage;
    private Double confidenceThreshold;
}
```

```java
package com.assignment.question;

import com.assignment.question.external.GoogleTranslateApi;
import java.util.List;

public class GoogleTranslationAdapter implements TranslationProviderAdapter {
    private GoogleTranslateApi googleTranslateApi;
    
    @Override
    public String translate(TranslationRequest request) {
        // TODO: implement
    }
    
    @Override
    public List<String> getSupportedLanguages() {
        // TODO: implement
    }
}
```

```java
package com.assignment.question;

import com.assignment.question.external.MicrosoftTranslateApi;
import java.util.List;

public class MicrosoftTranslationAdapter implements TranslationProviderAdapter {
    private MicrosoftTranslateApi translateApi;
    
    @Override
    public String translate(TranslationRequest request) {
        // TODO: implement
    }
    
    @Override
    public List<String> getSupportedLanguages() {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- The implementation logic of the `translate()` method in each adapter, including how to map TranslationRequest fields to the external API's specific request format
- The initialization/construction of the external API instances in each adapter
- The actual data transformation logic (e.g., how GoogleTranslationRequest is created from TranslationRequest in GoogleTranslationAdapter)
- The implementation of `getSupportedLanguages()` in each adapter
