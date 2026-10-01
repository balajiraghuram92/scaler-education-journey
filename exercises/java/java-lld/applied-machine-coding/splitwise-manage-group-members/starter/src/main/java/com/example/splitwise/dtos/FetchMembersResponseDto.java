package com.example.splitwise.dtos;

import com.example.splitwise.models.User;

import java.util.List;

public class FetchMembersResponseDto {
    private List<User> members;
    private ResponseStatus responseStatus;

    public List<User> getMembers() {
        return members;
    }

    public void setMembers(List<User> members) {
        this.members = members;
    }

    public ResponseStatus getResponseStatus() {
        return responseStatus;
    }

    public void setResponseStatus(ResponseStatus responseStatus) {
        this.responseStatus = responseStatus;
    }
}
