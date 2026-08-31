package apidecorator;

import apidecorator.api.Api;

/**
 * TODO - Extend {@link BaseApiDecorator} to log the request before delegating to the next layer.
 * 1. Implement executeRequest: log the request, then call the next layer.
 * 2. Add a constructor taking the next layer of type {@link apidecorator.api.Api} and calling super.
 */
public class LoggingDecorator extends BaseApiDecorator {

}
