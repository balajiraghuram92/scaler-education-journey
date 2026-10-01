package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupMember;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class InMemoryGroupMemberRepository implements GroupMemberRepository {
    private final Map<Long, GroupMember> groupMembers = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public GroupMember save(GroupMember groupMember) {
        if (groupMember.getId() == 0) {
            groupMember.setId(idCounter.incrementAndGet());
        }
        groupMembers.put(groupMember.getId(), groupMember);
        return groupMember;
    }

    @Override
    public List<GroupMember> findAll() {
        return new ArrayList<>(groupMembers.values());
    }

    @Override
    public void deleteByGroupId(long groupId) {
        groupMembers.values().removeIf(groupMember -> groupMember.getGroup().getId() == groupId);
    }
}
