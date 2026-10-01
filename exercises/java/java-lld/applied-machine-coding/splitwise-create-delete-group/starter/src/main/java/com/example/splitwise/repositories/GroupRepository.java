package com.example.splitwise.repositories;

import com.example.splitwise.models.Group;

import java.util.List;
import java.util.Optional;

public interface GroupRepository {
    Group save(Group group);

    Optional<Group> findById(long groupId);

    List<Group> findAll();

    void delete(Group group);
}
