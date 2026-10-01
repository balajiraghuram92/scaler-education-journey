package com.example.splitwise.dtos;

public class DeleteGroupRequestDto {
    private long groupId;
    private long userId;

    public long getGroupId() {
        return groupId;
    }

    public void setGroupId(long groupId) {
        this.groupId = groupId;
    }

    public long getUserId() {
        return userId;
    }

    public void setUserId(long userId) {
        this.userId = userId;
    }
}
