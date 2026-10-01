package com.example.splitwise.controllers;

import com.example.splitwise.dtos.AddMemberRequestDto;
import com.example.splitwise.dtos.AddMemberResponseDto;
import com.example.splitwise.dtos.FetchMembersRequestDto;
import com.example.splitwise.dtos.FetchMembersResponseDto;
import com.example.splitwise.dtos.RemoveMemberRequestDto;
import com.example.splitwise.dtos.RemoveMemberResponseDto;
import com.example.splitwise.dtos.ResponseStatus;
import com.example.splitwise.services.GroupService;

public class GroupController {
    private final GroupService groupService;

    public GroupController(GroupService groupService) {
        this.groupService = groupService;
    }

    public AddMemberResponseDto addMember(AddMemberRequestDto requestDto) {
        AddMemberResponseDto responseDto = new AddMemberResponseDto();
        try {
            responseDto.setGroupMember(groupService.addMember(requestDto.getGroupId(), requestDto.getAdminId(), requestDto.getMemberId()));
            responseDto.setResponseStatus(ResponseStatus.SUCCESS);
        } catch (Exception e) {
            responseDto.setResponseStatus(ResponseStatus.FAILURE);
        }
        return responseDto;
    }

    public RemoveMemberResponseDto removeMember(RemoveMemberRequestDto requestDto) {
        RemoveMemberResponseDto responseDto = new RemoveMemberResponseDto();
        try {
            groupService.removeMember(requestDto.getGroupId(), requestDto.getAdminId(), requestDto.getMemberId());
            responseDto.setResponseStatus(ResponseStatus.SUCCESS);
        } catch (Exception e) {
            responseDto.setResponseStatus(ResponseStatus.FAILURE);
        }
        return responseDto;
    }

    public FetchMembersResponseDto fetchMembers(FetchMembersRequestDto requestDto) {
        FetchMembersResponseDto responseDto = new FetchMembersResponseDto();
        try {
            responseDto.setMembers(groupService.fetchAllMembers(requestDto.getGroupId(), requestDto.getMemberId()));
            responseDto.setResponseStatus(ResponseStatus.SUCCESS);
        } catch (Exception e) {
            responseDto.setResponseStatus(ResponseStatus.FAILURE);
        }
        return responseDto;
    }
}
