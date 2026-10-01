package com.example.splitwise.dtos;

import com.example.splitwise.models.Group;

public class CreateGroupResponseDto {
    private Group group;
    private ResponseStatus responseStatus;

    public Group getGroup() {
        return group;
    }

    public void setGroup(Group group) {
        this.group = group;
    }

    public ResponseStatus getResponseStatus() {
        return responseStatus;
    }

    public void setResponseStatus(ResponseStatus responseStatus) {
        this.responseStatus = responseStatus;
    }
}
