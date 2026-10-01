package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupMember;

import java.util.List;

public interface GroupMemberRepository {
    GroupMember save(GroupMember groupMember);

    List<GroupMember> findAll();

    void deleteByGroupId(long groupId);
}
