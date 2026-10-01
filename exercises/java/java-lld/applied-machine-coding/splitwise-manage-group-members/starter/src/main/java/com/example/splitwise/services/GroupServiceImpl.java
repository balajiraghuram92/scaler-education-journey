package com.example.splitwise.services;

import com.example.splitwise.exceptions.InvalidGroupException;
import com.example.splitwise.exceptions.InvalidUserException;
import com.example.splitwise.exceptions.UnAuthorizedAccessException;
import com.example.splitwise.models.Group;
import com.example.splitwise.models.GroupAdmin;
import com.example.splitwise.models.GroupMember;
import com.example.splitwise.models.User;
import com.example.splitwise.repositories.GroupAdminRepository;
import com.example.splitwise.repositories.GroupMemberRepository;
import com.example.splitwise.repositories.GroupRepository;
import com.example.splitwise.repositories.UserRepository;

import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

// TODO: implement addMember — the group must exist (InvalidGroupException); the caller must be an
//  admin of that group (UnAuthorizedAccessException); the user being added must exist and must not
//  already be a member (InvalidUserException). Save a GroupMember with addedBy = the admin and
//  addedAt = now, and return it.
// TODO: implement removeMember — same group/admin/user checks; the user must currently be a member
//  of the group (InvalidUserException otherwise); delete that GroupMember row.
// TODO: implement fetchAllMembers — the group and the requesting user must exist; only an admin or a
//  member of the group may list it (UnAuthorizedAccessException otherwise). Return every admin and
//  every member of the group, each user once.
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
    public GroupMember addMember(long groupId, long adminUserId, long memberToBeAddedUserId) throws InvalidGroupException, InvalidUserException, UnAuthorizedAccessException {
        return null;
    }

    @Override
    public void removeMember(long groupId, long adminUserId, long memberToBeRemovedId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException {
    }

    @Override
    public List<User> fetchAllMembers(long groupId, long userId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException {
        return null;
    }
}
