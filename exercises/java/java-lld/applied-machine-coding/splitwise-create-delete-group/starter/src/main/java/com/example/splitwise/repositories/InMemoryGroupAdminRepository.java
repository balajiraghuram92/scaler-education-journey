package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupAdmin;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

// TODO: implement GroupAdminRepository as an in-memory store keyed by id —
// save(...) assigns an id when absent (id == 0) and stores the row;
// findByGroupIdAndAdminId(...) returns the row whose group id and admin user id both match;
// deleteByGroupId(...) removes every admin row belonging to that group.
public class InMemoryGroupAdminRepository implements GroupAdminRepository {
    private final Map<Long, GroupAdmin> groupAdmins = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public GroupAdmin save(GroupAdmin groupAdmin) {
        return null;
    }

    @Override
    public List<GroupAdmin> findAll() {
        return new ArrayList<>(groupAdmins.values());
    }

    @Override
    public Optional<GroupAdmin> findByGroupIdAndAdminId(long groupId, long adminId) {
        return Optional.empty();
    }

    @Override
    public void deleteByGroupId(long groupId) {
    }
}
