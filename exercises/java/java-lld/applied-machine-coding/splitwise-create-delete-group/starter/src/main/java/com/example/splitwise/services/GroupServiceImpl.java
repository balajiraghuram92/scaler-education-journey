package com.example.splitwise.services;

import com.example.splitwise.exceptions.InvalidGroupException;
import com.example.splitwise.exceptions.InvalidUserException;
import com.example.splitwise.exceptions.UnAuthorizedAccessException;
import com.example.splitwise.models.Group;
import com.example.splitwise.models.GroupAdmin;
import com.example.splitwise.models.User;
import com.example.splitwise.repositories.GroupAdminRepository;
import com.example.splitwise.repositories.GroupMemberRepository;
import com.example.splitwise.repositories.GroupRepository;
import com.example.splitwise.repositories.UserRepository;

import java.util.Date;
import java.util.Optional;

// TODO: implement createGroup —
//  1. look up the creating user (throw InvalidUserException if absent);
//  2. save a new Group with the given name, description and createdAt = now;
//  3. save a GroupAdmin row making the creator the admin (admin = addedBy = creator);
//  4. return the saved Group.
// TODO: implement deleteGroup —
//  1. the group must exist (InvalidGroupException) and the user must exist (InvalidUserException);
//  2. only an admin of that group may delete it (UnAuthorizedAccessException otherwise);
//  3. delete the group's admin rows and member rows, then the group itself.
public class GroupServiceImpl implements GroupService {
    private final GroupRepository groupRepository;
    private final UserRepository userRepository;
    private final GroupAdminRepository groupAdminRepository;
    private final GroupMemberRepository groupMemberRepository;

    public GroupServiceImpl(GroupRepository groupRepository, UserRepository userRepository,
                            GroupAdminRepository groupAdminRepository, GroupMemberRepository groupMemberRepository) {
        this.groupRepository = groupRepository;
        this.userRepository = userRepository;
        this.groupAdminRepository = groupAdminRepository;
        this.groupMemberRepository = groupMemberRepository;
    }

    @Override
    public Group createGroup(String groupName, String description, long userId) throws InvalidUserException {
        return null;
    }

    @Override
    public void deleteGroup(long groupId, long userId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException {
    }
}
