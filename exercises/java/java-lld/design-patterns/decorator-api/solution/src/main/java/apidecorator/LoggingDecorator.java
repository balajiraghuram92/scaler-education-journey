package apidecorator;

import apidecorator.api.Api;

public class LoggingDecorator extends BaseApiDecorator {

    public LoggingDecorator(Api nextLayer) {
        super(nextLayer);
    }

    @Override
    public String executeRequest(String requestData) {
        System.out.println("Logging request: " + requestData);
        return nextLayer.executeRequest(requestData);
    }
}
