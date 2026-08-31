package apidecorator;

import apidecorator.api.Api;

/**
 * TODO - Each decorator should have the same methods as the product it decorates, i.e. executeRequest.
 * Inherit from the API interface {@link apidecorator.api.Api}.
 *
 * TODO - Each decorator will have to call the next decorator in the chain and finally reach
 * {@link apidecorator.api.SimpleEcommerceAPI}. Add a protected field of type {@link apidecorator.api.Api}
 * storing the next layer, and a constructor taking that next layer.
 */
public abstract class BaseApiDecorator implements Api {

}
