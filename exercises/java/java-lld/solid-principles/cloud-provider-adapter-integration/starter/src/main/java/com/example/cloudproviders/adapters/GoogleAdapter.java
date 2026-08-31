package com.example.cloudproviders.adapters;

import com.example.cloudproviders.libraries.google.GoogleApi;
import com.example.cloudproviders.libraries.google.GoogleConnectionResponse;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.models.ConnectionStatus;

// TODO: implement CloudAdapter by delegating to GoogleApi — call
// googleApi.createConnection(userId), then map the GoogleConnectionResponse fields onto
// a new Connection (connectionId, connectionStatus via ConnectionStatus.valueOf(...),
// and the given userId).
public class GoogleAdapter implements CloudAdapter {
    private GoogleApi googleApi;

    public GoogleAdapter() {
        this.googleApi = new GoogleApi();
    }

    @Override
    public Connection createConnection(long userId) {
        return null;
    }
}
