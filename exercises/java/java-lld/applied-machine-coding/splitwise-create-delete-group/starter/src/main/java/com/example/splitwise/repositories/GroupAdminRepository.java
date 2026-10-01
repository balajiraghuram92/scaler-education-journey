package com.example.splitwise.repositories;

import com.example.splitwise.models.GroupAdmin;

import java.util.List;
import java.util.Optional;

public interface GroupAdminRepository {
    GroupAdmin save(GroupAdmin groupAdmin);

    List<GroupAdmin> findAll();

    Optional<GroupAdmin> findByGroupIdAndAdminId(long groupId, long adminId);

    void deleteByGroupId(long groupId);
}
