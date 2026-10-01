package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupMember;

import java.util.List;
import java.util.Optional;

public interface GroupMemberRepository {
    GroupMember save(GroupMember groupMember);

    Optional<GroupMember> findByGroupIdAndUserId(long groupId, long userId);

    List<GroupMember> findAllByGroupId(long groupId);

    void delete(GroupMember groupMember);
}
