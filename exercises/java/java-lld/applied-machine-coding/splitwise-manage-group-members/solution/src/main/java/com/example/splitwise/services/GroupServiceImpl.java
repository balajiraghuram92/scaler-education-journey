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
        Group group = groupRepository.findById(groupId)
                .orElseThrow(() -> new InvalidGroupException("Group not found"));

        GroupAdmin groupAdmin = groupAdminRepository.findByGroupIdAndAdminId(groupId, adminUserId)
                .orElseThrow(() -> new UnAuthorizedAccessException("The given user is not an admin of the group"));

        User memberToBeAdded = userRepository.findById(memberToBeAddedUserId)
                .orElseThrow(() -> new InvalidUserException("The given user does not exist"));

        Optional<GroupMember> groupMemberOptional = groupMemberRepository.findByGroupIdAndUserId(groupId, memberToBeAddedUserId);
        if (groupMemberOptional.isPresent()) {
            throw new InvalidUserException("The given user is already a member of the group");
        }

        GroupMember groupMember = new GroupMember();
        groupMember.setGroup(group);
        groupMember.setUser(memberToBeAdded);
        groupMember.setAddedBy(groupAdmin.getAdmin());
        groupMember.setAddedAt(new Date());
        return groupMemberRepository.save(groupMember);
    }

    @Override
    public void removeMember(long groupId, long adminUserId, long memberToBeRemovedId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException {
        groupRepository.findById(groupId)
                .orElseThrow(() -> new InvalidGroupException("Group not found"));

        groupAdminRepository.findByGroupIdAndAdminId(groupId, adminUserId)
                .orElseThrow(() -> new UnAuthorizedAccessException("The given user is not an admin of the group"));

        userRepository.findById(memberToBeRemovedId)
                .orElseThrow(() -> new InvalidUserException("The given user is not a valid user"));

        GroupMember groupMember = groupMemberRepository.findByGroupIdAndUserId(groupId, memberToBeRemovedId)
                .orElseThrow(() -> new InvalidUserException("The given user is not a member of the group"));

        groupMemberRepository.delete(groupMember);
    }

    @Override
    public List<User> fetchAllMembers(long groupId, long userId) throws InvalidGroupException, UnAuthorizedAccessException, InvalidUserException {
        groupRepository.findById(groupId)
                .orElseThrow(() -> new InvalidGroupException("Group not found"));

        userRepository.findById(userId)
                .orElseThrow(() -> new InvalidUserException("The user trying to access the group is not a valid user"));

        boolean isAdmin = groupAdminRepository.findByGroupIdAndAdminId(groupId, userId).isPresent();
        boolean isMember = groupMemberRepository.findByGroupIdAndUserId(groupId, userId).isPresent();
        if (!isAdmin && !isMember) {
            throw new UnAuthorizedAccessException("The given user is not a member of the group");
        }

        // A user can appear both as an admin row and a member row; the set removes the duplicate.
        Set<User> users = new LinkedHashSet<>();
        for (GroupAdmin groupAdmin : groupAdminRepository.findAllByGroupId(groupId)) {
            users.add(groupAdmin.getAdmin());
        }
        for (GroupMember groupMember : groupMemberRepository.findAllByGroupId(groupId)) {
            users.add(groupMember.getUser());
        }
        return new ArrayList<>(users);
    }
}
