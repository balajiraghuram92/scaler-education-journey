# Adapter Pattern for Social Media Aggregator

Source folder: `1786172667_5ddb808c3ff8b67b / Social_Adaptor-solution`

## Problem Statement

You are working on a social media aggregator app that pulls in posts from various social platforms. Each platform provides data in different structures through distinct APIs. Your task is to unify the data format within the app and ensure that integrating new social platforms remains hassle-free. To achieve this, you want to implement the Adapter pattern, allowing you to create adapter classes for different social media platform APIs. These adapters will convert platform-specific APIs into a common format that your application can use.

## Detailed Requirements

Your goal is to implement the Adapter pattern to create adapter classes for different social media platform APIs. These adapters should conform to a common interface, making it easy to integrate new platforms in the future. Your task is to abstract away the differences in APIs and data formats and provide a unified interface for your application to work with.

### Implementing the Adapter Pattern

1. **Review the existing APIs**: Study the APIs and data formats of the social media platforms you need to integrate. Understand the differences in their APIs and how they interact with their respective systems.

2. **Implement the adapter interface**: You have been provided with a `SocialMediaAdapter` interface. Your task is to implement this interface in different adapter classes, each corresponding to a different social media platform. The adapters should adapt the provider-specific APIs into a format that matches the `SocialMediaAdapter` interface.

3. **Use composition**: Create adapter classes that internally use instances of the actual social media platform APIs. You should not modify the platform APIs directly. Instead, create methods in the adapter classes that map to the platform APIs and perform the necessary transformations.

4. **Test your implementation**: Run the provided test cases in the `SocialMediaAdapterTest` class to ensure that your adapter classes work correctly. These test cases will check if your adapters have the required methods and if they interact with the platform APIs properly.

### Instructions

1. Implement the Adapter pattern by creating adapter classes that implement the `SocialMediaAdapter` interface and adapt the APIs of different social media platforms.
2. Implement the `SocialMediaPost` model class with 4 fields (2 String fields and 2 Long fields) to represent a unified post format across all platforms.
3. Run the provided test cases in the `SocialMediaAdapterTest` class to verify the correctness of your adapter pattern implementation. Make sure your adapters have the expected methods and interact with the platform APIs as required.

## Graded Contract (from tests)

- `SocialMediaAdapter` interface must have:
  - `List<SocialMediaPost> getPosts(Long userId, Long timestamp)` method
  - `void post(Long userId, String message)` method
- `SocialMediaPost` model must have exactly 4 fields:
  - 2 fields of type `String`
  - 2 fields of type `Long`
- At least 2 adapter implementations of `SocialMediaAdapter` interface (e.g., TwitterAdapter, FacebookAdapter)
- Each adapter implementation must:
  - Have a default no-arg constructor
  - Have a field of type `TwitterApi` or `FacebookApi` (the platform-specific API)
  - Implement both `getPosts()` and `post()` methods
- Tests verify:
  - Adapter classes implement the interface
  - Each adapter has a reference to the platform-specific API
  - `getPosts()` method is invoked with two Long parameters and returns a List
  - `post()` method is invoked with Long userId and String message
  - Adapters call appropriate ApiUtils methods (e.g., `ApiUtils.logTwitterGetPosts()`, `ApiUtils.logFacebookGetPosts()`, etc.)

## Learner Template

```java
package com.assignment.adapters;

import com.assignment.models.SocialMediaPost;

import java.util.List;

public interface SocialMediaAdapter {

    List<SocialMediaPost> getPosts(Long userId, Long timestamp);

    void post(Long userId, String message);
}
```

```java
package com.assignment.models;

public class SocialMediaPost {
    
    // TODO: Add 4 fields (2 String, 2 Long)
    
    // TODO: Add constructor and accessors
}
```

```java
package com.assignment.adapters;

import com.assignment.api.TwitterApi;
import com.assignment.api.TwitterTweet;
import com.assignment.models.SocialMediaPost;

import java.util.List;

public class TwitterAdapter implements SocialMediaAdapter {
    
    private TwitterApi twitterApi;
    
    public TwitterAdapter() {
        // TODO: Implement
    }
    
    @Override
    public List<SocialMediaPost> getPosts(Long userId, Long timestamp) {
        // TODO: Implement
    }

    @Override
    public void post(Long userId, String message) {
        // TODO: Implement
    }
}
```

```java
package com.assignment.adapters;

import com.assignment.api.FacebookApi;
import com.assignment.api.FacebookPost;
import com.assignment.models.SocialMediaPost;

import java.util.List;

public class FacebookAdapter implements SocialMediaAdapter {
    
    private FacebookApi facebookApi;
    
    public FacebookAdapter() {
        // TODO: Implement
    }
    
    @Override
    public List<SocialMediaPost> getPosts(Long userId, Long timestamp) {
        // TODO: Implement
    }

    @Override
    public void post(Long userId, String message) {
        // TODO: Implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- The 4 fields in `SocialMediaPost` model class (must determine which fields map to which platforms)
- Constructor and getter/setter methods for `SocialMediaPost`
- The initialization of `twitterApi` and `facebookApi` instances in their respective adapter constructors
- The logic to transform platform-specific post objects (TwitterTweet, FacebookPost) into `SocialMediaPost` objects
- The specific mapping logic between platform APIs and the unified interface (e.g., `getTweets()` vs `getPosts()`, field name mappings)
- The calling of ApiUtils utility methods to log API interactions
