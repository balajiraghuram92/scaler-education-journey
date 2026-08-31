package apidecorator.api;

import apidecorator.utils.ApiUtils;

public class SimpleEcommerceAPI implements Api {

    private static final String API_URL = "https://api.ecommerce.com";

    @Override
    public String executeRequest(String requestData) {
        return ApiUtils.callAPI(API_URL, requestData);
    }
}
