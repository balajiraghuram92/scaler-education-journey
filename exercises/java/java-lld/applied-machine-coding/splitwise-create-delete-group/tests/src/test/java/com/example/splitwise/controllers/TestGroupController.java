package com.example.splitwise.controllers;

import com.example.splitwise.dtos.*;
import com.example.splitwise.models.Group;
import com.example.splitwise.models.GroupAdmin;
import com.example.splitwise.models.GroupMember;
import com.example.splitwise.models.User;
import com.example.splitwise.repositories.*;
import com.example.splitwise.services.GroupServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

// Ported from the Scaler Splitwise "create/delete group" exercise (Spring Boot + JPA + H2).
// Spring wiring is replaced by explicit constructor wiring over in-memory repositories;
// the test scenarios and assertions are unchanged.
public class TestGroupController {

    private GroupRepository groupRepository;
    private UserRepository userRepository;
    private GroupAdminRepository groupAdminRepository;
    private GroupMemberRepository groupMemberRepository;

    private GroupController groupController;

    private User user;

    @BeforeEach
    public void insertDummy() {
        groupRepository = new InMemoryGroupRepository();
        userRepository = new InMemoryUserRepository();
        groupAdminRepository = new InMemoryGroupAdminRepository();
        groupMemberRepository = new InMemoryGroupMemberRepository();
        groupController = new GroupController(
                new GroupServiceImpl(groupRepository, userRepository, groupAdminRepository, groupMemberRepository));

        user = new User();
        user.setName("Admin 1");
        user.setPhoneNumber("1234567890");
        user = userRepository.save(user);
    }

    @Test
    public void testCreateGroup_UserNotPresent() {
        CreateGroupRequestDto requestDto = new CreateGroupRequestDto();
        requestDto.setName("Group 1");
        requestDto.setDescription("Group 1 Description");
        requestDto.setCreatorUserId(1000L);

        CreateGroupResponseDto responseDto = groupController.createGroup(requestDto);

        assertEquals(ResponseStatus.FAILURE, responseDto.getResponseStatus());
    }

    @Test
    public void testCreateGroup_Success() {
        CreateGroupRequestDto requestDto = new CreateGroupRequestDto();
        requestDto.setName("Group 1");
        requestDto.setDescription("Group 1 Description");
        requestDto.setCreatorUserId(user.getId());

        CreateGroupResponseDto responseDto = groupController.createGroup(requestDto);

        assertEquals(ResponseStatus.SUCCESS, responseDto.getResponseStatus());
        assertNotNull(responseDto.getGroup(), "Group should not be null");
        assertEquals("Group 1", responseDto.getGroup().getName(), "Group name should be same");
        assertEquals("Group 1 Description", responseDto.getGroup().getDescription(), "Group description should be same");

        List<GroupAdmin> all = groupAdminRepository.findAll().stream()
                .filter(groupAdmin -> groupAdmin.getGroup().getId() == responseDto.getGroup().getId())
                .collect(Collectors.toList());
        assertEquals(1, all.size(), "There should be one group admin");
        assertEquals(user.getId(), all.get(0).getAdmin().getId(), "The creator should be the group admin");
    }

    @Test
    public void testDeleteGroup_GroupNotPresent() {
        DeleteGroupRequestDto requestDto = new DeleteGroupRequestDto();
        requestDto.setGroupId(1000L);
        requestDto.setUserId(user.getId());

        DeleteGroupResponseDto responseDto = groupController.deleteGroup(requestDto);
        assertEquals(ResponseStatus.FAILURE, responseDto.getResponseStatus(), "Response status should be failure");
    }

    @Test
    public void testDeleteGroup_UserNotPresent() {
        Group group = new Group();
        group.setName("Group 1");
        group.setDescription("Group 1 Description");
        group = groupRepository.save(group);

        DeleteGroupRequestDto requestDto = new DeleteGroupRequestDto();
        requestDto.setGroupId(group.getId());
        requestDto.setUserId(1000L);

        DeleteGroupResponseDto responseDto = groupController.deleteGroup(requestDto);

        assertEquals(ResponseStatus.FAILURE, responseDto.getResponseStatus(), "Response status should be failure");
    }

    @Test
    public void testDeleteGroup_UserNotAdmin() {
        Group group = new Group();
        group.setName("Group 1");
        group.setDescription("Group 1 Description");
        group = groupRepository.save(group);

        User user2 = new User();
        user2.setName("Admin 2");
        user2.setPhoneNumber("1234567890");
        user2 = userRepository.save(user2);

        GroupAdmin groupAdmin = new GroupAdmin();
        groupAdmin.setGroup(group);
        groupAdmin.setAdmin(user2);
        groupAdmin.setAddedBy(user2);
        groupAdminRepository.save(groupAdmin);

        DeleteGroupRequestDto requestDto = new DeleteGroupRequestDto();
        requestDto.setGroupId(group.getId());
        requestDto.setUserId(user.getId());

        DeleteGroupResponseDto responseDto = groupController.deleteGroup(requestDto);

        assertEquals(ResponseStatus.FAILURE, responseDto.getResponseStatus(), "Response status should be failure");
        assertEquals(1, groupRepository.findAll().size(), "Group must survive an unauthorized delete");
    }

    @Test
    public void testDeleteGroup_Success() {
        Group group = new Group();
        group.setName("Group 1");
        group.setDescription("Group 1 Description");
        group = groupRepository.save(group);

        GroupAdmin groupAdmin = new GroupAdmin();
        groupAdmin.setGroup(group);
        groupAdmin.setAdmin(user);
        groupAdmin.setAddedBy(user);
        groupAdminRepository.save(groupAdmin);

        User member = new User();
        member.setName("Member 1");
        member.setPhoneNumber("1234567890");
        member = userRepository.save(member);

        GroupMember groupMember = new GroupMember();
        groupMember.setGroup(group);
        groupMember.setUser(member);
        groupMember.setAddedBy(user);
        groupMemberRepository.save(groupMember);

        DeleteGroupRequestDto requestDto = new DeleteGroupRequestDto();
        requestDto.setGroupId(group.getId());
        requestDto.setUserId(user.getId());

        DeleteGroupResponseDto responseDto = groupController.deleteGroup(requestDto);

        assertEquals(ResponseStatus.SUCCESS, responseDto.getResponseStatus(), "Response status should be success");

        Group finalGroup = group;
        List<Group> groups = this.groupRepository.findAll().stream()
                .filter(g -> g.getId() == finalGroup.getId()).collect(Collectors.toList());
        assertEquals(0, groups.size(), "Group should be deleted");

        List<GroupAdmin> groupAdmins = this.groupAdminRepository.findAll().stream()
                .filter(g -> g.getGroup().getId() == finalGroup.getId()).collect(Collectors.toList());
        assertEquals(0, groupAdmins.size(), "Group admin should be deleted");

        List<GroupMember> groupMembers = this.groupMemberRepository.findAll().stream()
                .filter(g -> g.getGroup().getId() == finalGroup.getId()).collect(Collectors.toList());
        assertEquals(0, groupMembers.size(), "Group member should be deleted");
    }
}
