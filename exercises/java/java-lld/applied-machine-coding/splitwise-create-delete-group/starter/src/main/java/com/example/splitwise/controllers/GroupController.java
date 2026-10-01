package com.example.splitwise.controllers;

import com.example.splitwise.dtos.CreateGroupRequestDto;
import com.example.splitwise.dtos.CreateGroupResponseDto;
import com.example.splitwise.dtos.DeleteGroupRequestDto;
import com.example.splitwise.dtos.DeleteGroupResponseDto;
import com.example.splitwise.dtos.ResponseStatus;
import com.example.splitwise.services.GroupService;

public class GroupController {
    private final GroupService groupService;

    public GroupController(GroupService groupService) {
        this.groupService = groupService;
    }

    public CreateGroupResponseDto createGroup(CreateGroupRequestDto requestDto) {
        CreateGroupResponseDto responseDto = new CreateGroupResponseDto();
        try {
            responseDto.setGroup(groupService.createGroup(requestDto.getName(), requestDto.getDescription(), requestDto.getCreatorUserId()));
            responseDto.setResponseStatus(ResponseStatus.SUCCESS);
        } catch (Exception e) {
            responseDto.setResponseStatus(ResponseStatus.FAILURE);
        }
        return responseDto;
    }

    public DeleteGroupResponseDto deleteGroup(DeleteGroupRequestDto requestDto) {
        DeleteGroupResponseDto responseDto = new DeleteGroupResponseDto();
        try {
            groupService.deleteGroup(requestDto.getGroupId(), requestDto.getUserId());
            responseDto.setResponseStatus(ResponseStatus.SUCCESS);
        } catch (Exception e) {
            responseDto.setResponseStatus(ResponseStatus.FAILURE);
        }
        return responseDto;
    }
}
