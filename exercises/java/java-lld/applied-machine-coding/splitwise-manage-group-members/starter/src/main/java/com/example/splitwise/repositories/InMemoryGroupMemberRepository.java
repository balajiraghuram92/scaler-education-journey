package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupMember;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

// TODO: implement GroupMemberRepository as an in-memory store keyed by id —
// save(...) assigns an id when absent (id == 0) and stores the row;
// findByGroupIdAndUserId(...) returns the row whose group id and user id both match;
// findAllByGroupId(...) returns every member row of that group;
// delete(...) removes the given row.
public class InMemoryGroupMemberRepository implements GroupMemberRepository {
    private final Map<Long, GroupMember> groupMembers = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public GroupMember save(GroupMember groupMember) {
        return null;
    }

    @Override
    public Optional<GroupMember> findByGroupIdAndUserId(long groupId, long userId) {
        return Optional.empty();
    }

    @Override
    public List<GroupMember> findAllByGroupId(long groupId) {
        return new ArrayList<>();
    }

    @Override
    public void delete(GroupMember groupMember) {
    }
}
