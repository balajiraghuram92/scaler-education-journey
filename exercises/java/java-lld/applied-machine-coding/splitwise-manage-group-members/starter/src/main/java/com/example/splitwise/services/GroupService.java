package com.example.splitwise.services;

import com.example.splitwise.exceptions.InvalidGroupException;
import com.example.splitwise.exceptions.InvalidUserException;
import com.example.splitwise.exceptions.UnAuthorizedAccessException;
import com.example.splitwise.models.GroupMember;
import com.example.splitwise.models.User;

import java.util.List;

public interface GroupService {
    GroupMember addMember(long groupId, long adminId, long userId) throws InvalidGroupException, InvalidUserException, UnAuthorizedAccessException;

    void removeMember(long groupId, long adminId, long userId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException;

    List<User> fetchAllMembers(long groupId, long userId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException;
}
