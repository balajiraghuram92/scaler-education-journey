package com.example.splitwise.repositories;

import com.example.splitwise.models.Group;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class InMemoryGroupRepository implements GroupRepository {
    private final Map<Long, Group> groups = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public Group save(Group group) {
        if (group.getId() == 0) {
            group.setId(idCounter.incrementAndGet());
        }
        groups.put(group.getId(), group);
        return group;
    }

    @Override
    public Optional<Group> findById(long groupId) {
        return Optional.ofNullable(groups.get(groupId));
    }
}
