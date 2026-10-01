package com.example.splitwise.services;

import com.example.splitwise.exceptions.InvalidGroupException;
import com.example.splitwise.exceptions.InvalidUserException;
import com.example.splitwise.exceptions.UnAuthorizedAccessException;
import com.example.splitwise.models.Group;

public interface GroupService {
    Group createGroup(String groupName, String description, long userId) throws InvalidUserException;

    void deleteGroup(long groupId, long userId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException;
}
