package com.example.splitwise.dtos;

import com.example.splitwise.models.GroupMember;

public class AddMemberResponseDto {
    private ResponseStatus responseStatus;
    private GroupMember groupMember;

    public ResponseStatus getResponseStatus() {
        return responseStatus;
    }

    public void setResponseStatus(ResponseStatus responseStatus) {
        this.responseStatus = responseStatus;
    }

    public GroupMember getGroupMember() {
        return groupMember;
    }

    public void setGroupMember(GroupMember groupMember) {
        this.groupMember = groupMember;
    }
}
