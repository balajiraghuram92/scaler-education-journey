package com.example.cloudproviders.adapters;

import com.example.cloudproviders.libraries.aws.AWSApi;
import com.example.cloudproviders.libraries.aws.AWSConnectionResponse;
import com.example.cloudproviders.models.Connection;
import com.example.cloudproviders.models.ConnectionStatus;

// TODO: implement CloudAdapter by delegating to AWSApi — call awsApi.createConnection(userId),
// then map the AWSConnectionResponse fields onto a new Connection (connectionId,
// connectionStatus via ConnectionStatus.valueOf(...), and the given userId).
public class AWSAdapter implements CloudAdapter {
    private AWSApi awsApi;
    public AWSAdapter() {
        this.awsApi = new AWSApi();
    }

    @Override
    public Connection createConnection(long userId) {
        return null;
    }
}
