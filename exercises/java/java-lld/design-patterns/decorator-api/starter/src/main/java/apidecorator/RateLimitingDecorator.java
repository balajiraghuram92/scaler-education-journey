package apidecorator;

import apidecorator.api.Api;
import apidecorator.utils.ApiUtils;
import apidecorator.utils.RateLimitExceededException;

/**
 * TODO - Extend {@link BaseApiDecorator} to enforce rate limiting.
 * Use {@link apidecorator.utils.ApiUtils#rateLimitExceeded(String)} to check the limit; if exceeded, throw
 * {@link apidecorator.utils.RateLimitExceededException}, otherwise call the next layer.
 * Also add a constructor taking the next layer of type {@link apidecorator.api.Api} and calling super.
 */
public class RateLimitingDecorator extends BaseApiDecorator {

}
