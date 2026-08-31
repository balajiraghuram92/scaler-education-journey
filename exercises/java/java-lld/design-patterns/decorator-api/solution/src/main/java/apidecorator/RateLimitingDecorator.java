package apidecorator;

import apidecorator.api.Api;
import apidecorator.utils.ApiUtils;
import apidecorator.utils.RateLimitExceededException;

public class RateLimitingDecorator extends BaseApiDecorator {

    public RateLimitingDecorator(Api nextLayer) {
        super(nextLayer);
    }

    @Override
    public String executeRequest(String requestData) {
        if (ApiUtils.rateLimitExceeded(requestData)) {
            throw new RateLimitExceededException("Rate limit exceeded");
        }

        return nextLayer.executeRequest(requestData);
    }
}
