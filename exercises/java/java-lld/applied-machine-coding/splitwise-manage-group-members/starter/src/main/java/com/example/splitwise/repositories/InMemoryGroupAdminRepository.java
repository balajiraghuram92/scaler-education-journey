package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupAdmin;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class InMemoryGroupAdminRepository implements GroupAdminRepository {
    private final Map<Long, GroupAdmin> groupAdmins = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public GroupAdmin save(GroupAdmin groupAdmin) {
        if (groupAdmin.getId() == 0) {
            groupAdmin.setId(idCounter.incrementAndGet());
        }
        groupAdmins.put(groupAdmin.getId(), groupAdmin);
        return groupAdmin;
    }

    @Override
    public Optional<GroupAdmin> findByGroupIdAndAdminId(long groupId, long adminId) {
        return groupAdmins.values().stream()
                .filter(groupAdmin -> groupAdmin.getGroup().getId() == groupId
                        && groupAdmin.getAdmin().getId() == adminId)
                .findFirst();
    }

    @Override
    public List<GroupAdmin> findAllByGroupId(long groupId) {
        return groupAdmins.values().stream()
                .filter(groupAdmin -> groupAdmin.getGroup().getId() == groupId)
                .collect(Collectors.toList());
    }
}
