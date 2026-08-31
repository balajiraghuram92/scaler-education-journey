package apidecorator;

import apidecorator.api.Api;

public abstract class BaseApiDecorator implements Api {
    protected Api nextLayer;

    public BaseApiDecorator(Api nextLayer) {
        this.nextLayer = nextLayer;
    }
}
