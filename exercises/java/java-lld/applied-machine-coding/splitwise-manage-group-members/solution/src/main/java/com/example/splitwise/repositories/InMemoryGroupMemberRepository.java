package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupMember;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

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
    public Optional<GroupMember> findByGroupIdAndUserId(long groupId, long userId) {
        return groupMembers.values().stream()
                .filter(groupMember -> groupMember.getGroup().getId() == groupId
                        && groupMember.getUser().getId() == userId)
                .findFirst();
    }

    @Override
    public List<GroupMember> findAllByGroupId(long groupId) {
        return groupMembers.values().stream()
                .filter(groupMember -> groupMember.getGroup().getId() == groupId)
                .collect(Collectors.toList());
    }

    @Override
    public void delete(GroupMember groupMember) {
        groupMembers.remove(groupMember.getId());
    }
}
