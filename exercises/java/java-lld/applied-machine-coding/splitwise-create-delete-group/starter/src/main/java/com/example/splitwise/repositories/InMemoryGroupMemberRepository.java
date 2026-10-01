package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupMember;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

// TODO: implement GroupMemberRepository as an in-memory store keyed by id —
// save(...) assigns an id when absent (id == 0) and stores the row;
// deleteByGroupId(...) removes every member row belonging to that group.
public class InMemoryGroupMemberRepository implements GroupMemberRepository {
    private final Map<Long, GroupMember> groupMembers = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public GroupMember save(GroupMember groupMember) {
        return null;
    }

    @Override
    public List<GroupMember> findAll() {
        return new ArrayList<>(groupMembers.values());
    }

    @Override
    public void deleteByGroupId(long groupId) {
    }
}
